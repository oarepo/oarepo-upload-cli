import click
from tqdm import tqdm

from authentication_token_parser import AuthenticationTokenParser
from repository_data_extractor import RepositoryDataExtractor
from repository_records_handler import RepositoryRecordsHandler
from entry_points_loader import EntryPointsLoader

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--record_path', help="Record entry point path.")
@click.option('--source_path', help="Record source entry point path.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('--token', help="SIS bearer authentication token.")
def main(collection_url, record_path, source_path, modified_after, modified_before, token) -> None:
    token_parser = AuthenticationTokenParser(token)
    token = token_parser.parse()
    if not token:
        print('Token is missing.')
        return

    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(collection_url, token)
        modified_after = repo_data_extractor.get_data(path=["aggregations", "max_date", "value"])

    ep_loader = EntryPointsLoader()
    record = ep_loader.load_abstract_record(record_arg_name=record_path)
    source = ep_loader.load_abstract_record_source(source_name_arg=source_path)

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