from invenio_db import db
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records import FileRecordModelMixin

from uct_theses.records.models import UctThesesMetadata


class UctThesesFileMetadata(db.Model, FileRecordModelMixin, RecordMetadataBase):
    """Model for UctThesesFileRecord metadata."""

    __tablename__ = "uctthesesfile_metadata"

    # Enables SQLAlchemy-Continuum versioning
    __versioned__ = {}
    __record_model_cls__ = UctThesesMetadata
