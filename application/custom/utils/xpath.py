from typing import Any




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
    def _search(json:dict, *xpath:str|list[int], warning=True):
        value = json
        try:
            for key in xpath:
                if isinstance(key, str):
                    value = value.get(key)
                elif isinstance(key, list):
                    value = value[key[0]]
            return value
        except (KeyError, IndexError, AttributeError):
            if warning:
                print('WARNING: failed to get', xpath)
            return None

