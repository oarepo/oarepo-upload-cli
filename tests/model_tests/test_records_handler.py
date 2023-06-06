from typing import Dict
import pytest
import requests

from oarepo_upload_cli.base.abstract_repository_records_handler import AbstractRepositoryRecordsHandler
from test_record import TestRecord

class TestRepositoryRecordsHandler(AbstractRepositoryRecordsHandler):
    def get_id_query(id: str) -> Dict[str, str]:
        return {}

headers = { "Content-Type": "application/json" }
url = 'https://localhost:5000/api/model/'

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    yield

    get_records_response = requests.get(url=url, headers=headers, verify=False)
    get_records_response.raise_for_status()

    get_records_response_payload = get_records_response.json()
    hits_ids = [hit['id'] for hit in get_records_response_payload['hits']['hits']]


    for record_id in hits_ids:
        response = requests.delete(url=f'{url}{record_id}', headers=headers, verify=False)
        response.raise_for_status()

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