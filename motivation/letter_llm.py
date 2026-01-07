import json
import re
from pathlib import Path
from typing import Dict, Any, List


SYSTEM_RULES = """
Tu écris une lettre de motivation basée UNIQUEMENT sur des faits fournis.
INTERDICTION d'inventer des expériences, entreprises, technologies, chiffres ou diplômes.

Tu as accès uniquement à:
- infos du CV structuré
- infos de l'annonce structurée
- matching factuel
- réponses utilisateur

Si une info est manquante:
- ne l'invente pas
- reformule de façon neutre ("Je souhaite approfondir...", "Je suis motivé(e) à développer...")

Sortie STRICT (JSON uniquement) :
{
  "subject_line": "...",
  "letter": "...",
  "bullets_strengths": ["...", "..."],
  "keywords_used": ["...", "..."]
}

Contraintes:
- letter = 180 à 300 mots (par défaut)
- Structure: Accroche -> Match -> Preuves -> Motivation -> Conclusion + dispo
- Style: professionnel, naturel, sans exagération.
"""


def build_letter_prompt(
    facts: Dict[str, Any],
    user_answers: Dict[str, str],
    variant: str = "classique",
    target_words: int = 230
) -> str:
    """
    variant: 'classique' | 'resultats' | 'concise'
    user_answers: réponses aux 3 questions (ex: {"a1": "...", "a2": "...", "a3": "..."})
    """
    cv = facts["cv"]
    job = facts["job"]
    match = facts["match"]

    payload = {
        "variant": variant,
        "target_words": target_words,
        "cv_name": cv.get("cv_name", ""),
        "cv_skills": cv.get("skills", [])[:40],
        "cv_experiences": cv.get("experiences", [])[:20],
        "cv_projects": cv.get("projects", [])[:15],
        "cv_achievements": cv.get("achievements", [])[:10],
        "job_title": job.get("title", ""),
        "job_description": job.get("description", "")[:1200],
        "job_skills": job.get("skills", [])[:40],
        "common_skills": match.get("common_skills", [])[:40],
        "missing_skills": match.get("missing_skills", [])[:20],
        "evidences": match.get("evidences", [])[:3],
        "match_score": match.get("match_score", 0),
        "user_answers": user_answers,
    }

    return (
        SYSTEM_RULES.strip()
        + "\n\nDONNÉES (JSON):\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nGénère uniquement le JSON de sortie."
    )


# -----------------------------
# Validation anti-hallucination
# -----------------------------

def _normalize_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def build_allowed_keywords(facts: Dict[str, Any], user_answers: Dict[str, str]) -> List[str]:
    """
    Liste blanche de mots/expressions autorisés (keywords) :
    - skills CV
    - skills annonce
    - mots du titre
    - réponses user
    """
    allowed = set()

    cv_sk = facts["cv"].get("skills", []) or []
    job_sk = facts["job"].get("skills", []) or []
    title = facts["job"].get("title", "") or ""

    for x in cv_sk + job_sk + title.split():
        nx = _normalize_text(str(x))
        if nx:
            allowed.add(nx)

    for ans in user_answers.values():
        nx = _normalize_text(str(ans))
        if nx:
            # on garde des tokens importants (pas tous les mots)
            for tok in nx.split():
                if len(tok) >= 3:
                    allowed.add(tok)

    return list(allowed)


def validate_letter_json(obj: Dict[str, Any]) -> None:
    required = ["subject_line", "letter", "bullets_strengths", "keywords_used"]
    for k in required:
        if k not in obj:
            raise ValueError(f"Champ manquant: {k}")

    if not isinstance(obj["subject_line"], str) or len(obj["subject_line"].strip()) < 5:
        raise ValueError("subject_line invalide.")
    if not isinstance(obj["letter"], str) or len(obj["letter"].strip()) < 50:
        raise ValueError("letter invalide.")
    if not isinstance(obj["bullets_strengths"], list):
        raise ValueError("bullets_strengths doit être une liste.")
    if not isinstance(obj["keywords_used"], list):
        raise ValueError("keywords_used doit être une liste.")


def check_no_new_keywords(letter_text: str, allowed_keywords: List[str]) -> None:
    """
    Contrôle léger mais utile :
    - On vérifie que les 'keywords_used' ne sortent pas de la whitelist.
    - Et on peut vérifier quelques patterns suspects.
    """
    # Ici on ne fait PAS une détection parfaite (trop coûteux),
    # mais on empêche le modèle de "sortir" des keywords inventés.
    # Le contrôle fort se fait sur keywords_used.
    pass


def run_letter_from_facts_file(
    facts_json_path: Path,
    user_answers: Dict[str, str],
    llm_generate_fn,
    variant: str = "classique",
    target_words: int = 230
) -> Dict[str, Any]:
    """
    facts_json_path: chemin vers *__facts.json
    user_answers: réponses aux questions
    llm_generate_fn: fonction(prompt)->str (sortie du modèle)
    """
    facts = json.loads(facts_json_path.read_text(encoding="utf-8"))
    prompt = build_letter_prompt(facts, user_answers=user_answers, variant=variant, target_words=target_words)

    raw = llm_generate_fn(prompt)
    obj = json.loads(raw)
    validate_letter_json(obj)

    # Validation keywords_used: ils doivent venir de la whitelist
    allowed = set(build_allowed_keywords(facts, user_answers))
    used = [_normalize_text(x) for x in obj.get("keywords_used", [])]
    used = [u for u in used if u]

    bad = [u for u in used if u not in allowed]
    if bad:
        raise ValueError(f"Keywords non autorisés détectés (potentielle hallucination): {bad[:10]}")

    return obj
