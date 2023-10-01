from typing import Dict, List, Union
from datetime import datetime

JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]


def dict_get(d, path):
    path = path.split(".")
    for p in path:
        d = d[p]
    return d


def parse_modified(metadata, modified_field_name):
    return datetime.fromisoformat(dict_get(metadata, modified_field_name))