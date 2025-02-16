"""
High level phonemize functions
"""

import unicodedata
import re

from mishkal.token import extract_letters
from mishkal.variants import Word
from mishkal.expander import Expander
from mishkal.dictionary import Dictionary
from mishkal.chars_set import pretty_chars_set # noqa: F401
from .utils import is_phonemized
from .variants import Phoneme
from .phonemize import Phonemizer
from . import config
from . import lexicon
from . import chars_set

expander = Expander()
dictionary = Dictionary()
phonemizer = Phonemizer()

def normalize(text: str) -> str:
    return unicodedata.normalize('NFD', text)

def phonemize(text: str, preserve_punctuation = True) -> str:
    """
    1. Normalize text
    2. Expand words with expander and dictionary
    3. Iterate lines
    4. Iterate words
    5. Phonemize each word
    """
    text = normalize(text)
    
    phonemized = []
    
    def phonemize_callback(match: re.Match[str]) -> str:
        word = match.group(0)
        letters = extract_letters(word)
        phonemes = phonemizer.phonemize_letters(letters)
        phonemes = ''.join(p.phonemes for p in phonemes)
        return phonemes
    
    for line in text.splitlines():
        if not line: 
            continue
        # Expand
        line = expander.expand_text(line)
        if not line: 
            continue
        # Dictionary
        line = dictionary.expand_text(line)
        if not line: 
            continue
        for word in line.split():
            if is_phonemized(word):
                # TODO: improve
                phonemized.append(word)
            else:
                phonemes = re.sub(config.HE_CHARS_PATTERN, phonemize_callback, word)
                phonemes = ''.join([c for c in phonemes if c in chars_set.get_chars_set()])
                phonemized.append(phonemes)
    phonemes = ' '.join(w for w in phonemized)
    if not preserve_punctuation:
        phonemes = ''.join(c for c in phonemes if c not in lexicon.PUNCTUATION)
    return phonemes