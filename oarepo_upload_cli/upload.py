import arrow
import click
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm

from oarepo_upload_cli.config import Config
from oarepo_upload_cli.entry_points_loader import EntryPointsLoader
from oarepo_upload_cli.base.abstract_file import FileStatus
from oarepo_upload_cli.repository_data_extractor import RepositoryDataExtractor

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--config_name', help="Configuration entry point path.")
@click.option('--source_name', help="Record source entry point path.")
@click.option('--repo_handler_name', help="Custom repository records handler.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('--bearer_token', help="SIS bearer authentication token.")
def main(collection_url, config_name, source_name, repo_handler_name, modified_after, modified_before, bearer_token) -> None:
    # -------------------------
    # - Environment variables -
    # -------------------------
    try:
        load_dotenv(find_dotenv(usecwd=True))
    except IOError as e:
        print(e)
        
        return

    # -----------------
    # - Configuration -
    # -----------------
    ep_loader = EntryPointsLoader()
    
    default_config = Config(bearer_token, collection_url, repo_handler_name, source_name)
    config = ep_loader.load_entry_point(config_name, default=default_config)(bearer_token, collection_url, repo_handler_name, source_name)
    
    # ----------------
    # - Entry points -
    # ----------------
    source = ep_loader.load_entry_point(config.entry_points_source)(config)    
    repo_handler = ep_loader.load_entry_point(config.entry_points_repo_handler)(config)
    
    # --------------
    # - Timestamps -
    # --------------
    if not modified_before:
        # set modified_before to current datetime
        modified_before = datetime.utcnow()
    else:
        modified_before = arrow.get(modified_before).datetime.replace(tzinfo=None)
    
    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(config)
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
        
        if source_record.deleted:
            # Marked to delete.
            
            if repository_record:
                repo_handler.delete_record(repository_record['links']['self'])
            
            continue
        
        if not repository_record:
            repository_record = repo_handler.create_record(source_record)
        else:
            # Check for the update of record's metadata.
            last_metadata_modification = datetime.fromisoformat(repository_record['metadata'][config.record_modified_field_name])
            if modified_after < last_metadata_modification <= modified_before:
                repo_handler.update_metadata(repository_record['links']['self'], source_record.metadata)
        
        # ---------
        # - Files -
        # ---------
        source_record_files = source_record.files
        repository_records_files = repo_handler.get_records_files(repository_record['links']['files'])
        
        source_files_keys = {file.key for file in source_record_files}
        repository_files_keys = {file['key'] for file in repository_records_files}
        
        # Find identical files keys in both sources, update them.
        for key in source_files_keys.intersection(repository_files_keys):
            source_file = [file for file in source_record_files if file.key == key][0]
            repository_file = [file for file in repository_records_files if file['key'] == key][0]
            
            last_repository_modification = datetime.fromisoformat(repository_file['metadata'][config.file_modified_field_name])
            if last_repository_modification < source_file.modified or repository_file['status'] == FileStatus.PENDING.value:
                # Source's is newer, update.
                repo_handler.update_file(repository_record['links']['files'], source_file)
        
        # Find files that are in source but not yet in repo, upload them.
        for key in source_files_keys.difference(repository_files_keys):
            source_file = [file for file in source_record_files if file.key == key][0]
            repo_handler.create_file(repository_record['links']['files'], source_file)
        
        # Delete files that are in repo and not in source.
        for key in repository_files_keys.difference(source_files_keys):
            repository_file = [file for file in repository_records_files if file.key == key][0]
            repo_handler.delete_file(repository_record['links']['files'], source_file)            

if __name__ == "__main__":
    main()