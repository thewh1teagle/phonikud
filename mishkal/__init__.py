"""
High level phonemize functions
"""

import unicodedata

from mishkal.phonemize import phonemize_letters
from mishkal.variants import Word
from .word import extract_letters
from .expander import expand_word

def phonemize(text: str, debug = False) -> str | list[Word]:
    """
    1. Normalize text
    2. Expand words with expander and dictionary
    3. Iterate lines
    4. Iterate words
    5. Phonemize each word
    """
    text = unicodedata.normalize('NFD', text)
    
    if not text:
        return [] if debug else ''
    
    phonemized: list[Word] = []
    
    for line in text.splitlines():
        for word in line.split():
            words = expand_word(word)
            for word in words:
                letters = extract_letters(word)
                phonemes = phonemize_letters(letters)
                phonemized_word = Word(word, phonemes)
                phonemized.append(phonemized_word)
    if debug:
        return phonemized
    return ' '.join(w.as_phonemes_str() for w in phonemized)