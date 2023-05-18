from datetime import datetime

import click
from dotenv import load_dotenv
import os
from tqdm import tqdm

from oarepo_upload_cli.authentication_token_parser import AuthenticationTokenParser, AuthenticationTokenParserConfig
from oarepo_upload_cli.repository_data_extractor import RepositoryDataExtractor
from oarepo_upload_cli.repository_records_handler import RepositoryRecordsHandler
from oarepo_upload_cli.entry_points_loader import EntryPointsLoaderConfig, EntryPointsLoader

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--record_path', help="Record entry point path.")
@click.option('--source_path', help="Record source entry point path.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('--token', help="SIS bearer authentication token.")
def main(collection_url, record_path, source_path, modified_after, modified_before, token) -> None:
    # -------------------------
    # - Environment variables -
    # -------------------------
    try:
        # Ensure that environment variables are present and loaded.
        load_dotenv()
    except IOError as e:
        print(e)
        
        return

    # ---------------------------
    # - Authentication (Bearer) -
    # ---------------------------
    token_parser_config = AuthenticationTokenParserConfig(
        ini_group=os.getenv('AUTHENTICATION_INI_GROUP'),
        ini_token=os.getenv('AUTHENTICATION_INI_TOKEN'),
        ini_file_name=os.getenv('AUTHENTICATION_INI_FILE')
    )
    token_parser = AuthenticationTokenParser(token_parser_config, token)
    if not(token := token_parser.get_token()):
        print('Bearer token is missing.')
        
        return

    # ----------------
    # - Entry points -
    # ----------------
    ep_config = EntryPointsLoaderConfig(
        group=os.getenv('ENTRY_POINTS_GROUP', 'oarepo_upload_cli'),
        record_source_name=os.getenv('ENTRY_POINTS_RECORD_NAME'),
        record_name=os.getenv('ENTRY_POINTS_RECORD_SOURCE_NAME')
    )
    ep_loader = EntryPointsLoader(config=ep_config)
    record = ep_loader.load_abstract_record(record_arg_name=record_path)
    source = ep_loader.load_abstract_record_source(source_name_arg=source_path)

    # --------------
    # - Timestamps -
    # --------------
    if not modified_before:
        # set modified before to current datetime
        modified_before = datetime.utcnow().isoformat()

    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(collection_url, token)
        modified_after = repo_data_extractor.get_data(path=["aggregations", "max_date", "value"])

    approximate_records_count = source.get_records_count(modified_after, modified_before)
    if not approximate_records_count:
        print(f'All records are up to the given date: {modified_after}')
        return

    handler = RepositoryRecordsHandler(collection_url)
    records = tqdm(source.get_records(modified_after, modified_before), total=approximate_records_count, disable=None)
    for rec in records:
        handler.upload_record(rec)

if __name__ == "__main__":
    main()