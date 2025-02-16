import re
from mishkal import config
from .chars_set import pretty_chars_set

def remove_niqqud(text: str):
    return re.sub(config.HE_NIQQUD_PATTERN, '', text)

def has_niqqud(text: str):
    return re.search(config.HE_NIQQUD_PATTERN, text) is not None

def is_only_phonemes(text: str):
    phoneme_set = pretty_chars_set()
    return all(i in phoneme_set for i in text)