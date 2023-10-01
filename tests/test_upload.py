import time
from datetime import datetime
from pathlib import Path

import pytest
import requests

from oarepo_upload_cli.config import Config
from oarepo_upload_cli.invenio.client import InvenioRepositoryClient
from oarepo_upload_cli.uploader import Uploader
from tests.source import TestSource

collection_url = "https://localhost:5000/api/simple/"


@pytest.fixture()
def clear_repository():
    def remove_records():
        headers = {"Authorization": f"Bearer {Path('.token').read_text().strip()}"}

        get_records_response = requests.get(
            url=collection_url,
            headers=headers,
            verify=False,
        )
        get_records_response.raise_for_status()

        get_records_response_payload = get_records_response.json()
        hits_ids = [hit["id"] for hit in get_records_response_payload["hits"]["hits"]]

        for record_id in hits_ids:
            response = requests.delete(
                url=f"{collection_url}{record_id}", headers=headers, verify=False
            )
            response.raise_for_status()

    remove_records()
    try:
        yield
    finally:
        remove_records()


def get_records():
    headers = {"Authorization": f"Bearer {Path('.token').read_text().strip()}"}
    time.sleep(1)
    get_records_response = requests.get(
        url=collection_url,
        headers=headers,
        verify=False,
    )
    get_records_response.raise_for_status()

    get_records_response_payload = get_records_response.json()
    ret = []
    for hit in get_records_response_payload["hits"]["hits"]:
        ret.append(
            {
                "md": hit["metadata"],
                "files": {
                    x["key"]: x.get("metadata")
                    for x in requests.get(
                        hit["links"]["files"],
                        headers=headers,
                        verify=False,
                    ).json()["entries"]
                },
            }
        )
    return ret


def t(month, day):
    return datetime(year=2023, month=month, day=day)


class LogCollector:
    def __init__(self):
        self.logs = []

    def __call__(self, *args):
        self.logs.append(args)

    def reset(self):
        self.logs = []

    @property
    def messages(self):
        return [x[3] for x in self.logs]


def test_upload(clear_repository, entry_points):
    config = Config(
        None,
        ("repository", "collection_url", collection_url),
        ("authentication", "token", Path(".token").read_text().strip()),
    )
    source = TestSource(config)
    repository = InvenioRepositoryClient(config)

    uploader = Uploader(config, source, repository)

    log = LogCollector()

    # create the first version of the record
    uploader.upload(t(1, 1), t(1, 31), log)
    assert log.messages == [
        "checking",
        "created",
    ]

    assert get_records() == [
        {
            "md": {
                "title": "Record 1",
                "originalId": "1",
                "dateModified": datetime(year=2023, month=1, day=1).isoformat(),
            },
            "files": {},
        }
    ]

    # nothing changed here
    log.reset()
    uploader.upload(t(1, 1), t(1, 31), log)
    assert log.messages == [
        "checking",
    ]

    assert get_records() == [
        {
            "md": {
                "title": "Record 1",
                "originalId": "1",
                "dateModified": datetime(year=2023, month=1, day=1).isoformat(),
            },
            "files": {},
        }
    ]

    # next month, the record comes again, but still not changed in the timestamp
    log.reset()
    uploader.upload(t(2, 1), t(2, 28), log)
    assert log.messages == [
        "checking",
    ]

    assert get_records() == [
        {
            "md": {
                "title": "Record 1",
                "originalId": "1",
                "dateModified": datetime(year=2023, month=1, day=1).isoformat(),
            },
            "files": {},
        }
    ]

    # next month, the metadata got updated
    log.reset()
    uploader.upload(t(3, 1), t(3, 31), log)
    assert log.messages == ["checking", "updated"]

    assert get_records() == [
        {
            "md": {
                "dateModified": "2023-03-01T00:00:00",
                "originalId": "1",
                "title": "Record 1 updated in month 3",
            },
            "files": {},
        }
    ]

    log.reset()
    uploader.upload(t(4, 1), t(4, 30), log)
    assert log.messages == ["checking", "sample.txt uploaded"]

    assert get_records() == [
        {
            "md": {
                "dateModified": "2023-03-01T00:00:00",
                "originalId": "1",
                "title": "Record 1 updated in month 3",
            },
            "files": {"sample.txt": {"dateModified": "2023-04-01T00:00:00"}},
        }
    ]

    # next month, the metadata got updated again, file stays the same
    log.reset()
    uploader.upload(t(5, 1), t(5, 31), log)
    assert log.messages == ["checking", "updated"]

    assert get_records() == [
        {
            "md": {
                "dateModified": "2023-05-01T00:00:00",
                "originalId": "1",
                "title": "Record 1 updated in month 5",
            },
            "files": {"sample.txt": {"dateModified": "2023-04-01T00:00:00"}},
        }
    ]

    # then a new file is uploaded
    log.reset()
    uploader.upload(t(6, 1), t(6, 30), log)
    assert log.messages == ["checking", "new.txt uploaded"]

    assert get_records() == [
        {
            "md": {
                "dateModified": "2023-05-01T00:00:00",
                "originalId": "1",
                "title": "Record 1 updated in month 5",
            },
            "files": {
                "sample.txt": {"dateModified": "2023-04-01T00:00:00"},
                "new.txt": {"dateModified": "2023-06-01T00:00:00"},
            },
        }
    ]

    # older file is removed
    log.reset()
    uploader.upload(t(7, 1), t(7, 31), log)
    assert log.messages == ["checking", "sample.txt deleted"]

    assert get_records() == [
        {
            "md": {
                "dateModified": "2023-05-01T00:00:00",
                "originalId": "1",
                "title": "Record 1 updated in month 5",
            },
            "files": {
                "new.txt": {"dateModified": "2023-06-01T00:00:00"},
            },
        }
    ]

    # record gets deleted
    log.reset()
    uploader.upload(t(8, 1), t(8, 31), log)
    assert log.messages == ["checking", "deleted"]

    assert get_records() == []
