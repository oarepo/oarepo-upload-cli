from http import HTTPStatus
import requests
from typing import Optional

from oarepo_upload_cli.abstract_metadata import AbstractMetadata
from oarepo_upload_cli.abstract_record import AbstractRecord
from oarepo_upload_cli.token_auth import BearerAuthentication
from oarepo_upload_cli.exceptions import ExceptionMessage, RepositoryCommunicationException

class RepositoryRecordsHandler:
    def __init__(self, collection_url: str, auth: BearerAuthentication):
        if not collection_url.endswith('/'):
            collection_url += '/'

        self._auth = auth
        self._collection_url = collection_url
        self._headers = { "Content-Type": "application/json" }

    def get_record(self, record: AbstractRecord):
        """
        Returns a record from the repository given by the collection url based on the id attribute.
        """
        
        if not hasattr(record, 'id'):
            raise AttributeError('Record is missing the \'id\' attribute.')
        
        record_url = f'{self._collection_url}{record.id}'
        
        try:
            response = requests.get(url=record_url, headers=self._headers, verify=False, auth=self._auth)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err
        
        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()
        
        repository_record = response.json()
        return repository_record

    def get_records_files(self, record: AbstractRecord):
        if not hasattr(record, 'id'):
            raise AttributeError('Record is missing the \'id\' attribute.')
        
        repository_record = self.get_record(record)
        files_url = repository_record['links']['files']
        records_files_url = f'{self._collection_url}{files_url}'
        
        try:
            response = requests.get(url=records_files_url, headers=self._headers, verify=False, auth=self._auth)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err
        
        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()
            
        record_repository_files = response.json()
        return record_repository_files['entries']

    def upload_metadata(self, record: AbstractRecord):
        if not hasattr(record, 'id'):
            raise AttributeError('Record is missing the \'id\' attribute.')
        
        record_url = f'{self._collection_url}{record.id}'
        
        try:
            response = requests.put(url=record_url, headers=self._headers, json=record.metadata, verify=False, auth=self._auth)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        if response.status_code == HTTPStatus.NOT_FOUND.value:
            raise ValueError()
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as http_err:
                raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err

            response_payload = response.json()
            
            return response_payload['id']
            
    def upload_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Uploads a record to the repository with metadata given by the record parameter.
        If already present, modifies the content.
        """
        
        if not hasattr(record, 'id'):
            return self._create_record(record)

        record_url = f'{self._collection_url}{record.id}'

        try:
            response = requests.put(url=record_url, headers=self._headers, json=record.metadata, verify=False, auth=self._auth)
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

    def upload_file(self, record_id, file_key):
        # TODO
        
        pass

    def _create_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Creates a record in the repository with metadata given by the record parameter.
        """

        try:
            response = requests.post(url=self._collection_url, headers=self._headers, json=record.metadata, verify=False, auth=self._auth)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        response_payload = response.json()

        return response_payload['id']

        

        