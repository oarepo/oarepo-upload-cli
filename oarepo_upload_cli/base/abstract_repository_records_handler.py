from abc import ABC, abstractmethod
from http import HTTPStatus
import requests
from typing import Dict, Optional

from oarepo_upload_cli.base.abstract_file import AbstractFile
from oarepo_upload_cli.base.abstract_metadata import AbstractMetadata
from oarepo_upload_cli.base.abstract_record import AbstractRecord
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.exceptions import ExceptionMessage, RepositoryCommunicationException

class AbstractRepositoryRecordsHandler(ABC):
    def __init__(self, config: Config):
        self._config = config
        self._headers = { "Content-Type": "application/json" }
    
    @abstractmethod
    def get_id_query(id: str) -> Dict[str, str]:
        pass

    def create_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Creates a record in the repository with the given metadata.
        
        Returns created record metadata.
        """
        
        response = self._send_request('post', url=self._config.collection_url, headers=self._headers, json=record.metadata.metadata, verify=False, auth=self._config.auth)

        response_payload = response.json()
        return response_payload

    def delete_file(self, record_files_link: str, file: AbstractFile):
        """
        Tries to delete a given file of a given record by its key.
        """
        
        assert file.key is not None, "File's key was not set."
        
        file_url = f'{self._config.collection_url}{record_files_link}/{file.key}'
        
        delete_response = self._send_request('delete', url=file_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        if delete_response.status_code != HTTPStatus.OK.value:
            # TODO: The file was not deleted correctly.
            
            return
        
        commit_url = f'{file_url}/commit'
        
        commit_response = self._send_request('post', url=commit_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        if commit_response.status_code != HTTPStatus.OK.value:
            # TODO: The commit was not successful.
            
            return        

    def delete_record(self, record_self_link: str) -> Optional[bool]:
        """
        Tries to delete a given record.
        """
        
        record_url = f'{self._config.collection_url}{record_self_link}'
        self._send_request('delete', url=record_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        return True

    def get_record(self, record: AbstractRecord) -> Optional[object]:
        """
        Performs search request for the given record in the repository.
        Returns a tuple that consists of an indicator whether it is a new record,
        and a record from the repository given by the record identifier if exists, otherwise None.
        """
        
        assert record.id is not None, "Record's identifier was not set."

        params = self.get_id_query(record.id)
        
        response = self._send_request('get', url=self._config.collection_url, params=params, headers=self._headers, verify=False, auth=self._config.auth)
        response_payload = response.json()
        
        hits = response_payload['hits']['hits']
        return None if not hits else hits[0]

    def get_records_files(self, record_files_link: str):
        """
        Returns metadata of a given record files.
        """
        
        records_files_url = f'{self._config.collection_url}{record_files_link}'
        response = self._send_request('get', url=records_files_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        record_repository_files = response.json()
        return record_repository_files['entries']

    def update_metadata(self, record_self_link: str, new_metadata: AbstractMetadata):
        """
        Perform actualization of a given records metadata.
        """
        
        record_url = f'{self._config.collection_url}{record_self_link}'
        response = self._send_request('put', url=record_url, headers=self._headers, json=new_metadata.metadata, verify=False, auth=self._config.auth)
        
        response_payload = response.json()
        return response_payload

    def update_file(self, record_files_link: str, file: AbstractFile):
        # PUT the newer file metadata.
        file_url = f'{self._config.collection_url}{record_files_link}/{file.key}'
        
        put_updated_response = self._send_request('put', url=file_url, headers=self._headers, json=file.metadata, verify=False, auth=self._config.auth)
        
        if put_updated_response.status_code != HTTPStatus.OK.value:
            # TODO: The file metadata was not updated correctly.
            
            return
        
        # PUT content
        put_content_url = f'{file_url}/content'
        put_headers = { "Content-Type": file.content_type }    
        put_request_data = file.get_reader()
        
        put_response = self._send_request('put', url=put_content_url, headers=put_headers, json=put_request_data, verify=False, auth=self._config.auth)
        
        if put_response.status_code != HTTPStatus.OK.value:
            # TODO: The file content was not uploaded correctly.
            
            return
        
        # POST commit.
        commit_url = f'{file_url}/commit'
        
        commit_response = self._send_request('post', url=commit_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        if commit_response.status_code != HTTPStatus.OK.value:
            # TODO: The commit was not successful.
            
            return

    def create_file(self, record_files_link: str, file: AbstractFile):
        """
        Creates a file given by the file metadata of a given record if it does not exists yet.
        If it already exists, updates it.
        """
        
        # POST the file metadata (a key).
        post_files_url = f'{self._config.collection_url}{record_files_link}'
        post_request_data = file.metadata
        
        post_response = self._send_request('post', url=post_files_url, headers=self._headers, json=post_request_data, verify=False, auth=self._config.auth)
        
        if post_response.status_code != HTTPStatus.OK.value:
            # TODO: The file metadata was not uploaded correctly.
            
            return
        
        # PUT content
        put_content_url = f'{post_files_url}/{file.key}/content'
        put_headers = { "Content-Type": file.content_type }    
        put_request_data = file.get_reader()
        
        put_response = self._send_request('put', url=put_content_url, headers=put_headers, json=put_request_data, verify=False, auth=self._config.auth)
        
        if put_response.status_code != HTTPStatus.OK.value:
            # TODO: The file content was not uploaded correctly.
            
            return
        
        # POST commit.
        commit_url = f'{post_files_url}/{file.key}/commit'
        
        commit_response = self._send_request('post', url=commit_url, headers=self._headers, verify=False, auth=self._config.auth)
        
        if commit_response.status_code != HTTPStatus.OK.value:
            # TODO: The commit was not successful.
            
            return

    def _send_request(self, http_verb, **kwargs):
        try:
            request_method = getattr(globals()['requests'], http_verb)
            response = request_method(**kwargs)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError.value, conn_err) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError.value, http_err, response.text, url=kwargs['url']) from http_err
        except Exception as err:
            raise RepositoryCommunicationException(err.message, err) from err
        
        return response

        