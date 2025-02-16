r"""
All characters in Hebrew that used for LETTERS sounds
Excluding Gershaim (0x22 and 0x5F4) as it's not sound in character level
Excluding RAFE (0x5BF), METEG (0x5BD)
Checked on ~3M words curpos

Reference 
    https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
    https://en.wikipedia.org/wiki/Hebrew_punctuation#Geresh_and_gershayim
    https://github.com/python/cpython/blob/main/Lib/string.py#L31
    
For display the name of each use:
import unicodedata
unicodedata.name(c)

To normalize hebrew characters (eg. U+FB4x from single character of letter + nikud into multiple characters).
import unicodedata
unicodedata.normalize('NFD', '\uFB30')

** Currently punctuation are ignored **
"""

from . import (
    letters,
    symbols
)
import unicodedata

PUNCTUATION = {
    char: unicodedata.name(char) for char in 
    r"""!"'(),-.:?`""" # See string.punctuation
}

# Lexicon dictionary
LETTERS = {
    char: unicodedata.name(char) for char in 
    letters.chars
}
LETTER_SYMBOLS = {
    char: unicodedata.name(char) for char in 
    symbols.chars
}
LEXICON = {
    **LETTERS,
    **PUNCTUATION, 
    **LETTER_SYMBOLS,
}
