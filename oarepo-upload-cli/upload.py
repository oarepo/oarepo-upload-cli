import argparse
import pkg_resources
from repository_data_extractor import RepositoryDataExtractor

def main(args: argparse.Namespace) -> None:
    repo_data_extractor = RepositoryDataExtractor(args.repository_url)
    max_date = repo_data_extractor.get_data(["aggregations", "max_date", "value"])
    print(max_date)

def init_args_parser():
    """
    Initialize a parser of scripts arguments.

    Parser accepts two arguments:
    - repository url string
    - date to check against the last uploaded repository document
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--repo_url", type=str, help="Repository URL address to upload new documents to.")
    parser.add_argument("--date", type=str, help="Date to compare already uploaded repository items to.")
    parser.add_argument("--token", type=str, help="SIS authentication token.")
    
    return parser

if __name__ == "__main__":
    parser = init_args_parser()
    args = parser.parse_args([] if "__file__" not in globals() else None)

    main(args)