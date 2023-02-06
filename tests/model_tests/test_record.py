from oarepo_upload_cli.abstract_record import AbstractRecord

class TestRecord(AbstractRecord):
    # prevent pytest from trying to discover tests in the class
    __test__ = False

    def __init__(self, updated: str, id: str = None):
        self._updated = updated
        self._id = id

    def get_metadata(self):
        return { "metadata": { "updated": self._updated } }

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value