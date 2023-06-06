from typing import List

from oarepo_upload_cli.abstract_file import AbstractFile
from oarepo_upload_cli.abstract_metadata import AbstractMetadata
from oarepo_upload_cli.abstract_record import AbstractRecord
from .file import TestFile
from .metadata import TestMetadata

class TestRecord(AbstractRecord):
    def __init__(self, timestamp, zakladni_metadata, lide, soubory, anotace):
        super().__init__(timestamp, zakladni_metadata['ID_PRACE'])
        self._metadata = TestMetadata(zakladni_metadata, lide, anotace)
        self._files = []

        for soubor in soubory:
            self.files.append(TestFile(soubor, zakladni_metadata))

    @property
    def metadata(self) -> AbstractMetadata:
        return self._metadata

    @property
    def files(self) -> List[AbstractFile]:
        return self._files