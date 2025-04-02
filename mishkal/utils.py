from mishkal import vocab
import unicodedata
import regex as re

def sort_diacritics(match):
    letter = match.group(1)
    diacritics = "".join(sorted(match.group(2)))  # Sort diacritics
    return letter + diacritics

NORMALIZE_PATTERNS = {
    # Alphabet followed by 1/2 symbols then dagesh. make dagesh first
    r"(\p{L})(\p{M}+)": sort_diacritics,
    r"([^בכךפףו])(\u05bc)": r"\1",
}


def remove_niqqud(text: str):
    return re.sub(vocab.HE_NIQQUD_PATTERN, "", text)


def has_niqqud(text: str):
    return re.search(vocab.HE_NIQQUD_PATTERN, text) is not None


def normalize(text: str) -> str:
    """
    Normalize unicode (decomposite)
    Deduplicate niqqud (eg. only Patah instead of Kamatz)
    Keep only Hebrew characters / punctuation / IPA
    """
    # Decompose text
    text = unicodedata.normalize("NFD", text)
    for k, v in NORMALIZE_PATTERNS.items():
        text = re.sub(k, v, text)
    # Normalize niqqud, remove duplicate phonetics 'sounds' (eg. only Patah)
    for k, v in vocab.NIQQUD_DEDUPLICATE.items():
        text = text.replace(k, v)
    return text

def post_normalize(phonemes: str):
    phonemes = re.sub(r'^h|h$', '', phonemes)
    return phonemes

def get_unicode_names(text: str):
    return [unicodedata.name(c, "?") for c in text]
