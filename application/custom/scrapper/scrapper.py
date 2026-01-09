import time
import requests
from curl_cffi import requests as cffi_requests

from ..utils.parser import ParseHTML



class Scrapper:

    def __init__(self):
        self.session = self.__create_session()

    def __create_session(self):
        return cffi_requests.Session()

    def _safe_requests(self, url:str, method='GET', raise_status=True, _tic=0, **kwargs) -> str|None:
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
                return response.text
            elif raise_status:
                response.raise_for_status()
            return None
        except requests.RequestException as e:
            if _tic < 3:
                time.sleep(.5)
                return self._safe_requests(url, method, raise_status=raise_status, _tic=_tic+1, **kwargs)
            else:
                raise Exception(f'Request failed ({response.status_code}): {e}')
            
    def collect(self, url:str) -> str|None:
        """Request webpage and returns content

        Arguments:
            url (str): URL to request

        Returns:
            str|None: Webpage text content
        """

        response = self._safe_requests(url)
        return ParseHTML(response)
