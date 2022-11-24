import argparse

from repository_data_extractor import RepositoryDataExtractor
from entry_points_loader import EntryPointsLoader

def main(args: argparse.Namespace) -> None:
    repo_data_extractor = RepositoryDataExtractor(args.repository_url)
    max_date = repo_data_extractor.get_data(["aggregations", "max_date", "value"])
    
    ep_loader = EntryPointsLoader()
    abstract_record = ep_loader.load_abstract_record(args.abstract_record)
    abstract_record_source = ep_loader.load_abstract_record_source(args.abstract_record_source)

    # TODO:
    # - load records from source
    # - get metadata from loaded records
    # - send put request if max date is older than current

def init_args_parser():
    """
    Initialize a parser of scripts arguments.

    Parser accepts several arguments:
    - repository url string
    - date to check against the last uploaded repository document
    - authentication token
    - entry points names of abstract record and abstract record source
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--repo_url", type=str, help="Repository URL address to upload new documents to.")
    parser.add_argument("--date", type=str, help="Date to compare already uploaded repository items to.")
    parser.add_argument("--token", type=str, help="SIS authentication token.")
    parser.add_argument("--abstract_record", type=str, help="Abstract record source entry point name.")
    parser.add_argument("--abstract_record_source", type=str, help="Abstract record source entry point name.")
    
    return parser

if __name__ == "__main__":
    parser = init_args_parser()
    args = parser.parse_args([] if "__file__" not in globals() else None)

    main(args)