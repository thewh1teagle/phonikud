"""
High level phonemize functions
"""

import unicodedata

from mishkal.token import extract_letters
from mishkal.variants import Word
from mishkal.expander import Expander
from mishkal.dictionary import Dictionary
from mishkal.phoneme_set import get_phoneme_set # noqa: F401
from .utils import is_only_phonemes
from .variants import Phoneme
from .phonemize import Phonemizer

expander = Expander()
dictionary = Dictionary()
phonemizer = Phonemizer()

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
        if not line: continue
        line = expander.expand_text(line)
        if not line: continue
        line = dictionary.expand_text(line)
        for word in line.split():
            if is_only_phonemes(word):
                # TODO: improve
                phonemized.append(Word(word, [Phoneme(p, word, None, reasons='pre phonemized') for p in word]))
            else:
                letters = extract_letters(word)
                phonemes = phonemizer.phonemize_letters(letters)
                phonemized_word = Word(word, phonemes)
                phonemized.append(phonemized_word)
    if debug:
        return phonemized
    return ' '.join(w.as_phonemes_str() for w in phonemized)