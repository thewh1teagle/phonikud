"""
Break word into letters and construct phonemes using letter module
"""

import unicodedata
from .. import lexicon
from .phoneme import Letter, Phoneme
from ..letter import phonemize_letters

class PhonemizedWord:
    def __init__(self, word: str, phonemes: list[Phoneme]):
        self.word = word
        self.phonemes = phonemes
    
    def as_phonemes_str(self) -> str:
        return ''.join(p.phonemes for p in self.phonemes)
    
    def as_word_str(self) -> str:
        return self.word
    
    def symbols_names(self) -> list[str]:
        names = []
        for phoneme in self.phonemes:
            for symbol in phoneme.letter.symbols:
                names.append(unicodedata.name(symbol, '?'))
        return ', '.join(names)

def get_letters(word: str) -> list[Letter]:
    """
    Splits a Hebrew word into Letter objects where each letter retains its symbols (if present).
    Assumptions:
    - The input is at least 1 character long.
    - Hebrew letters are from lexicon.LETTERS.
    - Niqqud and other marks are from lexicon.LETTER_SYMBOLS.
    """
    letters = []
    i = 0

    while i < len(word):
        char = word[i]

        if char in lexicon.LETTERS:
            symbols = []
            i += 1  # Move to potential niqqud

            # Collect symbols attached to this letter
            while i < len(word) and word[i] in lexicon.LETTER_SYMBOLS:
                symbols.append(word[i])
                i += 1  # Move to the next character
            letters.append(Letter(char, symbols))
        else:
            i += 1  # Skip non-letter characters (shouldn't happen in normal words)

    return letters

def phonemize_word(word: str) -> PhonemizedWord:
    """
    Convert Hebrew word into phonemes
    We assume that:
        - Dates expanded to words
        - Numbers expanded to word
        - Symbols expanded already
        - Known words converted to phonemes
        - Rashey Tavot (acronyms) expanded already
        - English words converted to phonemes already
        - Text normalized using unicodedata.normalize('NFD')
    
    This function phonemize *ONLY* hebrew characters / regular punctuation from LEXICON
    Other characters ignored!
    """
    
    # Filter characters that are in lexicon
    # TODO: logging
    word = ''.join([c for c in word if lexicon.LEXICON.get(c)])
    letters = get_letters(word)
    phonemes = phonemize_letters(letters)
    return phonemes