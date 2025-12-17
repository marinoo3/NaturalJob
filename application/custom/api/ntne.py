from datetime import date
from typing import Generator, Any

from .base_api import BaseAPI
from ..utils.parser import ParseHTML, XPathSearch, ParseNumeric
from ..db.offer.models import Offer, Description, Company, City, Region




class NTNE(BaseAPI):

    base_url = "https://nostalentsnosemplois.auvergnerhonealpes.fr/api"
    endpoints = {
        'search': '/joboffers/search'
    }
    headers = {
        "Accept": "application/json,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://nostalentsnosemplois.auvergnerhonealpes.fr/",
    }

    def __init__(self, keyword="data"):
        super().__init__(self.base_url, keyword=keyword, headers=self.headers, cffi=True)

    def __parse_date(self, result:dict) -> date|None:
        # Parse date
        date_str = XPathSearch(result, 'publicationDate')
        if not date_str:
            return None
        # Convert to iso date
        return date.fromisoformat(date_str[:10])

    
    def __parse_salary(self, result:dict, source='label') -> float|None:
        # Parse and return salary label
        if source == 'label':
            label = XPathSearch(result, 'labels', 'salary', 'value')
            if label.lower() == 'salaire selon profil':
                return None
            return label
        
        _match = {
            'min': 'from',
            'max': 'to'
        }
        # Raise exeption if unexpected `source` value
        key = _match.get(source)
        if not key:
            raise ValueError("Unexpected `source` value, should be in ('label', 'min', 'max)")
        # Parse salary and return if None
        salary = XPathSearch(result, 'salary', key)
        if not salary:
            return None
        # Convert to annual period
        period = XPathSearch(result, 'salary', 'period')
        match period:
            case 'MONTH':
                salary = salary * 12
            case 'HOUR':
                salary = salary * 35 * 52

        return salary
    
    def __parse_experience(self, result:dict) -> int|None:
        label = XPathSearch(result, 'labels', 'experienceLevelList', [0], 'value', warning=False)
        if not label:
            return None
        numbers = ParseNumeric(label)
        return min(numbers)

    def __create_offer(self, result:dict) -> Offer:
        description = Description(
            offer_description = ParseHTML(XPathSearch(result, 'description')),
            profile_description = ParseHTML(XPathSearch(result, 'profileDescription')),
        )
        company = Company(
            name = XPathSearch(result, 'company', 'name'),
            description = ParseHTML(XPathSearch(result, 'companyDescription')),
            industry = XPathSearch(result, 'company', 'industryField', 'value')
        )
        region = Region(
            code = XPathSearch(result, 'locations', [0], 'admin2Code'),
            name = XPathSearch(result, 'locations', [0], 'admin2Label')
        )
        city = City(
            name = XPathSearch(result, 'locations', [0], 'admin3Label'),
            region = region
        )

        degrees = []
        degrees_list = XPathSearch(result, 'labels', 'degreeList')
        if degrees_list is not None:
            for degree_element in degrees_list:
                degree = XPathSearch(degree_element, 'value')
                if degree:
                    degrees.append(degree)

        skills = []
        skills_list = XPathSearch(result, 'labels', 'specializationList')
        if skills_list is not None:
            for skill_element in skills_list:
                skill = XPathSearch(skill_element, 'value')
                if skill:
                    skills.append(skill)

        return Offer(
            title = XPathSearch(result, 'title'),
            job_name = XPathSearch(result, 'mainJob', 'label', warning=False) or XPathSearch(result, 'unknownJob'),
            job_type = XPathSearch(result, 'jobType', [0]),
            contract_type = XPathSearch(result, 'contractTypes', [0]),
            salary_label = self.__parse_salary(result, source='label'),
            salary_min = self.__parse_salary(result, source='min'),
            salary_max = self.__parse_salary(result, source='max'),
            min_experience = self.__parse_experience(result),
            latitude = XPathSearch(result, 'locations', [0], 'lat'),
            longitude = XPathSearch(result, 'locations', [0], 'lon'),
            date = (d := self.__parse_date(result)) and d.isoformat(),
            source = 'NTNE',
            description = description,
            company = company,
            city = city,
            skills=skills,
            degrees=degrees
        )

    def _iter_recent(self, url: str, params: dict, stop_date: date | None) -> Generator[Offer, Any, None]:
        while True:
            content = self._safe_requests(url, method='GET', params=params)
            if not content['content']:
                return

            for result in content['content']:
                publish_date = self.__parse_date(result)
                if stop_date and publish_date <= stop_date:
                    return
                yield self.__create_offer(result)

            params['page'] += 1

    def iter_search(self, stop_date: date | None = None) -> Generator[Offer, Any, None]:
        url = self.base_url + self.endpoints['search']
        params = {
            'serjobsearch': True,
            'scoringVersion': 'SERJOBSEARCH',
            'sorting': 'DATE',
            'expandLocations': True,
            'facet': ["cities", "date", "company", "industry", "contract", "job", "macroJob", "jobType", "content_language", "license", "degree", "experienceLevel"],
            'page': 1,
            'limit': 20,
            'what': self.keyword,
        }
        yield from self._iter_recent(url, params, stop_date)

    def get_total(self) -> int|None:
        """Get total of result on API

        Returns:
            int|None: Total result
        """

        url = self.base_url + self.endpoints['search']
        params = {
            'serjobsearch': True,
            'scoringVersion': 'SERJOBSEARCH',
            'sorting': 'DATE',
            'expandLocations': True,
            'facet': ["cities", "date", "company", "industry", "contract", "job", "macroJob", "jobType", "content_language", "license", "degree", "experienceLevel"],
            'page': 1,
            'limit': 0,
            'what': self.keyword,
        }
        result = self._safe_requests(url, method='GET', params=params)
        if not result:
            return None
        return result.get('total')