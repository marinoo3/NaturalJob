from .base_api import BaseAPI

from datetime import date




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

    def _loop_recent(self, url:str, params:dict, stop_date:date|None) -> list[dict]:
        jobs = []
        while True:
            # Request content and skip if empty (reached end)
            content = self.safe_requests(url, method='GET')
            if len(content['content']) == 0:
                break
            # Check if stop date reached and break if so
            for result in content['content']:
                publish_date = date.fromisoformat(result['publicationDate'][:10])
                if publish_date <= stop_date:
                    break
                jobs.append(result)
            # Next page
            params['page'] += 1

        return jobs

    def search(self, stop_date:date=None) -> list[dict]:
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
            'sorting': "SCORING",
            'expandLocations': True,
            'facet': ["cities", "date", "company", "industry", "contract", "job", "macroJob", "jobType", "content_language", "license", "degree", "experienceLevel"],
            'page': 1,
            'limit': 20,
            'what': self.keyword
        }

        jobs = self._loop_recent(url, params, stop_date)
        return jobs