import os

class Config:
    def __init__(self, bearer_token_arg: str=None):
        self._bearer_token = bearer_token_arg
    
    @property
    def bearer_token(self):
        return self._bearer_token or os.getenv('BEARER_TOKEN')
    
    @property
    def entry_points_group(self):
        return os.getenv('ENTRY_POINTS_GROUP', 'oarepo_upload_cli.dependencies')
    
    @property
    def entry_points_repo_handler(self):
        return os.getenv('ENTRY_POINTS_REPO_HANDLER', 'repo_handler')
    
    @property
    def entry_points_source(self):
        return os.getenv('ENTRY_POINTS_SOURCE', 'source')
    
    @property
    def file_modified_field_name(self):
        return os.getenv('FILE_MODIFIED_FIELD_NAME', 'dateModified')
    
    @property
    def record_modified_field_name(self):
        return os.getenv('RECORD_MODIFIED_FIELD_NAME', 'dateModified')