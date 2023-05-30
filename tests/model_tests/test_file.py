import io
import mimetypes
import unicodedata

from oarepo_upload_cli.abstract_file import AbstractFile


class TestFile(AbstractFile):
    def __init__(self, sis_file_metadata, zakladni_metadata):
        key = (
            sis_file_metadata['FTYP'].lower() + '-' +
            str(zakladni_metadata['ID_PRACE']) + '-' +
            remove_accents(zakladni_metadata['PRIJMENI_STUDENTA']).lower() + '-' +
            remove_accents(zakladni_metadata['JMENO_STUDENTA']).lower() + '.' +
            sis_file_metadata['FNAZEV'].split('.')[-1]
        )
        super().__init__(key)
        self._content_type = mimetypes.MimeTypes().guess_type(
            sis_file_metadata['FNAZEV'])[0]
        self._modified = sis_file_metadata['FDT'].isoformat()
        self._reader = io.BytesIO(b'something here')

    def content_type(self):
        return self._content_type

    def modified(self):
        return self._modified

    def get_reader(self):
        return self._reader


def remove_accents(x):
    nfkd_form = unicodedata.normalize('NFKD', x)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
