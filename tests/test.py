from invenio_access.permissions import system_identity
from invenio_app.factory import create_api

from model.model.proxies import current_service

from test_source import TestSource

api = create_api()

def upload_random_records(update_after_timestamp: str, size: int):
    test_source = TestSource(size)
    with api.app_context():
        for record in test_source.get_records(update_after_timestamp):
            # checknut es index
            current_service.create(system_identity, record.get_metadata())


def clear():
    """
    Removes records from invenio.
    """
    pass