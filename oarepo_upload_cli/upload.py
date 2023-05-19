import click
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
import os
from tqdm import tqdm

from oarepo_upload_cli.authentication_token_parser import AuthenticationTokenParser, AuthenticationTokenParserConfig
from oarepo_upload_cli.token_auth import BearerAuthentication
from oarepo_upload_cli.entry_points_loader import EntryPointsLoaderConfig, EntryPointsLoader
from oarepo_upload_cli.repository_data_extractor import RepositoryDataExtractor
from oarepo_upload_cli.repository_records_handler import RepositoryRecordsHandler, RepositoryRecordsHandlerConfig

@dataclass
class MetadataConfig:
    modified_name: str

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--source', help="Record source entry point path.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('--token', help="SIS bearer authentication token.")
def main(collection_url, source, modified_after, modified_before, token) -> None:
    # -------------------------
    # - Environment variables -
    # -------------------------
    try:
        load_dotenv()
    except IOError as e:
        print(e)
        
        return

    # ---------------------------
    # - Authentication (Bearer) -
    # ---------------------------
    token_parser_config = AuthenticationTokenParserConfig(
        ini_group=os.getenv('AUTHENTICATION_INI_GROUP', 'authentication'),
        ini_token=os.getenv('AUTHENTICATION_INI_TOKEN', 'token'),
        ini_file_name=os.getenv('AUTHENTICATION_INI_FILE', 'oarepo_upload.ini')
    )
    token_parser = AuthenticationTokenParser(token_parser_config, token)
    if not(token := token_parser.get_token()):
        print('Bearer token is missing.')
        
        return

    auth = BearerAuthentication(token)

    # ----------------
    # - Entry points -
    # ----------------
    ep_config = EntryPointsLoaderConfig(
        group=os.getenv('ENTRY_POINTS_GROUP', 'oarepo_upload_cli.dependencies'),
        source=os.getenv('ENTRY_POINTS_SOURCE', 'source'),
    )
    ep_loader = EntryPointsLoader(config=ep_config)
    source = ep_loader.load_abstract_record_source(source_arg=source)

    # --------------
    # - Timestamps -
    # --------------
    if not modified_before:
        # set modified before to current datetime
        modified_before = datetime.utcnow() #.isoformat()
    else:
        modified_before = datetime.fromtimestamp(modified_before)
    
    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(collection_url, auth)
        modified_after = repo_data_extractor.get_data(path=['aggregations', 'max_date', 'value'])
    
    modified_after = datetime.fromtimestamp(modified_after)

    # ----------
    # - Upload -
    # ----------
    approximate_records_count = source.get_records_count(modified_after, modified_before)
    if not approximate_records_count:
        print(f'All records are up to the given date: {modified_after}')
        
        return

    metadata_config = MetadataConfig(
        modified_name=os.getenv('RECORD_METADATA_MODIFIED', 'dateModified')
    )
    repo_handler = RepositoryRecordsHandler(metadata_config, collection_url, auth)
    source_records = tqdm(source.get_records(modified_after, modified_before), total=approximate_records_count, disable=None)
    for source_record in source_records:
        # Get the repository version of this record.
        repository_record = repo_handler.get_record(source_record)
        
        # ------------
        # - Metadata -
        # ------------
        last_metadata_modification = datetime.fromisoformat(repository_record['metadata'][metadata_config.modified_name])
        if modified_after < last_metadata_modification <= modified_before:
            # Metadata was updated, upload the new version.
            
            repo_handler.upload_metadata(source_record)
        
        # ---------
        # - Files -
        # ---------
        source_record_files = source_record.files
        repository_records_files = repo_handler.get_records_files(source_record)
        
        # Find identical files keys in both sources, update them.
        source_files_keys = {file.key for file in source_record_files}
        repository_files_keys = {file['key'] for file in repository_records_files}
        for key in source_files_keys.intersection(repository_files_keys):
            source_file = [file for file in source_record_files if file.key == key][0]
            repository_file = [file for file in repository_records_files if file['key'] == key][0]
            
            last_repository_modification = datetime.fromisoformat(repository_file[metadata_config.modified_name])
            if last_repository_modification < source_file.modified:
                # Source's is newer, update.
                repo_handler.upload_file(source_record, source_file)
                
        # Find files that are in source but not yet in repo, upload them.
        for key in source_files_keys.difference(repository_files_keys):
            source_file = [file for file in source_record_files if file.key == key][0]
            repo_handler.upload_file(source_record, source_file)
        
        # Delete files that are in repo and not in source.
        for key in repository_files_keys.difference(source_files_keys):
            repository_file = [file for file in repository_records_files if file.key == key][0]
            repo_handler.delete_file(source_record, source_file)            

if __name__ == "__main__":
    main()