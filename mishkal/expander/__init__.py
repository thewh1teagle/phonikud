"""
Expand dates and numbers into words with niqqud
This happens before phonemization
"""

from .numbers import num_to_word
from .dates import date_to_word

def expand_word(word: str):
    word = date_to_word(word)
    word = num_to_word(word)
    return word.split()