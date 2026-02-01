import re

def is_valid_bm(text: str) -> bool:
    return bool(re.fullmatch(r"\d+(\.\d+)?", text))
