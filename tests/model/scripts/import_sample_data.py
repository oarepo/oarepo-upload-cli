import argparse
import sys
from pathlib import Path

import yaml
from invenio_access.permissions import system_identity
from invenio_app.factory import create_api

from model.proxies import current_service


def cli():
    parser = argparse.ArgumentParser(description="Imports data from yaml file")
    parser.add_argument("filename", help="Filename to import the data from", nargs="?")

    args = parser.parse_args()

    if args.filename:
        filename = args.filename
    else:
        filename = Path(sys.argv[0]).parent / "sample_data.yaml"

    api = create_api()

    with api.app_context():
        with open(filename) as f:
            for doc in yaml.load_all(f, yaml.SafeLoader):
                current_service.create(system_identity, doc)


if __name__ == "__main__":
    cli()
