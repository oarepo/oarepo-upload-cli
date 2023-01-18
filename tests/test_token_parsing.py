import pytest
import os

from oarepo_upload_cli.authentication_token_parser import AuthenticationTokenParser

@pytest.mark.parametrize('token_arg,expected', [('arg1', 'arg1'), ('arg2', 'arg2')])
def test_parse_token_arg(token_arg, expected):
    """
    Tests correct parsing of a token passed as a command line argument.
    """
    token_parser = AuthenticationTokenParser(token_arg)
    result = token_parser.parse()

    assert result == expected

current_dir, home_dir, config_home_dir = '.', os.environ['HOME'], f'{os.environ["HOME"]}/.config'
file_name = 'oarepo_upload.ini'

def create_file(directory, token):
    ini_content_template = lambda token: f'[authentication]\ntoken = {token}\n'

    with open(f'{directory}/{file_name}', 'w') as f:
        content = ini_content_template(token)        
        f.write(content)

def remove_file(directory):
    os.remove(f'{directory}/{file_name}')

@pytest.mark.parametrize('token,expected', [('curr_dir1', 'curr_dir1'), ('curr_dir2', 'curr_dir2')])
def test_parse_ini_current_dir(token, expected):
    """
    Tests correct parsing of a token written in an ini file located in the current directory.
    """

    create_file(current_dir, token)

    token_parser = AuthenticationTokenParser()
    result = token_parser.parse()

    assert result == expected

    remove_file(current_dir)
    
@pytest.mark.parametrize('token,expected', [('home_dir1', 'home_dir1'), ('home_dir2', 'home_dir2')])
def test_parse_ini_home_dir(token, expected):
    """
    Tests correct parsing of a token written in an ini file located in the home directory.
    """

    create_file(home_dir, token)

    token_parser = AuthenticationTokenParser()
    result = token_parser.parse()

    assert result == expected

    remove_file(home_dir)

@pytest.mark.parametrize('token,expected', [('config_home_dir1', 'config_home_dir1'), ('config_home_dir2', 'config_home_dir2')])
def test_parse_ini_config_home_dir(token, expected):
    """
    Tests correct parsing of a token written in an ini file located in the config directory in the home directory.
    """

    create_file(config_home_dir, token)

    token_parser = AuthenticationTokenParser()
    result = token_parser.parse()

    assert result == expected

    remove_file(config_home_dir)