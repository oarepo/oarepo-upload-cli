import functools
import os
import pytest
import requests

from oarepo_upload_cli.token_auth import BearerAuthentication
from .infrastructure.records_handler import TestRepositoryRecordsHandler
from .infrastructure.record import TestRecord

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """
    Clean up, delete records metadata and files.
    """
    
    yield

    records_response_payload = send_request('get', collection_url)
    records_hits = [hit for hit in records_response_payload['hits']['hits']]

    for record in records_hits:
        if record['files']['enabled']:
            # Delete stored files and their content.
            files_url = f'{collection_url}/{record["links"]["files"]}'
            files_response_payload = send_request('get', file_url)
            
            for file_entry in files_response_payload['entries']:
                file_url = f'{files_url}/{file_entry["key"]}'
                send_request('delete', file_url)
                
                commit_deletion_url = f'{file_url}/commit'
                send_request('post', commit_deletion_url)
        
        # Delete metadata.
        record_metadata_url = f'{collection_url}{record["id"]}'
        send_request('delete', record_metadata_url)
        
        delete_metadata_commit_url = f'{record_metadata_url}/commit'
        send_request('post', delete_metadata_commit_url)

def test_delete_record():
    records_handler = TestRepositoryRecordsHandler(collection_url, auth)

    # ARRANGE
    # -------
    # TODO: apply source here
    record = TestRecord('2022-11-02')
    created_metadata = records_handler.get_record(record)

    # ACT
    # ---
    records_handler.delete_record(record)
    
    # ASSERT
    # ------
    records_response_payload = send_request('get', collection_url)
    records_hits_ids = [hit['id'] for hit in records_response_payload['hits']['hits']]

    assert created_metadata['id'] not in records_hits_ids

def test_get_record_all_new():
    records_handler = TestRepositoryRecordsHandler(collection_url, auth)

    # ARRANGE
    # -------
    # TODO: apply source here
    record1 = TestRecord('2022-11-02')
    record2 = TestRecord('2015-10-13')
    record3 = TestRecord('2019-03-30')

    records = [record1, record2, record3]

    # ACT
    # ---
    created_metadatas_ids = [records_handler.get_record(record)['id'] for record in records]
    
    # ASSERT
    # ------
    records_response_payload = send_request('get', collection_url)
    records_hits_ids = [hit['id'] for hit in records_response_payload['hits']['hits']]

    assert len(created_metadatas_ids) == len(records_hits_ids)
    assert all([a == b for a, b in zip(sorted(created_metadatas_ids), sorted(records_hits_ids))])

def requests_send_request(headers, auth, http_verb, url):
    try:
        request_method = getattr(globals()['requests'], http_verb)
        response = request_method(url=url, headers=headers, verify=False, auth=auth)

        response.raise_for_status()
    except Exception as err:
        print(err)
        
        return
    
    return response.json()
    
if __name__ == "__main__":
    headers = { "Content-Type": "application/json" }
    collection_url = 'https://localhost:5000/api/model/'
    
    bearer_token = os.getenv('BEARER_TOKEN')
    auth = BearerAuthentication(bearer_token)
    
    send_request = functools.partial(requests_send_request, headers, auth)