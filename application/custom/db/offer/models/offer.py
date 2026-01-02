from dataclasses import dataclass, field, asdict
from typing import Optional, List
from flask import render_template, url_for
from datetime import date



@dataclass
class Company:
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None

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
class Cluster:
    id: int
    main_tokens: str = None
    name: str = None

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
    cluster: Optional[Cluster] = None
    degrees: List[str] = field(default_factory=list)  # degree names
    skills: List[str] = field(default_factory=list)   # skill names

    dict = asdict

    def convert_date(self, target_format:str) -> str:
        date_obj = date.fromisoformat(self.date)
        return date_obj.strftime(target_format)
    
    def truncate_description(self, limit:int) -> str:
        description = self.description.offer_description
        if len(description) <= limit:
            return description
        return description[:limit-3] + '...'
    
    def company_url(self) -> str:
        if self.company.logo_url:
            return self.company.logo_url
        return 'hello'
    
    def format_score(self, score:float) -> int:
        if score is None:
            return None
        return round((1-score) * 100)

    def render(self, id:int, score:float=None, style='result') -> str:
        """Create html template object

        Args:
            id (int): The offer id
            style (str): The type of template to render: 'preview', 'result', 'fullview'. Defaults to 'result'.

        Returns:
            str: The html object
        """

        match style:
            case 'preview':
                return None
            case 'result':
                return render_template(
                    'elements/offer_result.html', 
                    offer_id=id, 
                    title=self.title,
                    description=self.truncate_description(225),
                    company_name=self.company.name,
                    company_logo=self.company.logo_url or url_for('static', filename='images/company.svg'),
                    date=self.convert_date('%d %B %Y'),
                    tags=[],
                    score=self.format_score(score)
                    )
            case 'fullview':
                return None
            case _:
                raise ValueError("Wrong `style` value, expected 'preview', 'result' or 'fullview'")