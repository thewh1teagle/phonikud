"""
High level phonemize functions
"""

import unicodedata
from .word import Word, phonemize_word
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
                phonemes = phonemize_word(word)
                phonemized_word = Word(word, phonemes)
                phonemized.append(phonemized_word)
    if debug:
        return phonemized
    

    return ' '.join(w.as_phonemes_str() for w in phonemized)