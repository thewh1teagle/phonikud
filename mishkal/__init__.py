"""
High level phonemize functions
"""

import unicodedata

from mishkal.word import extract_letters
from mishkal.phonemize import phonemize_letters
from mishkal.variants import Word
from mishkal.expander import Expander
from mishkal.phoneme_table import get_phoneme_set # noqa: F401

expander = Expander()

def normalize(text: str) -> str:
    return unicodedata.normalize('NFD', text)

def phonemize(text: str, debug = False) -> str | list[Word]:
    """
    1. Normalize text
    2. Expand words with expander and dictionary
    3. Iterate lines
    4. Iterate words
    5. Phonemize each word
    """
    text = normalize(text)
    
    if not text:
        return [] if debug else ''
    
    phonemized: list[Word] = []
    
    for line in text.splitlines():
        line = expander.expand_text(line)
        for word in line.split():
            letters = extract_letters(word)
            phonemes = phonemize_letters(letters)
            phonemized_word = Word(word, phonemes)
            phonemized.append(phonemized_word)
    if debug:
        return phonemized
    return ' '.join(w.as_phonemes_str() for w in phonemized)