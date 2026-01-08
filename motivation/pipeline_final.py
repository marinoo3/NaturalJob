import json
from pathlib import Path
from typing import Dict, Any, Optional

from cv.parser import load_all_cvs
from nlp.vectorizer import load_and_prepare_offers

from motivation.job_structurer import build_job_struct
from motivation.cv_structurer import build_cv_struct
from motivation.matcher import build_skill_vocab_from_offers, match_cv_to_job
from motivation.schemas import to_json_dict

from motivation.llm_client import MistralLLMClient, parse_json_text
from motivation.questions_llm import build_questions_prompt, validate_questions_json
from motivation.letter_llm import (
    build_letter_prompt,
    validate_letter_json,
    build_allowed_keywords,
    _normalize_text,
)
from motivation.post_edit import make_variants, make_ats_friendly


def save_json(path: Path, obj: Dict[str, Any]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def run_for_offer(
    offer_id: int,
    cv_dir: Path = Path("data/cv"),
    offers_csv: Path = Path("data/offer.csv"),
    out_dir: Path = Path("data/outputs_motivation"),
    model: str = "mistral-large-latest",
    variant: str = "classique",
    target_words: int = 230,
    user_answers: Optional[Dict[str, str]] = None,
):
    """
    Pipeline final (avec LLM) pour une offre.
    - Génère facts JSON
    - Génère 3 questions (JSON)
    - Génère lettre (JSON)
    - Post-edit + variantes + ATS-friendly
    """
    user_answers = user_answers or {
        "a1": "Poste visé et motivation principale : (à compléter)",
        "a2": "Une réalisation chiffrée liée à l'offre : (à compléter)",
        "a3": "Ton et longueur souhaités : (à compléter)",
    }

    client = MistralLLMClient(model=model)

    # 1) Offres + offre cible
    df_offers = load_and_prepare_offers(offers_csv)
    job = build_job_struct(df_offers, offer_id)

    # 2) vocab skills (si skills vide -> fallback titre)
    skill_vocab = build_skill_vocab_from_offers(df_offers)
    if job.title:
        for w in job.title.split():
            if w not in skill_vocab:
                skill_vocab.append(w)

    # 3) CVs
    cvs = load_all_cvs(cv_dir)

    # 4) outputs dirs
    facts_dir = out_dir / "facts"
    letters_dir = out_dir / "letters"
    facts_dir.mkdir(parents=True, exist_ok=True)
    letters_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for cv_name, raw_cv in cvs.items():
        # --- A) FACTS
        cv_struct = build_cv_struct(cv_name, raw_cv, skill_vocab=skill_vocab)
        match = match_cv_to_job(cv_struct, job)

        facts_payload = {
            "cv": to_json_dict(cv_struct),
            "job": to_json_dict(job),
            "match": to_json_dict(match),
        }

        facts_path = facts_dir / f"{cv_name}__offer_{offer_id}__facts.json"
        save_json(facts_path, facts_payload)

        # --- B) QUESTIONS (LLM)
        q_prompt = build_questions_prompt(facts_payload)
        q_raw = client.generate(q_prompt, temperature=0.2, max_tokens=600)
        (letters_dir / f"{cv_name}__offer_{offer_id}__questions_raw.txt").write_text(q_raw, encoding="utf-8")

        q_obj = parse_json_text(q_raw)
        validate_questions_json(q_obj)

        q_path = letters_dir / f"{cv_name}__offer_{offer_id}__questions.json"
        save_json(q_path, q_obj)

        # --- C) LETTRE (LLM)
        l_prompt = build_letter_prompt(
            facts_payload,
            user_answers=user_answers,
            variant=variant,
            target_words=target_words,
        )

        raw_letter = client.generate(l_prompt, temperature=0.2, max_tokens=1000)
        (letters_dir / f"{cv_name}__offer_{offer_id}__letter_raw.txt").write_text(raw_letter, encoding="utf-8")

        letter_obj = parse_json_text(raw_letter)
        validate_letter_json(letter_obj)

        # --- Anti-hallucination: keywords_used dans une whitelist
        allowed = set(build_allowed_keywords(facts_payload, user_answers))
        used = [_normalize_text(x) for x in (letter_obj.get("keywords_used") or [])]
        used = [u for u in used if u]

        bad = [u for u in used if u not in allowed]
        if bad:
            raise ValueError(f"[{cv_name}] Keywords non autorisés (hallucination possible): {bad[:10]}")

        # --- D) POST-EDIT
        enriched = make_variants(letter_obj)

        enriched["ats_friendly"] = make_ats_friendly(
            enriched["variants"]["classique"],
            letter_obj.get("keywords_used", []),
        )

        out_letter_path = letters_dir / f"{cv_name}__offer_{offer_id}__letter.json"
        save_json(out_letter_path, enriched)

        results.append({
            "cv": cv_name,
            "facts": str(facts_path),
            "questions": str(q_path),
            "letter": str(out_letter_path),
            "score": facts_payload["match"]["match_score"],
        })

    # résumé
    summary_path = out_dir / f"summary_offer_{offer_id}.json"
    save_json(summary_path, {"offer_id": offer_id, "results": results})

    return summary_path


if __name__ == "__main__":
    summary = run_for_offer(offer_id=0)
    print("Saved summary:", summary)
