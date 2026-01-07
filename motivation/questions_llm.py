import json
from pathlib import Path
from typing import Dict, Any


SYSTEM_RULES = """
Tu es un assistant qui prépare une lettre de motivation SANS inventer.
Tu dois produire EXACTEMENT 3 questions utiles et actionnables.
Règles:
- 1 question = 1 information nécessaire pour écrire une bonne lettre.
- Pas de questions vagues.
- Ne demande pas des infos déjà présentes dans les données.
- Si une info manque, tu la demandes.
Format de sortie STRICT (JSON uniquement):
{
  "q1": "...",
  "q2": "...",
  "q3": "...",
  "why_each": {
    "q1": "...",
    "q2": "...",
    "q3": "..."
  }
}
"""


def build_questions_prompt(facts: Dict[str, Any]) -> str:
    cv = facts["cv"]
    job = facts["job"]
    match = facts["match"]

    # On fournit un résumé compact pour guider le modèle (et limiter le bruit)
    payload = {
        "cv_name": cv.get("cv_name", ""),
        "cv_skills": cv.get("skills", [])[:30],
        "cv_achievements": cv.get("achievements", [])[:10],
        "job_title": job.get("title", ""),
        "job_skills": job.get("skills", [])[:30],
        "common_skills": match.get("common_skills", [])[:30],
        "missing_skills": match.get("missing_skills", [])[:15],
        "evidences": match.get("evidences", [])[:3],
        "match_score": match.get("match_score", 0),
    }

    return (
        SYSTEM_RULES.strip()
        + "\n\nDONNÉES (JSON):\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\nGénère uniquement le JSON de sortie."
    )


def validate_questions_json(obj: Dict[str, Any]) -> None:
    # Validation minimale et stricte
    required = ["q1", "q2", "q3", "why_each"]
    for k in required:
        if k not in obj:
            raise ValueError(f"Champ manquant: {k}")

    if not isinstance(obj["why_each"], dict):
        raise ValueError("why_each doit être un objet JSON.")

    for qk in ["q1", "q2", "q3"]:
        if not isinstance(obj[qk], str) or len(obj[qk].strip()) < 5:
            raise ValueError(f"{qk} invalide.")
        if qk not in obj["why_each"]:
            raise ValueError(f"why_each.{qk} manquant.")
        if not isinstance(obj["why_each"][qk], str) or len(obj["why_each"][qk].strip()) < 5:
            raise ValueError(f"why_each.{qk} invalide.")


# ---- Utilisation (branché plus tard à ton LLM) ----
# Ici on ne force pas un SDK particulier.
# Tu injecteras prompt -> modèle -> texte -> json.loads -> validate
def run_questions_from_facts_file(facts_json_path: Path, llm_generate_fn) -> Dict[str, Any]:
    """
    facts_json_path: chemin vers le *__facts.json
    llm_generate_fn: fonction qui prend (prompt:str) et renvoie (str) = sortie du modèle
    """
    facts = json.loads(facts_json_path.read_text(encoding="utf-8"))
    prompt = build_questions_prompt(facts)

    raw = llm_generate_fn(prompt)
    obj = json.loads(raw)
    validate_questions_json(obj)
    return obj
