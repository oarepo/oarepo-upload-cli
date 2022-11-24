import requests
from token_auth import TokenAuth

class RepositoryDataExtractor:
    """
    Sends, processes and returns data from a request sent to the given repository.
    """

    def __init__(self, url, token=None):
        self.url = url
        self.token = token

    def get_data(self, path):
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
            print(f'Network problem has occurred: {conn_err}.')
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP Error has occurred: {http_err}.')
        except Exception as err:
            print(f'An error has occurred: {err}.')
        else:
            content = response.json()

            found, invalid_path_item = self.__check_path(content, path)
            if not found:
                print(f'Invalid item in the path: {invalid_path_item}')
                return
            
            data = self.__traverse_path(content, path)

            return data

    def __traverse_path(data, path):
        for p in path:
            data = data[p]

        return data
    
    def __check_path(self, response_content: dict, path: list[str]) -> bool:
        pass
        

