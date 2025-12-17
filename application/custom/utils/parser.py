from typing import Any
from bs4 import BeautifulSoup
import re



class XPathSearch:

    """Safely search xpath (list of key or index) in a dict"""

    def __new__(cls, json:dict, *xpath:str|list[int], warning=True) -> Any:
        """Search xpath in json

        Args:
            json (dict): The dict object
            *xpath (str, list[int]): XPath to search
            warning (bool): whether to print a warning or not when not found

        Returns:
            Any, None: The dict value, None if not found
        """

        return cls._search(json, *xpath, warning=warning)

    @staticmethod
    def _search(json:dict, *xpath:str|int|float|list[int], warning=True):
        value = json
        try:
            for key in xpath:
                if isinstance(key, (str, int, float)):
                    value = value.get(key)
                elif isinstance(key, list):
                    value = value[key[0]]
            return value
        except (KeyError, IndexError, AttributeError):
            if warning:
                print('WARNING: failed to get', xpath)
            return None



class ParseHTML:

    """Parse text on a HTML string"""

    def __new__(cls, html:str) -> str:
        """Parse text in HTML string and remove all tags

        Args:
            html (str): the HTML string to parse

        Returns:
            str: the cleaned text
        """

        return cls.__parse_html(html)
    
    @staticmethod
    def __parse_html(html:str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(separator=" ")
    

class ParseNumeric:

    """Parse numeric values from string"""

    def __new__(cls, text:str) -> list[int]:
        return cls.__parse_numeric(text)
    
    @staticmethod
    def __parse_numeric(text:str) -> list[int]:
        numbers = []
        for n in re.findall(r'\d[\d ]*', text):
            formatted = n.replace(' ', '')
            numbers.append(int(formatted))
        return numbers