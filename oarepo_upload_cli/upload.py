import arrow
import click
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import os
from tqdm import tqdm

from oarepo_upload_cli.token_auth import BearerAuthentication
from oarepo_upload_cli.entry_points_loader import EntryPointsLoaderConfig, EntryPointsLoader
from oarepo_upload_cli.repository_data_extractor import RepositoryDataExtractor

@dataclass
class MetadataConfig:
    file_modified_field_name: str
    record_modified_field_name: str

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--source', help="Record source entry point path.")
@click.option('--repo_handler', help="Custom repository records handler.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('--token', help="SIS bearer authentication token.")
def main(collection_url, source, repo_handler, modified_after, modified_before, token) -> None:
    # -------------------------
    # - Environment variables -
    # -------------------------
    try:
        load_dotenv(find_dotenv(usecwd=True))
    except IOError as e:
        print(e)
        
        return

    # --------------------------
    # - Metadata configuration -
    # --------------------------
    metadata_config = MetadataConfig(
        file_modified_field_name=os.getenv('FILE_MODIFIED_FIELD_NAME', 'dateModified'),
        record_modified_field_name=os.getenv('RECORD_MODIFIED_FIELD_NAME', 'dateModified')
    )

    # ---------------------------
    # - Authentication (Bearer) -
    # ---------------------------
    bearer_token = token or os.getenv('BEARER_TOKEN')
    if not bearer_token:
        print('Bearer token is missing.')
        
        return

    auth = BearerAuthentication(bearer_token)

    # ----------------
    # - Entry points -
    # ----------------
    ep_config = EntryPointsLoaderConfig(
        group=os.getenv('ENTRY_POINTS_GROUP', 'oarepo_upload_cli.dependencies'),
        source=os.getenv('ENTRY_POINTS_SOURCE', 'source'),
        repo_handler=os.getenv('ENTRY_POINTS_REPO_HANDLER', 'repo_handler')        
    )
        
    ep_loader = EntryPointsLoader(config=ep_config)
    source = ep_loader.load_entry_point(config_value=ep_config.source, arg=source)()
    repo_handler = ep_loader.load_entry_point(config_value=ep_config.repo_handler, arg=repo_handler)(collection_url, auth)

    # --------------
    # - Timestamps -
    # --------------
    if not modified_before:
        # set modified before to current datetime
        modified_before = datetime.utcnow()
    else:
        modified_before = arrow.get(modified_before).datetime.replace(tzinfo=None)
    
    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(collection_url, auth)
        modified_after = repo_data_extractor.get_data(path=['aggregations', 'max_date', 'value'])
    
    modified_after = arrow.get(modified_after).datetime.replace(tzinfo=None)

    # ----------
    # - Upload -
    # ----------
    approximate_records_count = source.get_records_count(modified_after, modified_before)
    if not approximate_records_count:
        print(f'All records are up to the given date: {modified_after}')
        
        return

    source_records = tqdm(source.get_records(modified_after, modified_before), total=approximate_records_count, disable=None)
    for source_record in source_records:
        # Get the repository version of this record.
        repository_record = repo_handler.get_record(source_record)
        if not repository_record:
            repository_record = repo_handler.create_record(source_record)
        else:
            # Check for the update of record's metadata.
            last_metadata_modification = datetime.fromisoformat(repository_record['metadata'][metadata_config.record_modified_field_name])
            if modified_after < last_metadata_modification <= modified_before:
                repo_handler.update_metadata(source_record)
        
        # ---------
        # - Files -
        # ---------
        source_record_files = source_record.files
        repository_records_files = repo_handler.get_records_files(source_record)
        
        source_files_keys = {file.key for file in source_record_files}
        repository_files_keys = {file['key'] for file in repository_records_files}
        
        # Find identical files keys in both sources, update them.
        for key in source_files_keys.intersection(repository_files_keys):
            source_file = [file for file in source_record_files if file.key == key][0]
            repository_file = [file for file in repository_records_files if file['key'] == key][0]
            
            last_repository_modification = datetime.fromisoformat(repository_file[metadata_config.file_modified_field_name])
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