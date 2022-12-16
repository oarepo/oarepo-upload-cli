from configparser import ConfigParser
import os
from typing import Optional

class AuthenticationTokenParser:
    """
    Unificator of token parsing from different sources.
    """
    def __init__(self, token_arg: Optional[str]):
        self.token_arg = token_arg
        self.ini_group = 'authentication'
        self.ini_token = 'token'
        self.ini_file_name = 'oarepo_upload.ini'

    def parse(self):
        """
        Tries to retrieve the token from all possible sources:
        - command line argument
        - ini file in the current directory
        - ini file in the home directory

        If not present anywhere, returns None.
        """
        if self.token_arg:
            return self.token_arg

        path = self.ini_file_name
        if os.path.isfile(path):
            # ini file present in the current directory
            return self.__get_token(path)

        path = f'{os.environ["HOME"]}/{self.ini_file_name}'
        if os.path.isfile(path):
            # ini file present in the home directory
            return self.__get_token(path)

    def __get_token(self, path):
        config_parser = ConfigParser()
        config_parser.read(path)
        
        return config_parser.get(self.ini_group, self.ini_token, fallback=None)