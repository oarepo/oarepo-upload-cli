from oarepo_upload_cli.abstract_record import AbstractRecord

class TestRecord(AbstractRecord):
    def __init__(self, updated: str):
        self.updated = updated

    def get_metadata(self):
        return { "updated": self.updated }

    def id(self):
        return super().id