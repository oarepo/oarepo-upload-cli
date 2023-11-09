from datetime import datetime
from typing import Dict, List, Union

JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]


def dict_get(d, path):
    path = path.split(".")
    for p in path:
        d = d[p]
        if d is None:
            break
    return d


def parse_modified(metadata, modified_field_name):
    text = dict_get(metadata, modified_field_name)
    if text:
        return datetime.fromisoformat(text)
    return None


def noop(*args, **kwargs):
    pass
