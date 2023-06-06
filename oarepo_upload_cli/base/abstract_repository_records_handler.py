from abc import ABC, abstractmethod
from http import HTTPStatus
import requests
from typing import Dict, Optional

from oarepo_upload_cli.base.abstract_file import AbstractFile
from oarepo_upload_cli.base.abstract_metadata import AbstractMetadata
from oarepo_upload_cli.base.abstract_record import AbstractRecord
from oarepo_upload_cli.config import Config
from oarepo_upload_cli.exceptions import ExceptionMessage, RepositoryCommunicationException
from oarepo_upload_cli.repository.url_builder import RepositoryURLBuilder

class AbstractRepositoryRecordsHandler(ABC):
    def __init__(self, config: Config):
        self._config = config
        self._json_headers = { "Content-Type": "application/json" }
        self._url_builder = RepositoryURLBuilder(self._config.collection_url)
    
    @abstractmethod
    def get_id_query(id: str) -> Dict[str, str]:
        pass

    def create_file(self, record_files_link: str, file: AbstractFile):
        """
        Creates a file given by the file metadata of a given record if it does not exists yet.
        If it already exists, updates it.
        """
        
        def post_metadata():
            url = self._url_builder.record(record_files_link)
            request_data = [file.metadata]
            
            res = self._send_request('post', url=url, json=request_data)
            if res.status_code != HTTPStatus.OK:
                # TODO: The file metadata was not uploaded correctly.
                
                return  
            
        def put_content():
            url = self._url_builder.file_content(record_files_link, file.key)
            headers = { "Content-Type": file.content_type }    
            request_data = file.get_reader()
            
            res = self._send_request('put', url=url, headers=headers, json=request_data)
            if res.status_code != HTTPStatus.OK:
                # TODO: The file content was not uploaded correctly.
                
                return      
        
        def post_commit():
            url = self._url_builder.file_commit(record_files_link, file.key)
        
            res = self._send_request('post', url=url)
            if res.status_code != HTTPStatus.OK:
                # TODO: The commit was not successful.
                
                return
        
        assert file.key is not None, "File's key was not set."
        assert file.metadata is not None, "File's metadata was not set."
        
        post_metadata()
        put_content()
        post_commit()


    def create_record(self, record: AbstractRecord) -> Optional[str]:
        """
        Creates a record in the repository with the given metadata.
        
        Returns created record metadata.
        """
        
        assert record.metadata is not None, "Record's metadata was not set."
        
        res = self._send_request('post', url=self._config.collection_url, json=record.metadata.metadata)
        res_payload = res.json()
        return res_payload

    def delete_file(self, record_files_link: str, file: AbstractFile):
        """
        Tries to delete a given file of a given record by its key.
        """
        
        def delete_metadata():
            url = self._url_builder.file(record_files_link, file.key)
        
            res = self._send_request('delete', url=url)
            if res.status_code != HTTPStatus.OK:
                # TODO: The file was not deleted correctly.
                
                return    
        
        def post_commit():
            url = self._url_builder.file_commit(record_files_link, file.key)
        
            res = self._send_request('post', url=url)
            if res.status_code != HTTPStatus.OK:
                # TODO: The commit was not successful.
                
                return        
        
        assert file.key is not None, "File's key was not set."
        
        delete_metadata()
        post_commit()

    def delete_record(self, record_self_link: str) -> Optional[bool]:
        """
        Tries to delete a given record.
        """
        
        url = self._url_builder.record(record_self_link)
        res = self._send_request('delete', url=url)
        assert res.status_code == HTTPStatus.GONE, f'Deletion of the record {record_self_link} was not successful.'
        
        return True

    def get_record(self, record: AbstractRecord) -> Optional[object]:
        """
        Performs search request for the given record in the repository.
        Returns a tuple that consists of an indicator whether it is a new record,
        and a record from the repository given by the record identifier if exists, otherwise None.
        """
        
        assert record.id is not None, "Record's identifier was not set."

        params = self.get_id_query(record.id)
        
        res = self._send_request('get', url=self._config.collection_url, params=params)
        
        res_payload = res.json()
        hits = res_payload['hits']['hits']
        return None if not hits else hits[0]

    def get_records_files(self, record_files_link: str):
        """
        Returns metadata of a given record files.
        """
        
        url = self._url_builder.record_files(record_files_link)
        
        res = self._send_request('get', url=url)
        
        res_payload = res.json()
        return res_payload['entries']

    def update_metadata(self, record_self_link: str, new_metadata: AbstractMetadata):
        """
        Perform actualization of a given records metadata.
        """
        
        url = self._url_builder.record(record_self_link)
        
        res = self._send_request('put', url=url, json=new_metadata.metadata)
        res_payload = res.json()
        return res_payload

    def update_file(self, record_files_link: str, file: AbstractFile):
        """
        Updates the content of a give file.
        """
        
        def put_metadata():
            url = self._url_builder.file(record_files_link, file.key)
        
            res = self._send_request('put', url=url, json=file.metadata)
            if res.status_code != HTTPStatus.OK:
                # TODO: The file metadata was not updated correctly.
                
                return    
        
        def put_content():
            url = self._url_builder.file_content(record_files_link, file.key)
            headers = { "Content-Type": file.content_type }
            request_data = file.get_reader()
            
            res = self._send_request('put', url=url, headers=headers, data=request_data)
            if res.status_code != HTTPStatus.OK:
                # TODO: The file content was not uploaded correctly.
                
                return    
        
        def post_commit():
            url = self._url_builder.file_commit(record_files_link, file.key)
        
            res = self._send_request('post', url=url)
            if res.status_code != HTTPStatus.OK:
                # TODO: The commit was not successful.
                
                return    
            
        put_metadata()
        put_content()
        post_commit()
        
    def _send_request(self, http_verb, **kwargs):
        try:
            request_method = getattr(globals()['requests'], http_verb)
            headers = self._json_headers if 'headers' not in kwargs else kwargs['headers']
            
            res = request_method(verify=False, auth=self._config.auth, headers=headers **kwargs)
            res.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException(ExceptionMessage.ConnectionError, conn_err) from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException(ExceptionMessage.HTTPError, http_err, res.text, url=kwargs['url']) from http_err
        except Exception as err:
            raise RepositoryCommunicationException(err.message, err) from err

        return res