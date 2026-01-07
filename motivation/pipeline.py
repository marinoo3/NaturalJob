import json
from pathlib import Path

from cv.parser import load_all_cvs
from nlp.vectorizer import load_and_prepare_offers

from .job_structurer import build_job_struct
from .cv_structurer import build_cv_struct
from .matcher import build_skill_vocab_from_offers, match_cv_to_job
from .schemas import to_json_dict


def build_facts_for_one_offer(
    cv_dir: Path,
    offers_csv: Path,
    offer_id: int,
    out_dir: Path
):
    """
    Génère un fichier JSON factuel (sans LLM) par CV pour une offre donnée.
    Output: data/outputs_motivation/<CV>__offer_<id>__facts.json
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Charger + préparer les offres (inclut clean_document)
    df_offers = load_and_prepare_offers(offers_csv)

    # 2) Structurer l'offre choisie
    job = build_job_struct(df_offers, offer_id)

    # 3) Construire un vocab skills global (si la colonne skills est exploitable)
    skill_vocab = build_skill_vocab_from_offers(df_offers)

    # 4) Fallback: si skills vides, on utilise au moins le titre comme vocab
    # (sinon extraction skills CV = toujours vide)
    if not skill_vocab:
        skill_vocab = []

    if job.title:
        for w in job.title.split():
            if w not in skill_vocab:
                skill_vocab.append(w)

    # 5) Charger tous les CV et produire les facts
    cvs = load_all_cvs(cv_dir)
    saved_paths = []

    for cv_name, raw_cv in cvs.items():
        cv_struct = build_cv_struct(cv_name, raw_cv, skill_vocab=skill_vocab)
        match = match_cv_to_job(cv_struct, job)

        payload = {
            "cv": to_json_dict(cv_struct),
            "job": to_json_dict(job),
            "match": to_json_dict(match),
        }

        out_path = out_dir / f"{cv_name}__offer_{offer_id}__facts.json"
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        saved_paths.append(str(out_path))

    return saved_paths


if __name__ == "__main__":
    # valeurs par défaut (tu peux changer offer_id)
    saved = build_facts_for_one_offer(
        cv_dir=Path("data/cv"),
        offers_csv=Path("data/offer.csv"),
        offer_id=0,
        out_dir=Path("data/outputs_motivation")
    )

    print("Saved JSON files:")
    for p in saved:
        print("-", p)
