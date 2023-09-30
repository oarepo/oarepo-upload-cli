import os

from oarepo_upload_cli.auth.bearer_auth import BearerAuthentication
import configparser
import importlib


class Config:
    def __init__(self, init_file_path):
        config = configparser.ConfigParser()
        if os.path.exists(init_file_path):
            config.read_file(init_file_path)
        try:
            self.cfg = config["options"]
        except:
            self.cfg = {}

    @property
    def auth(self):
        return BearerAuthentication(self.bearer_token)

    @property
    def bearer_token(self):
        return self.ensure_defined("options", "REPOSITORY_UPLOADER_BEARER_TOKEN")

    @property
    def collection_url(self):
        return self.ensure_defined(
            "collection_url", "REPOSITORY_UPLOADER_COLLECTION_URL"
        )

    def ensure_defined(self, config_key, os_environ_key):
        ret = self.cfg.get(config_key) or os.getenv(os_environ_key)
        if not ret:
            raise Exception(
                f"Please supply {config_key} to init file or set {os_environ_key} environment variable"
            )
        return ret

    @property
    def file_modified_field_name(self):
        return (
            self.cfg.get("file_modified_field")
            or os.getenv("REPOSITORY_UPLOADER_FILE_MODIFIED_FIELD_NAME")
            or "dateModified"
        )

    @property
    def record_modified_field_name(self):
        return (
            self.cfg.get("record_modified_field")
            or os.getenv("REPOSITORY_UPLOADER_RECORD_MODIFIED_FIELD_NAME")
            or "dateModified"
        )

    @property
    def source_name(self):
        return self.ensure_defined("source", "REPOSITORY_UPLOADER_SOURCE")

    @property
    def repository_name(self):
        return self.ensure_defined("repository", "REPOSITORY_UPLOADER_REPOSITORY")
