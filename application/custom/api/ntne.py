from datetime import date

from .base_api import BaseAPI
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

    def __create_offer(self, result:dict) -> Offer:
        description = Description(
            offer_description = self._get_key(result, ['description']),
            profile_description = self._get_key(result, ['profileDescription']),
        )
        company = Company(
            name = self._get_key(result, ['company', 'name']),
            description = self._get_key(result, ['companyDescription']),
            industry = self._get_key(result, ['company', 'industryField', 'value'])
        )
        region = Region(
            code = self._get_key(result, ['locations', [0], 'admin2Code']),
            name = self._get_key(result, ['locations', [0], 'admin2Label'])
        )
        city = City(
            name = self._get_key(result, ['locations', [0], 'admin3Label']),
            region = region
        )
        return Offer(
            title = self._get_key(result, ['title']),
            job_name = self._get_key(result, ['mainJob', 'label'], fallback=['unknownJob']),
            job_type = self._get_key(result, ['jobType', [0]]),
            contract_type = self._get_key(result, ['contractTypes', [0]]),
            salary = self._get_key(result, ['labels', 'salary', 'value']),
            min_experience = self._get_key(result, ['labels', 'experienceLevelList', [0], 'value']),
            latitude = self._get_key(result, ['locations', [0], 'lat']),
            longitude = self._get_key(result, ['locations', [0], 'lon']),
            date = date.fromisoformat(result['publicationDate'][:10]).isoformat(),
            source = 'NTNE',
            description = description,
            company = company,
            city = city
        )

    def _loop_recent(self, url:str, params:dict, stop_date:date|None) -> list[Offer]:
        jobs = []
        while True:
            # Request content and skip if empty (reached end)
            content = self._safe_requests(url, method='GET', params=params)
            if len(content['content']) == 0:
                break
            # Check if stop date reached
            for result in content['content']:
                publish_date = date.fromisoformat(result['publicationDate'][:10])
                if stop_date and publish_date <= stop_date:
                    return jobs
                offer = self.__create_offer(result)
                jobs.append(offer)
            # Next page
            params['page'] += 1

        return jobs

    def search(self, stop_date:date=None) -> list[Offer]:
        """Loop search on NTNE job API from most recent to a specific date

        Args:
            stop_date (date): The date to stop the search. Parse all jobs if `None`.

        Return
            (list[dict]): The concatened json response
        """

        url = self.base_url + self.endpoints['search']
        params = {
            'serjobsearch': True,
            'scoringVersion': "SERJOBSEARCH",
            'sorting': "DATE",
            'expandLocations': True,
            'facet': ["cities", "date", "company", "industry", "contract", "job", "macroJob", "jobType", "content_language", "license", "degree", "experienceLevel"],
            'page': 1,
            'limit': 20,
            'what': self.keyword
        }

        jobs = self._loop_recent(url, params, stop_date)
        return jobs