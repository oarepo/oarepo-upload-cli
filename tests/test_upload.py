import requests
from typing import List, Optional

from test_record import TestRecord

collection_url = 'https://localhost:5000/api/model/'
headers = { "Content-Type": "application/json" }

def create_record(record: TestRecord) -> tuple[bool, Optional[str]]:
    """
    Tries to create a record in the repository from the given records metadata.
    Method uses the HTTP POST, because it assumes that the record is not present yet.

    If the record's creation was successful,
    returns a tuple True and url link of the created item if it was successful.
    
    Otherwise, it returns False and None.
    """

    try:
        response = requests.post(url=collection_url, headers=headers, data=record.get_metadata(), verify=False)

        response.raise_for_status()
    except requests.ConnectionError as conn_err:
        print(f'Failed to connect to the repository: {conn_err}.')
        return False, None
    except requests.HTTPError as http_err:
        print(f'Failed to create a record with the id: {record.id}, due to the HTTP error: {http_err}.')
        return False, None
    except Exception as err:
        print(f'Failed to create a record with the id: {record.id} due to the error: {err}.')
        return False, None

    return True, response.headers['links']['self']
    
def create_records(records: List[TestRecord]) -> List[str]:
    """
    Creates records in the repository from the given records.
    Returns a list of urls of successfully created records.
    """

    records_urls = []

    for record in records:
        has_created, record_url = create_record(record)

        if has_created:
            records_urls.append(record_url)

    return records_urls