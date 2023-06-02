import functools
from http import HTTPStatus
import os
import pytest
import requests

from oarepo_upload_cli.token_auth import BearerAuthentication
from ..infrastructure.records_handler import TestRepositoryRecordsHandler

@pytest.fixture(scope="module")
def collection_url():
    return 'https://localhost:5000/api/uct_theses/'

@pytest.fixture(scope="module")
def json_headers():
    return { "Content-Type": "application/json" }

@pytest.fixture(scope="module")
def bearer_auth():
    bearer_token = os.getenv('BEARER_TOKEN')
    
    return BearerAuthentication(bearer_token)

@pytest.fixture(scope="module")
def send_request(json_headers, bearer_auth):
    def _requests_send_request(headers, auth, http_verb, url):
        try:
            request_method = getattr(globals()['requests'], http_verb)
            response = request_method(url=url, headers=headers, verify=False, auth=auth)

            response.raise_for_status()
        except Exception as err:
            print(err)
            
            return
        
        return response
    
    return functools.partial(_requests_send_request, json_headers, bearer_auth)

@pytest.fixture(scope="module")
def repository_handler(collection_url, bearer_auth):
    return TestRepositoryRecordsHandler(collection_url, bearer_auth)

@pytest.fixture(autouse=True)
def repository_clean_up(collection_url, send_request):
    """
    Clean up, delete records metadata and files.
    """
    
    yield

    records_response_payload = send_request('get', collection_url)
    records_hits = [hit for hit in records_response_payload['hits']['hits']]

    for repository_record in records_hits:
        record_metadata_url = f'{collection_url}{repository_record["links"]["self"]}'
        send_request('delete', record_metadata_url)

        gone_check_response = send_request('get', record_metadata_url)
        if gone_check_response.status_code != HTTPStatus.GONE.value:
            print(f'Delete failed: {repository_record["links"]["self"]}')