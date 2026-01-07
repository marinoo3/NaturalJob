from typing import List
from .schemas import MatchStruct, Evidence


def build_skill_vocab_from_offers(df_offers) -> List[str]:
    """
    Construit un vocabulaire de compétences à partir de la colonne 'skills' si elle existe.
    Si la colonne est vide/non remplie, retourne [] (ce n'est pas bloquant).
    """
    if "skills" not in df_offers.columns:
        return []

    vocab = []
    for v in df_offers["skills"].fillna("").astype(str).tolist():
        # support séparateurs divers
        v = v.replace("|", ",").replace(";", ",")
        for part in v.split(","):
            sk = part.strip()
            if sk:
                vocab.append(sk)

    # dédoublonnage en gardant l'ordre
    seen = set()
    out = []
    for sk in vocab:
        low = sk.lower()
        if low not in seen:
            seen.add(low)
            out.append(sk)
    return out


def _evidence_from_cv(raw_cv: str, skills: List[str], max_evidences: int = 3) -> List[Evidence]:
    """
    Cherche des lignes du CV qui prouvent les skills (zéro hallucination).
    V1: on fait simple: on scanne les lignes et on prend la première occurrence par skill.
    """
    lines = [l.strip() for l in raw_cv.splitlines() if l.strip()]
    evidences: List[Evidence] = []

    for sk in skills:
        sk_low = sk.lower()
        for l in lines:
            if sk_low in l.lower():
                evidences.append(Evidence(skill=sk, proof=l))
                break
        if len(evidences) >= max_evidences:
            break

    return evidences


def score_match(job_skills: List[str], common: List[str]) -> int:
    """
    Score simple, défendable dans un rapport :
    - si pas de job_skills -> fallback basé sur nb de common
    - sinon -> couverture des skills de l'offre
    """
    if not job_skills:
        return min(60, 20 + 10 * len(common))  # borne propre

    cov = len(common) / max(1, len(job_skills))
    return int(round(100 * cov))


def match_cv_to_job(cv_struct, job_struct) -> MatchStruct:
    """
    Entrées:
    - cv_struct : CVStruct
    - job_struct: JobStruct

    Sortie:
    - MatchStruct (factuel, explicable, sans invention)
    """
    job_skills = job_struct.skills
    cv_skills = cv_struct.skills

    # intersection case-insensitive
    job_map = {s.lower(): s for s in job_skills}
    cv_set = set([s.lower() for s in cv_skills])

    common = [original for low, original in job_map.items() if low in cv_set]
    missing = [s for s in job_skills if s.lower() not in cv_set]

    evidences = _evidence_from_cv(cv_struct.raw_text, common, max_evidences=3)
    score = score_match(job_skills, common)

    keywords_used = []
    if job_struct.title:
        keywords_used += job_struct.title.split()
    keywords_used += job_skills

    return MatchStruct(
        cv_name=cv_struct.cv_name,
        offer_id=job_struct.offer_id,
        title=job_struct.title,
        common_skills=common,
        missing_skills=missing[:15],
        evidences=evidences,
        match_score=score,
        keywords_used=keywords_used[:30]
    )
