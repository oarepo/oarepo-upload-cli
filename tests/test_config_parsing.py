from pathlib import Path

from oarepo_upload_cli.config import Config


def test_parse_ini():
    """
    Tests correct parsing of a token written in an ini file located in the current directory.
    """
    config = Config(Path(__file__).parent / "oarepo_upload.ini")

    assert config.file_modified_field_name == "myFileModified"
    assert config.record_modified_field_name == "myRecordModified"

    assert config.source_name == "mySource"
    assert config.repository_name == "myRepo"
    assert config.collection_url == "myCollection"
    assert config.bearer_token == "myBearer"
