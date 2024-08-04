import string
import random
from typing import List


def random_alias_string(length: int, exclude_list: List[str]) -> str:
    while True:
        alias = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=length)
        )
        if alias not in exclude_list:
            return alias
