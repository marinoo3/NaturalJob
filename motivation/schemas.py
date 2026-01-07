from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class CVStruct:
    cv_name: str
    raw_text: str
    clean_text: str
    skills: List[str]
    experiences: List[str]      # V1: chunks (heuristique)
    education: List[str]
    projects: List[str]
    achievements: List[str]     # lignes avec chiffres / résultats


@dataclass
class JobStruct:
    offer_id: int
    title: str
    description: str
    skills: List[str]           # depuis colonne skills si dispo
    clean_document: str


@dataclass
class Evidence:
    skill: str
    proof: str                  # phrase/ligne du CV qui justifie


@dataclass
class MatchStruct:
    cv_name: str
    offer_id: int
    title: str
    common_skills: List[str]
    missing_skills: List[str]
    evidences: List[Evidence]
    match_score: int            # 0–100
    keywords_used: List[str]    # pour ATS


def to_json_dict(obj) -> Dict[str, Any]:
    """
    Convertit une dataclass (et ses sous-dataclasses) en dict JSON sérialisable.
    """
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    raise TypeError("to_json_dict attend une dataclass.")
