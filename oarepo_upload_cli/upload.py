import click
from tqdm import tqdm

from authentication_token_parser import AuthenticationTokenParser
from repository_data_extractor import RepositoryDataExtractor
from repository_records_handler import RepositoryRecordsHandler
from entry_points_loader import EntryPointsLoader

@click.command()
@click.option('--collection_url', help="Concrete collection URL address to synchronize records.")
@click.option('--source', help="Abstract record source entry point name.")
@click.option('--modified_after', help="Timestamp that represents date after modification. If not specified, the last updated timestamp from repository will be used.")
@click.option('--modified_before', help="Timestamp that represents date before modification.")
@click.option('-t', '--token', help="SIS bearer authentication token.")
def main(collection_url, source, modified_after, modified_before, token) -> None:
    token_parser = AuthenticationTokenParser(token)
    token = token_parser.parse()
    if not token:
        print('Token is missing.')
        return

    if not modified_after:
        repo_data_extractor = RepositoryDataExtractor(collection_url, token)
        modified_after = repo_data_extractor.get_data(path=["aggregations", "max_date", "value"])

    ep_loader = EntryPointsLoader()
    source = ep_loader.load_abstract_record_source(source_name_arg=source)

    approximate_records_count = source.get_records_count(modified_after, modified_before)
    if not approximate_records_count:
        print(f'All records are up to the given date: {modified_after}')
        return

    handler = RepositoryRecordsHandler(collection_url)
    records = tqdm(source.get_records(modified_after, modified_before), total=approximate_records_count, disable=None)
    for record in records:
        handler.upload_record(record)

if __name__ == "__main__":
    main()