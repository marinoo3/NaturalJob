from datetime import date
import json

from .base_api import BaseAPI
from ..utils.parser import XPathSearch, ParseHTML, ParseNumeric
from ..db.offer.models import Offer, Description, Company, City, Region




class APEC(BaseAPI):

    size = 100
    base_url = "https://www.apec.fr/cms/webservices"
    endpoints = {
        'search': '/rechercheOffre',
        'hierarchy': '/referentielstatique/presentations/visuels/liste/hierarchie',
        'offer': '/offre/public'
    }
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Origin': 'https://www.apec.fr'
    }

    def __init__(self, keyword="data") -> None:
        super().__init__(self.base_url, keyword=keyword, headers=self.headers)

    def __parse_date(self, result:dict) -> date|None:
        date_str = XPathSearch(result, 'datePublication')
        if not date_str:
            return None
        return date.fromisoformat(date_str[:10])


    def __parse_region_code(self, result:int) -> int|None:
        postal_code = XPathSearch(result, 'adresseOffre', 'adresseCodePostal', warning=False)
        if not postal_code:
            return None
        return postal_code[:2]
    
    def __parse_industry(self, result:dict, hierarchy:dict) -> str|None:
        industry_id = XPathSearch(result, 'idNomSecteurActivite')
        if not industry_id:
            return None
        industry = XPathSearch(hierarchy, 'NAF_700_SERVICE_DOMAIN', industry_id)
        return industry
    
    def __parse_job_type(self, result:dict) -> str:
        if result.get('idNomDureeTempsPartiel'):
            return 'PART_TIME'
        return 'FULL_TIME'
    
    def __parse_contract_type(self, result:dict, hierarchy:dict) -> str|None:
        contract_id = XPathSearch(result, 'idNomTypeContrat')
        if not contract_id:
            return None
        contract_type = XPathSearch(hierarchy, 'RECHERCHE_OFFRE_TYPE_CONTRAT', contract_id)
        return contract_type
    
    def __parse_salary(self, result:dict, source='label') -> float|None:
        label = XPathSearch(result, 'salaireTexte')
        if label.lower() == 'a négocier':
            return None
        
        if source == 'label':
            return label
        
        keys = {
            'min': 0,
            'max': 1
        }
        index = keys.get(source)
        if index is None:
            raise ValueError("Unexpected `source` value, should be in ('label', 'min', 'max)")
        
        amounts = ParseNumeric(label)
        if len(amounts) >= index+1:
            return amounts[index]
        return None
        
    def __parse_experience(self, result:dict, hierarchy:dict) -> str|None:
        experience_id = XPathSearch(result, 'idNomNiveauExperience')
        if not experience_id:
            return None
        experience = XPathSearch(hierarchy, 'OFFRE_NIVEAU_EXPERIENCE', experience_id)
        year = ParseNumeric(experience)
        if not year:
            return None
        return year[0]


    def __create_offer(self, result:dict, hierarchy:dict) -> Offer:
        description = Description(
            offer_description = ParseHTML(XPathSearch(result, 'texteHtml')),
            profile_description = ParseHTML(XPathSearch(result, 'texteHtmlProfil')),
        )
        company = Company(
            name = XPathSearch(result, 'enseigne'),
            description = ParseHTML(XPathSearch(result, 'texteHtmlEntreprise')),
            industry = self.__parse_industry(result, hierarchy)
        )
        region = Region(
            code = self.__parse_region_code(result),
            name = None
        )
        city = City(
            name = XPathSearch(result, 'adresseOffre', 'adresseVille', warning=False),
            region = region
        )
        return Offer(
            title = XPathSearch(result, 'intitule'),
            job_name = XPathSearch(result, 'intitule'),
            job_type = self.__parse_job_type(result),
            contract_type = self.__parse_contract_type(result, hierarchy),
            salary_label = self.__parse_salary(result, source='label'),
            salary_min = self.__parse_salary(result, source='min'),
            salary_max = self.__parse_salary(result, source='max'),
            min_experience = self.__parse_experience(result, hierarchy),
            latitude = XPathSearch(result, 'latitude'),
            longitude = XPathSearch(result, 'longitude'),
            date = self.__parse_date(result).isoformat(),
            source = 'APEC',
            description = description,
            company = company,
            city = city
        )

    def _loop_recent(self, url:str, payload:dict, stop_date:date|None) -> list[str]:
        job_ids = []
        while True:
            # Request content and skip if empty (reached end)
            content = self._safe_requests(url, method='POST', json=payload)
            if len(content['resultats']) == 0:
                break
            # Check if stop date reached
            for result in content['resultats']:
                publish_date = self.__parse_date(result)
                print(stop_date, publish_date)
                if stop_date and publish_date <= stop_date:
                    return job_ids
                job_ids.append(result['numeroOffre'])
            # Next page
            payload['pagination']['startIndex'] += self.size

        return job_ids
    
    def _collect_hierarchy(self, url, payload) -> dict:
        # Request latest hierarchy json
        content = self._safe_requests(url, method='POST', json=payload)
        # Load from backup if fails
        if not content:
            print('WARNING: Failed to collect APEC hierarchy. Getting it from `data/dist/apec_hierarchy.json`')
            with open('data/dist/apec_hierarchy.json', 'r') as f:
                return json.load(f)
        # Build the key map dict
        key_map = {}
        for element in content:
            category = element['codePresentation']
            key = element['idNomenclature']
            value = element['libelle']
            if not key_map.get(category):
                key_map[category] = {}
            key_map[category][key] = value
        return key_map
    
    def _iter_content(self, url:str, params:dict, job_ids:list[str], hierarchy:dict):
        for id in job_ids:
            params['numeroOffre'] = id
            result = self._safe_requests(url, method='GET', params=params, raise_status=False)
            if not result:
                print(f'WARNING: APEC job {id} not found')
                continue # skip if no response
            yield self.__create_offer(result, hierarchy)

    def iter_search(self, stop_date:date=None):
        """Loop search on APEC job API from most recent to a specific date. First collect recent offer IDs, then request individual content.

        Args:
            stop_date (date): The date to stop the search. Parse all jobs if `None`.

        Return
            (list[dict]): The concatened json response
        """

        # Search recent job IDs
        search_url = self.base_url + self.endpoints['search']
        payload = {
            "lieux": [],
            "fonctions": [],
            "statutPoste": [],
            "typesContrat": [],
            "typesConvention": ["143684", "143685", "143686", "143687", "143706"],
            "niveauxExperience": [],
            "idsEtablissement": [],
            "secteursActivite": [],
            "typesTeletravail": [],
            "idNomZonesDeplacement": [],
            "positionNumbersExcluded": [],
            "typeClient": "CADRE",
            "sorts": [{"type": "DATE", "direction": "DESCENDING"}],
            "pagination": {"range": self.size, "startIndex": 0},
            "activeFiltre": True,
            "pointGeolocDeReference": {"distance": 0},
            "motsCles": "data",
        }
        job_ids = self._loop_recent(search_url, payload, stop_date)

        # Get hierarchy map (json containing id labels)
        hierarchy_url = self.base_url + self.endpoints['hierarchy']
        payload = {
            'codesPresentations': [
                'NAF_700_SERVICE_DOMAIN',
                'RECHERCHE_OFFRE_TYPE_CONTRAT',
                'OFFRE_NIVEAU_EXPERIENCE'
            ]
        }
        hierarchy = self._collect_hierarchy(hierarchy_url, payload)

        # Get individual content
        offer_url = self.base_url + self.endpoints['offer']
        params = {
            'numeroOffre' : None
        }
        yield from self._iter_content(offer_url, params, job_ids, hierarchy)
    
    def get_total(self) -> int|None:
        """Get total of result on API

        Returns:
            int|None: Total result
        """

        url = self.base_url + self.endpoints['search']
        payload = {
            "lieux": [],
            "fonctions": [],
            "statutPoste": [],
            "typesContrat": [],
            "typesConvention": ["143684", "143685", "143686", "143687", "143706"],
            "niveauxExperience": [],
            "idsEtablissement": [],
            "secteursActivite": [],
            "typesTeletravail": [],
            "idNomZonesDeplacement": [],
            "positionNumbersExcluded": [],
            "typeClient": "CADRE",
            "sorts": [{"type": "DATE", "direction": "DESCENDING"}],
            "pagination": {"range": 0, "startIndex": 0},
            "activeFiltre": True,
            "pointGeolocDeReference": {"distance": 0},
            "motsCles": "data",
        }
        result = self._safe_requests(url, method='POST', json=payload)
        if not result:
            return None
        return result.get('totalCount')

