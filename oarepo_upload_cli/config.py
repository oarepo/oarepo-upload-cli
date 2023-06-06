import os

from oarepo_upload_cli.auth.bearer_auth import BearerAuthentication

class Config:
    def __init__(self, bearer_token_arg: str=None, collection_url_arg: str=None):
        self._bearer_token = bearer_token_arg
        self._collection_url = collection_url_arg
    
    @property
    def bearer_token(self):
        token = self._bearer_token or os.getenv('BEARER_TOKEN')
    
        return BearerAuthentication(token)
    
    @property
    def collection_url(self):
        url = self._collection_url or os.getenv('COLLECTION_URL')
        if not url.endswith('/'):
            url += '/'
            
        return url
    
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