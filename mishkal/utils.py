import re
from mishkal import config
from .chars_set import get_chars_set

def remove_niqqud(text: str):
    return re.sub(config.HE_NIQQUD_PATTERN, '', text)

def has_niqqud(text: str):
    return re.search(config.HE_NIQQUD_PATTERN, text) is not None

def is_phonemized(text: str):
    chars_set = get_chars_set()
    return all(i in chars_set for i in text)