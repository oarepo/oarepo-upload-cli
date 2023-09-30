from typing import Dict, List, Union

JsonType = Union[None, int, str, bool, List["JsonType"], Dict[str, "JsonType"]]
