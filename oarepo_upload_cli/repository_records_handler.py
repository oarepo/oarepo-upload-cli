from http import HTTPStatus
import requests
from typing import Dict, Optional

from oarepo_upload_cli.abstract_file import AbstractFile
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

    def delete_file(self, record: AbstractRecord, file: AbstractFile):
        pass

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
        
        if response.status_code == HTTPStatus.NOT_FOUND.value:
            return self._create_record(record)
        
        if response.status_code != HTTPStatus.OK.value:
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
        
        if response.status_code != HTTPStatus.OK.value:
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
            
            return response_payload
            
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
            
            return response_payload

    def upload_file(self, record: AbstractRecord, file: AbstractFile):
        if not hasattr(record, 'id'):
            raise AttributeError('Record is missing the \'id\' property.')
        
        # POST the file metadata (a key).
        post_files_url = f'{self._collection_url}{record.id}/files'
        post_request_data = file.metadata()
        
        post_response = self._send_request('post', url=post_files_url, headers=self._headers, json=post_request_data, verify=False, auth=self._auth)
        
        if post_response.status_code != HTTPStatus.OK.value:
            # TODO: The file metadata was not uploaded correctly.
            
            return
        
        # PUT content
        put_content_url = f'{post_files_url}/{file.key}/content'
        put_headers = { "Content-Type": file.content_type }    
        put_request_data = file.get_reader()
        
        put_response = self._send_request('put', url=put_content_url, headers=put_headers, json=put_request_data, verify=False, auth=self._auth)
        
        if put_response.status_code != HTTPStatus.OK.value:
            # TODO: The file content was not uploaded correctly.
            
            return
        
        # POST commit.
        commit_url = f'{post_files_url}/{file.key}/commit'
        
        commit_response = self._send_request('post', url=commit_url, headers=self._headers, verify=False, auth=self._auth)
        
        if commit_response.status_code != HTTPStatus.OK.value:
            # TODO: The commit was not successful.
            
            return
            

    def _create_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Creates a record in the repository with metadata given by the record parameter.
        """
        response = self._send_request('post', url=self._collection_url, headers=self._headers, json=record.metadata, verify=False, auth=self._auth)
        response_payload = response.json()
        
        return response_payload

    def _send_request(self, http_verb, **kwargs):
        try:
            request_method = getattr(globals()['requests'], http_verb)
            response = request_method(kwargs)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError) from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err
        
        return response

        