from collections import deque
from json import JSONDecodeError
import requests
from typing import Any, Deque

from .config import Config
from .exceptions import ExceptionMessage, RepositoryCommunicationException

Path = list[str]
ResponseContent = dict

class RepositoryDataExtractor:
    """
    Sends, processes and returns data from a request sent to the given repository.
    """

    def __init__(self, config: Config):
        self._config = config

    def get_data(self, path: Path) -> Any | None:
        """
        Sends a request to the given repository URL. Tries to acquire the data from the response determined by the given path.

        Returns the data or prints an error with the description what happened.
        """

        try:
            url = self._config.collection_url
            response = requests.get(url, auth=self._config.auth)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError.value, conn_err) from conn_err
        except requests.exceptions.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError.value, http_err, response.text, url=url) from http_err
        except Exception as err:
            raise RepositoryCommunicationException(err.message, err) from err
        
        try:
            content = response.json()
        except JSONDecodeError as serialization_err:
            raise RepositoryCommunicationException(ExceptionMessage.JSONContentNotSerializable.value, serialization_err) from serialization_err
        
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
        

