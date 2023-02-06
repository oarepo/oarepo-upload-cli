from http import HTTPStatus
import requests
from typing import Optional

from oarepo_upload_cli.abstract_record import AbstractRecord
from oarepo_upload_cli.exceptions import ExceptionMessage, RepositoryCommunicationException

class RepositoryRecordsHandler:
    def __init__(self, collection_url: str):
        if not collection_url.endswith('/'):
            collection_url += '/'

        self.collection_url = collection_url
        self.headers = { "Content-Type": "application/json" }

    def upload_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Uploads a record to the repository with metadata given by the record parameter.
        If already present, modifies the content.
        """
        
        if not record.id:
            return self._create_record(record)

        item_url = f'{self.collection_url}{record.id}'
        metadata = record.get_metadata()

        try:
            response = requests.put(url=item_url, headers=self.headers, json=metadata, verify=False)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        if response.status_code == HTTPStatus.NOT_FOUND.value:
            return self._create_record(record)
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as http_err:
                raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err

            response_payload = response.json()
            
            return response_payload['id']

    def _create_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Creates a record in the repository with metadata given by the record parameter.
        """
        
        metadata = record.get_metadata()

        try:
            response = requests.post(url=self.collection_url, headers=self.headers, json=metadata, verify=False)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        response_payload = response.json()

        return response_payload['id']

        

        