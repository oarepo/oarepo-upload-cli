from oarepo_upload_cli.abstract_record import AbstractRecord

class TestRecord(AbstractRecord):
    def __init__(self, updated: str, id: str = None):
        self._updated = updated
        self._id = id

    def get_metadata(self):
        return { "updated": self._updated }

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value