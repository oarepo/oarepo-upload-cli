
import pytest
from invenio_records_resources.resources import FileResource

from uct_theses.resources.files.config import UctThesesFileResourceConfig
from uct_theses.services.files.config import UctThesesFileServiceConfig
from uct_theses.services.files.service import UctThesesFileService


@pytest.fixture(scope="module")
def file_service():
    """File service shared fixture."""
    service = UctThesesFileService(UctThesesFileServiceConfig())
    return service


@pytest.fixture(scope="module")
def file_resource(file_service):
    """File Resources."""
    return FileResource(UctThesesFileResourceConfig(), file_service)


@pytest.fixture(scope="module")
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


@pytest.fixture(scope="module")
def app_config(app_config):
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    return app_config
