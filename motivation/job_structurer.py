from typing import List
import re
import pandas as pd
from cv.preprocess import clean_text
from .schemas import JobStruct


def _split_skills_field(skills_value: str) -> List[str]:
    """
    Sépare une colonne 'skills' (si elle existe) en liste de compétences.
    Supporte séparateurs: virgule, point-virgule, slash, pipe, saut de ligne.
    """
    if not isinstance(skills_value, str):
        return []
    s = skills_value.strip()
    if not s:
        return []

    parts = re.split(r"[,\n;/|]+", s)
    skills = []
    for p in parts:
        p = p.strip()
        if p:
            skills.append(p)

    # dédoublonnage en gardant l'ordre
    seen = set()
    out = []
    for sk in skills:
        low = sk.lower()
        if low not in seen:
            seen.add(low)
            out.append(sk)
    return out


def build_job_struct(df_offers: pd.DataFrame, offer_id: int) -> JobStruct:
    """
    Construit une JobStruct à partir du DataFrame des offres
    (chargé via nlp.vectorizer.load_and_prepare_offers).
    """
    row = df_offers.iloc[offer_id]

    title = str(row["title"]) if "title" in df_offers.columns else ""
    description = str(row["description"]) if "description" in df_offers.columns else ""
    skills_raw = str(row["skills"]) if "skills" in df_offers.columns else ""

    skills_list = _split_skills_field(skills_raw)

    clean_doc = str(row["clean_document"]) if "clean_document" in df_offers.columns else clean_text(
        f"{title} {description} {skills_raw}"
    )

    return JobStruct(
        offer_id=offer_id,
        title=title,
        description=description,
        skills=skills_list,
        clean_document=clean_doc
    )
