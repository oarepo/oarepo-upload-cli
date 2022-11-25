from collections import deque
from typing import Any, Deque, Union
import requests
from json import JSONDecodeError

from token_auth import TokenAuth

Path = list[str]
ResponseContent = dict

class RepositoryCommunicationException(Exception):
    """
    Raised when there is a problem with requesting data from repository happens.
    """    
    pass

class RepositoryDataExtractor:
    """
    Sends, processes and returns data from a request sent to the given repository.
    """

    def __init__(self, url: str, token: str=None):
        self.url = url
        self.token = token

    def get_data(self, path: Path) -> Any | None:
        """
        Sends a request to the given repository URL. Tries to acquire the data from the response determined by the given path.

        Returns the data or prints an error with the description what happened.
        """

        try:
            response = None

            if self.token:
                # NOTE: prod preparation, after resolving what token we will use, remove the else branch
                response = requests.get(self.url, auth=TokenAuth(self.token))
            else:
                response = requests.get(self.url)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException('Network problem has occurred') from conn_err
        except requests.exceptions.HTTPError as http_err:
            raise RepositoryCommunicationException('HTTP error has occurred.') from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err
        
        try:
            content = response.json()
        except JSONDecodeError as serialization_err:
            raise RepositoryCommunicationException('Response could not be serialized') from serialization_err
        
        found, invalid_path_item = self.__check_path(content, deque(path))
        if not found:
            print(f'Invalid item in the path: {invalid_path_item}')
            return
        
        data = self.__traverse_path(content, path)

        return data

    def __traverse_path(self, content: ResponseContent, path: Path) -> Any:
        for p in path:
            content = content[p]

        return content
    
    def __check_path(self, content: ResponseContent, path_to_check: Deque[str]) -> bool:
        if not path_to_check:
            return True, None
        
        p = path_to_check.popleft()
        if not p in content:
            return False, p
    
        return self.__check_path(content[p], path_to_check)
        

