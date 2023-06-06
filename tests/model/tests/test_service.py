import datetime

import pytest
import pytz
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError

from model.proxies import current_service


def test_read(app, db, sample_record, sample_metadata_list, search_clear):
    with pytest.raises(PIDDoesNotExistError):
        current_service.read(system_identity, "fwegthi8op")
    read_record = current_service.read(system_identity, sample_record["id"])
    assert read_record.data["metadata"] == sample_record.metadata


def test_create(app, db, sample_metadata_list, search_clear):
    created_records = []
    for sample_metadata_point in sample_metadata_list:
        created_records.append(
            current_service.create(system_identity, sample_metadata_point)
        )
    for sample_metadata_point, created_record in zip(
        sample_metadata_list, created_records
    ):
        created_record_reread = current_service.read(
            system_identity, created_record["id"]
        )
        assert (
            created_record_reread.data["metadata"] == sample_metadata_point["metadata"]
        )


def test_update(app, db, sample_record, sample_metadata_list, search_clear):
    with pytest.raises(PIDDoesNotExistError):
        current_service.update(
            system_identity, "fwsegerhjtyuk754dh", sample_metadata_list[2]
        )

    old_record_data = current_service.read(system_identity, sample_record["id"]).data
    updated_record = current_service.update(
        system_identity, sample_record["id"], sample_metadata_list[2]
    )
    updated_record_read = current_service.read(system_identity, sample_record["id"])
    assert old_record_data["metadata"] == sample_record["metadata"]
    assert (
        updated_record.data["metadata"]
        == sample_metadata_list[2]["metadata"]
        != old_record_data["metadata"]
    )
    assert updated_record_read.data["metadata"] == updated_record.data["metadata"]
    assert (
        updated_record.data["revision_id"]
        == updated_record_read.data["revision_id"]
        == old_record_data["revision_id"] + 1
    )


def test_delete(app, db, sample_record, search_clear):
    with pytest.raises(PIDDoesNotExistError):
        current_service.delete(system_identity, "fwsegerhjtyuk754dh")

    to_delete_record = current_service.read(system_identity, sample_record["id"])
    assert to_delete_record
    current_service.delete(system_identity, sample_record["id"])
    with pytest.raises(PIDDeletedError):
        current_service.read(system_identity, sample_record["id"])


def test_search(app, db, sample_records, sample_metadata_list, search_clear):
    sample_record = sample_records[0]

    res_one = list(
        current_service.search(system_identity, params={"q": "fish attack painting"})
    )
    res_fail = list(current_service.search(system_identity, params={"q": "wefrtghthy"}))
    res_created = list(
        current_service.search(
            system_identity, params={"q": str(datetime.datetime.now().date())}
        )
    )

    res_created_fail = list(
        current_service.search(system_identity, params={"q": "2022-10-16"})
    )
    res_facets = list(
        current_service.scan(
            system_identity,
            params={
                "facets": {
                    "created": [pytz.utc.localize(sample_record.created).isoformat()]
                }
            },
        ).hits
    )

    res_listing = list(current_service.search(system_identity))

    assert len(res_fail) == 0
    assert len(res_listing) == 25
    assert len(res_one) == 1
    assert len(res_created) == 25
    assert len(res_created_fail) == 0
    assert len(res_facets) == 1
