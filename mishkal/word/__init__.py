"""
Break word into letters and construct phonemes using letter module
"""

from .. import lexicon
from ..variants import Letter

def break_into_letters(word: str) -> list[Letter]:
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

def extract_letters(word: str) -> list[Letter]:
    """
    Extract letters from word
    We assume that:
        - Dates expanded to words
        - Numbers expanded to word
        - Symbols expanded already
        - Known words converted to phonemes
        - Rashey Tavot (acronyms) expanded already
        - English words converted to phonemes already
        - Text normalized using unicodedata.normalize('NFD')
    
    This function extract *ONLY* hebrew letters and niqqud from LEXICON
    Other characters ignored!
    """
    
    # Filter characters that are in lexicon
    # TODO: logging
    word = ''.join([c for c in word if lexicon.LEXICON.get(c)])
    letters = break_into_letters(word)
    return letters