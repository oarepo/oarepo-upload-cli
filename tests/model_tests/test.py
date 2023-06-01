import functools
import os
import pytest
import requests

from oarepo_upload_cli.token_auth import BearerAuthentication
from .test_records_handler import TestRepositoryRecordsHandler
from test_record import TestRecord

def requests_send_request(headers, auth, http_verb, url):
    try:
        request_method = getattr(globals()['requests'], http_verb)
        response = request_method(url=url, headers=headers, verify=False, auth=auth)

        response.raise_for_status()
    except Exception as err:
        print(err)
        
        return
    
    return response.json()

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

def test_create():
    records_handler = TestRepositoryRecordsHandler(collection_url=url)

    # ARRANGE
    # -------
    record1 = TestRecord('2022-11-02')
    record2 = TestRecord('2015-10-13')
    record3 = TestRecord('2019-03-30')

    records = [record1, record2, record3]

    # ACT
    # ---
    created_ids = [records_handler.upload_record(record) for record in records]
    
    # ASSERT
    # ------
    response = requests.get(url=url, headers=headers, verify=False)
    response.raise_for_status()

    response_payload = response.json()

    hits_ids = [hit['id'] for hit in response_payload['hits']['hits']]

    assert len(created_ids) == len(hits_ids)
    assert all([a == b for a, b in zip(sorted(created_ids), sorted(hits_ids))])

def test_upload():
    # ARRANGE
    # -------
    records_handler = TestRepositoryRecordsHandler(collection_url=url)

    record_previous = TestRecord('2001-03-07')
    record_previous.id = records_handler.upload_record(record_previous)

    new_updated = '2001-03-08'
    record_new = TestRecord(new_updated)
    record_new.id = record_previous.id

    # ACT
    # ---
    record_new.id = records_handler.upload_record(record_new)

    # ASSERT
    # ------

    # modified the same record
    assert record_new.id == record_previous.id
    
    response = requests.get(url=f'{url}{record_previous.id}', headers=headers, verify=False)
    response.raise_for_status()

    response_payload = response.json()

    # its the same record
    assert response_payload['id'] == record_new.id

    # field updated was modified correctly
    assert response_payload['metadata']['updated'] == new_updated
    
if __name__ == "__main__":
    headers = { "Content-Type": "application/json" }
    collection_url = 'https://localhost:5000/api/model/'
    
    bearer_token = os.getenv('BEARER_TOKEN')
    auth = BearerAuthentication(bearer_token)
    
    send_request = functools.partial(requests_send_request, headers, auth)