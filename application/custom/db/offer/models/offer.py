from dataclasses import dataclass, field, asdict
from typing import Optional, List

@dataclass
class Company:
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None

@dataclass
class Region:
    code: str
    name: str

@dataclass
class City:
    name: str
    region: Region

@dataclass
class Description:
    offer_description: str
    profile_description: Optional[str] = None

@dataclass
class Offer:
    title: str
    job_name: str
    job_type: Optional[str]
    contract_type: Optional[str]
    salary_label: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    min_experience: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    date: str                    # store ISO-8601 string, e.g., “2024-05-01”
    source: str                  # to trace origin of the offer
    description: Description
    company: Company
    city: City
    degrees: List[str] = field(default_factory=list)  # degree names
    skills: List[str] = field(default_factory=list)   # skill names

    dict = asdict