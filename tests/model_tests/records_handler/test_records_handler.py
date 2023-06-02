from http import HTTPStatus
import pytest

from ..infrastructure.records_handler import TestRepositoryRecordsHandler
from ..infrastructure.record import TestRecord

# Mock version of the source? :)
@pytest.fixture
def records_source():
    def _source():
        input_records = []
        
        return input_records
    
    return _source

def test_create_record(collection_url, repository_handler, send_request, records_source):
    created_metadatas = [repository_handler.create_record(source_record) for source_record in records_source()]
    
    records_response = send_request('get', collection_url)
    assert records_response.status_code == HTTPStatus.OK.value
    
    records_response_payload = records_response.json()
    records_hits = [hit for hit in records_response_payload['hits']['hits']]

    assert len(created_metadatas) == len(records_hits)
    assert all([a['id'] == b['id'] for a, b in zip(sorted(created_metadatas), sorted(records_hits))])

def test_delete_record(collection_url, repository_handler, send_request, records_source):
    created_metadatas = [repository_handler.create_record(source_record) for source_record in records_source()]

    for uploaded_record in created_metadatas:    
        record_url = f'{collection_url}{uploaded_record["links"]["self"]}'
        send_request('delete', record_url)
    
        gone_check_response = send_request('get', record_url)
        assert gone_check_response.status_code == HTTPStatus.GONE.value

def test_delete_file():
    pass

def test_get_record_exists(repository_handler, send_request, source):
    # ARRANGE
    # -------
    # TODO: apply source here
    record = TestRecord('2022-11-02')
    created_metadata = records_handler.create_record(record)

    # ACT
    # ---
    returned_metadata = records_handler.get_record(record)
    
    # ASSERT
    # ------
    assert created_metadata['id'] == returned_metadata['id']
    
def test_get_record_does_not_exist():
    records_handler = TestRepositoryRecordsHandler(collection_url, auth)

    # ARRANGE
    # -------
    # TODO: apply source here
    record = TestRecord('2022-11-02')

    # ACT
    # ---
    returned_metadata = records_handler.get_record(record)
    
    # ASSERT
    # ------
    assert returned_metadata is None

def test_update_metadata():
    pass

def test_upload_file():
    pass