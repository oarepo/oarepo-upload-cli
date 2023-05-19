from configparser import ConfigParser
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

@dataclass
class AuthenticationTokenParserConfig:
    ini_group: str
    ini_token: str
    ini_file_name: str

class AuthenticationTokenParser:
    """
    Unificator of token parsing from different sources.
    """
    def __init__(self, config: AuthenticationTokenParserConfig, token_arg: Optional[str] = None):
        self._token_arg = token_arg
        self._config = config

    def get_token(self):
        """
        Tries to retrieve the token from possible sources:
        - command line argument
        - ini file in the current directory
        - hidden ini file in the home directory
        - ini file in the .config directory in the home directory

        If not present anywhere, returns None.
        """
        if self._token_arg:
            return self._token_arg

        possible_token_locations = [
            self._config.ini_file_name,                                   # current dir
            f'{os.environ["HOME"]}/.{self._config.ini_file_name}',        # home dir
            f'{os.environ["HOME"]}/.config/.{self._config.ini_file_name}' # .config dir
        ]

        for ini_file_path in possible_token_locations:
            if Path(ini_file_path).exists():
                return self.__get_token(ini_file_path)
        
        return None

    def __get_token(self, path):
        config_parser = ConfigParser()
        config_parser.read(path)
        
        return config_parser.get(self._config.ini_group, self._config.ini_token, fallback=None)