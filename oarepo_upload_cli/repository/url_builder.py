class RepositoryURLBuilder:
    """
    Constructs and provides URLs for a repository handling needs.
    """
    
    def __init__(self, collection_url: str):
        if not collection_url.endswith('/'):
            collection_url += '/'

        self._collection_url = collection_url

    def record(self, record_self_link: str):
        return f'{self._collection_url}{record_self_link}'

    def record_files(self, record_files_link: str):
        return f'{self._collection_url}{record_files_link}'

    def file(self, record_files_link, file_key):
        return f'{self._collection_url}{record_files_link}/{file_key}'

    def file_content(self, record_files_link: str, file_key: str):
        return f'{self.file(record_files_link, file_key)}/content'

    def file_commit(self, record_files_link: str, file_key: str):
        return f'{self.file(record_files_link, file_key)}/commit'