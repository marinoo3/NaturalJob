from abc import ABC, abstractmethod
import time

import requests
from curl_cffi import requests as cffi_requests




class BaseAPI(ABC):

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    def __init__(self, base_url:str, keyword="data", headers:dict=None, cffi=False) -> None:
        self.base_url = base_url
        self.keyword = keyword
        self.session = self.__create_session(cffi)
        self.session.headers = headers or self.headers

    def __create_session(self, cffi:bool):
        if cffi:
            return cffi_requests.Session()
        return requests.Session()
    
    @abstractmethod
    def _loop_recent(self):
        ...

    def _safe_requests(self, url:str, method='GET', raise_status=True, _tic=0, **kwargs) -> dict|None:
        """Make a requests with exeption and retries

        Args:
            method (str): Method to use on request ('GET', 'POST', 'PUT', 'DELETE'). Defaults to 'GET'.

        Return:
            (Response): The response json output
        """

        method = method.upper()
        if method not in ['GET', 'POST', 'PUT', 'DELETE']:
            raise ValueError(f"Unsupported method: {method}. Should be in ('GET', 'POST', 'PUT', 'DELETE')")

        try:
            response = self.session.request(method, url, **kwargs)
            if response.status_code in [200, 400]:
                return response.json()
            elif raise_status:
                response.raise_for_status()
            return None
        except requests.RequestException as e:
            if _tic < 3:
                time.sleep(.5)
                return self._safe_requests(url, method, raise_status=raise_status, _tic=_tic+1, **kwargs)
            else:
                raise Exception(f'Request failed ({response.status_code}): {e}')