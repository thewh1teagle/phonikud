from mishkal import lexicon
import unicodedata
import regex as re


def sort_diacritics(match):
    letter = match.group(1)
    diacritics = "".join(sorted(match.group(2)))  # Sort diacritics
    return letter + diacritics


NORMALIZE_PATTERNS = {
    # Alphabet followed by 1/2 symbols then dagesh. make dagesh first
    r"(\p{L})(\p{M}+)": sort_diacritics,
    "״": '"',
    "׳": "'",
}


def remove_niqqud(text: str):
    return re.sub(lexicon.HE_NIQQUD_PATTERN, "", text)


def has_niqqud(text: str):
    return re.search(lexicon.HE_NIQQUD_PATTERN, text) is not None


def normalize(text: str) -> str:
    """
    Normalize unicode (decomposite)
    Deduplicate niqqud (eg. only Patah instead of Kamatz)
    Keep only Hebrew characters / punctuation / IPA
    Sort diacritics
    """

    # Decompose text
    text = unicodedata.normalize("NFD", text)
    for k, v in NORMALIZE_PATTERNS.items():
        text = re.sub(k, v, text)
    # Normalize niqqud, remove duplicate phonetics 'sounds' (eg. only Patah)
    for k, v in lexicon.NIQQUD_DEDUPLICATE.items():
        text = text.replace(k, v)
    return text


def post_normalize(phonemes: str):
    new_phonemes = []
    for word in phonemes.split(" "):
        # remove glottal stop from end
        word = re.sub(r"ʔ$", "", word)
        # remove h from end
        word = re.sub(r"h$", "", word)
        word = re.sub(r"ˈh$", "ˈ", word)
        # remove j followed by a i
        word = re.sub(r"ij", "i", word)
        new_phonemes.append(word)
    return " ".join(new_phonemes)


def get_unicode_names(text: str):
    return [unicodedata.name(c, "?") for c in text]

def has_vowel(s: iter):
    return any(i in s for i in 'aeiou')

def has_constant(s: iter):
    return any(i not in 'aeiou' for i in s)

