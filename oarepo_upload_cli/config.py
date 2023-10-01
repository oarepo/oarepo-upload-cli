import configparser
import os

from oarepo_upload_cli.auth.bearer_auth import BearerAuthentication


class Config:
    def __init__(self, init_file_path=None, *overrides):
        config = configparser.ConfigParser()
        if init_file_path and os.path.exists(init_file_path):
            config.read(init_file_path)

        for section in ("authentication", "repository", "entrypoints"):
            if not config.has_section(section):
                config.add_section(section)

        self.config = config
        for override in overrides:
            self.override(*override)

    @property
    def auth(self):
        return BearerAuthentication(self.bearer_token)

    @property
    def bearer_token(self):
        return self.ensure_defined(
            "authentication", "token", "REPOSITORY_UPLOADER_BEARER_TOKEN"
        )

    @property
    def collection_url(self):
        return self.ensure_defined(
            "repository", "collection_url", "REPOSITORY_UPLOADER_COLLECTION_URL"
        )

    @property
    def file_modified_field_name(self):
        return (
            self.config["repository"].get("file_modified_field")
            or os.getenv("REPOSITORY_UPLOADER_FILE_MODIFIED_FIELD_NAME")
            or "metadata.dateModified"
        )

    @property
    def record_modified_field_name(self):
        return (
            self.config["repository"].get("record_modified_field")
            or os.getenv("REPOSITORY_UPLOADER_RECORD_MODIFIED_FIELD_NAME")
            or "metadata.dateModified"
        )

    @property
    def source_name(self):
        return self.ensure_defined(
            "entrypoints", "source", "REPOSITORY_UPLOADER_SOURCE"
        )

    @property
    def repository_name(self):
        return (
            self.config["entrypoints"].get("repository")
            or os.getenv("REPOSITORY_UPLOADER_REPOSITORY")
            or "invenio"
        )

    @property
    def repository_id_query_field(self):
        return (
            self.config["repository"].get("id_query_field")
            or os.getenv("REPOSITORY_UPLOADER_ID_QUERY_FIELD")
            or "metadata.originalId"
        )

    @property
    def repository_last_modification_date_agg(self):
        return self.config["repository"].get("last_modification_date_agg") or os.getenv(
            "REPOSITORY_UPLOADER_LAST_MODIFICATION_DATE_AGG"
        )

    def override(self, section, option, value):
        if value:
            self.config[section][option] = value

    def ensure_defined(self, section, config_key, os_environ_key):
        ret = self.config[section].get(config_key) or os.getenv(os_environ_key)
        if not ret:
            raise Exception(
                f"Please supply {config_key} to init file or set {os_environ_key} environment variable"
            )
        return ret
