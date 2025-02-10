"""
High level phonemize functions
"""

import unicodedata
from .word import PhonemizedWord, phonemize_word
           

def phonemize(text: str, debug = False) -> str | list[PhonemizedWord]:
    """
    1. Normalize text
    2. Expand words with expander and dictionary
    3. Iterate lines
    4. Iterate words
    5. Phonemize each word
    """
    text = unicodedata.normalize('NFD', text)
    # TODO: expand date and numbers
    
    if not text:
        return [] if debug else ''
    
    phonemized: list[PhonemizedWord] = []
    
    for line in text.splitlines():
        for word in line.split():
            phonemes = phonemize_word(word)
            phonemized_word = PhonemizedWord(word, phonemes)
            phonemized.append(phonemized_word)
    if debug:
        return phonemized
    

    return ' '.join(w.as_phonemes_str() for w in phonemized)