from http import HTTPStatus
import requests

from abstract_record import AbstractRecord
from exceptions import ExceptionMessage, RepositoryCommunicationException

class RepositoryRecordsHandler:
    def __init__(self, collection_url: str):
        if not collection_url.endswith('/'):
            collection_url += '/'

        self.collection_url = collection_url
        self.headers = { "Content-Type": "application/json" }

    def upload_record(self, record: AbstractRecord) -> None:
        """
        """
        url = f'{self.collection_url}'
        metadata = record.get_metadata()

        try:
            response = requests.put(url=url, headers=self.headers, data=metadata)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        if response.status_code == HTTPStatus.NOT_FOUND.value:
            self.create_record(record)
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as http_err:
                raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err

    def create_record(self, record: AbstractRecord) -> None:
        """
        """
        url = f'{self.collection_url}'
        metadata = record.get_metadata()

        try:
            response = requests.post(url=url, headers=self.headers, data=metadata)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        

        