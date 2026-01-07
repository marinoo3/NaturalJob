import re
from typing import List
from cv.preprocess import clean_text
from .schemas import CVStruct


SECTION_HINTS = {
    "experiences": ["expérience", "experience", "professionnel", "stage", "emploi"],
    "education": ["formation", "éducation", "education", "diplôme", "université", "cnam"],
    "projects": ["projet", "projects", "réalisation", "realisation"],
    "skills": ["compétence", "competence", "skills", "stack", "technologies", "outils"]
}


def _extract_lines(text: str) -> List[str]:
    lines = [l.strip() for l in text.splitlines()]
    return [l for l in lines if l]


def _extract_achievements(lines: List[str]) -> List[str]:
    """
    Récupère les lignes contenant chiffres/%, durées, etc. (preuves chiffrées).
    """
    out = []
    pattern = re.compile(r"(\d+(\.\d+)?\s?%|\b\d+\b|\b\d+\s?(mois|ans|semaines|jours)\b)", re.IGNORECASE)
    for l in lines:
        if pattern.search(l):
            out.append(l)
    return out[:15]


def _guess_sections(lines: List[str]) -> dict:
    """
    Heuristique: on regroupe les lignes après un titre de section probable.
    V1 simple mais explicable.
    """
    buckets = {k: [] for k in SECTION_HINTS.keys()}
    current = None

    for l in lines:
        low = l.lower()

        found = None
        for sec, hints in SECTION_HINTS.items():
            # petit filtre: un titre de section est souvent court
            if any(h in low for h in hints) and len(low) <= 40:
                found = sec
                break

        if found:
            current = found
            continue

        if current:
            buckets[current].append(l)

    return buckets


def _extract_skills_from_vocab(clean_cv_text: str, skill_vocab: List[str]) -> List[str]:
    """
    Extrait les skills du CV en cherchant un vocabulaire donné (skill_vocab),
    en travaillant sur la version nettoyée.
    """
    cv_tokens = set(clean_cv_text.split())
    found = []
    seen = set()

    for sk in skill_vocab:
        sk_clean = clean_text(sk)
        if not sk_clean:
            continue

        parts = sk_clean.split()
        if len(parts) == 1:
            ok = parts[0] in cv_tokens
        else:
            ok = sk_clean in clean_cv_text

        if ok:
            key = sk.lower()
            if key not in seen:
                seen.add(key)
                found.append(sk)

    return found


def build_cv_struct(cv_name: str, raw_text: str, skill_vocab: List[str]) -> CVStruct:
    clean_cv = clean_text(raw_text)
    lines = _extract_lines(raw_text)

    sections = _guess_sections(lines)

    achievements = _extract_achievements(lines)
    skills = _extract_skills_from_vocab(clean_cv, skill_vocab=skill_vocab)

    # fallback: si aucune section détectée, on prend des chunks du début
    experiences = sections["experiences"][:30] if sections["experiences"] else lines[:30]
    education = sections["education"][:20] if sections["education"] else []
    projects = sections["projects"][:20] if sections["projects"] else []

    return CVStruct(
        cv_name=cv_name,
        raw_text=raw_text,
        clean_text=clean_cv,
        skills=skills,
        experiences=experiences,
        education=education,
        projects=projects,
        achievements=achievements
    )
