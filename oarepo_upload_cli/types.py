from typing import Union, List, Dict

JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]
