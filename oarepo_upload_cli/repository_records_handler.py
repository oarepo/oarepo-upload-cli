import requests

from abstract_record import AbstractRecord
from repository_communication_exception import RepositoryCommunicationException

class RepositoryRecordsHandler:
    def __init__(self, base_repo_url: str):
        if not base_repo_url.endswith('/'):
            base_repo_url += '/'

        self.repo_url = base_repo_url

    def upload_record(self, record: AbstractRecord) -> None:
        """
        """

        url = f'{self.repo_url}/{record.id}'
        headers = { "Content-Type": "application/json" }
        metadata = record.get_metadata()

        try:
            response = requests.put(url=url, headers=headers, data=metadata)
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException('Network problem has occurred') from conn_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        if response.status_code == 404:
            self.create_record(record)
        else:
            try:
                response.raise_for_status()
            except requests.HTTPError as http_err:
                raise RepositoryCommunicationException('HTTP error has occured') from http_err

    def create_record(self, record: AbstractRecord) -> None:
        """
        """
        
        url = f'{self.repo_url}/{record.id}'
        headers = { "Content-Type": "application/json" }
        metadata = record.get_metadata()

        try:
            response = requests.post(url=url, headers=headers, data=metadata)

            response.raise_for_status()
        except requests.ConnectionError as conn_err:
            raise RepositoryCommunicationException('Network problem has occurred') from conn_err
        except requests.HTTPError as http_err:
            raise RepositoryCommunicationException('HTTP error has occured') from http_err
        except Exception as err:
            raise RepositoryCommunicationException() from err

        

        