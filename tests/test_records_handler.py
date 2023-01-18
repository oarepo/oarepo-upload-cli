import requests

from oarepo_upload_cli.repository_records_handler import RepositoryRecordsHandler
from test_record import TestRecord

headers = { "Content-Type": "application/json" }
url = 'https://localhost:5000/api/model/'

def test_create():
    records_handler = RepositoryRecordsHandler(collection_url=url)

    # ARRANGE
    # -------
    record1 = TestRecord('2022-11-02')
    record2 = TestRecord('2015-10-13')
    record3 = TestRecord('2019-03-30')
    records = [record1, record2, record3]

    # ACT
    # ---
    created_records_urls = []
    for record in records:
        created_url = records_handler.upload_record(record)
        created_records_urls.append(created_url)

    # ASSERT
    # ------

    response = requests.get(url=url, headers=headers)
    response.raise_for_status()

    repo_created_links = [hit['links']['self'] for hit in response['hits']['hits']]

    assert len(created_records_urls) == len(repo_created_links)
    assert all([a == b for a, b in zip(sorted(created_records_urls), sorted(repo_created_links))])

def test_upload():
    records_handler = RepositoryRecordsHandler(collection_url=url)

    # ARRANGE
    # -------
    record_previous = TestRecord('2001-03-07')
    created_record_url = records_handler.create_record(record_previous)

    new_updated = '2001-03-08'
    record_new = TestRecord(new_updated)

    # ACT
    # ---
    uploaded_record_url = records_handler.upload_record(record_new)

    # ASSERT
    # ------

    # modified the same record
    assert created_record_url == uploaded_record_url
    
    query_params = { 'id': created_record_url }
    response = requests.get(url=url, headers=headers, params=query_params)
    response.raise_for_status()

    # its the same record
    assert response['links']['self'] == uploaded_record_url

    # field updated was modified correctly
    assert response['metadata']['upadted'] == new_updated