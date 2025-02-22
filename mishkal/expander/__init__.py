"""
Expand dates and numbers into words with niqqud
This happens before phonemization
"""

from .numbers import num_to_word
from .dates import date_to_word
from .dictionary import Dictionary

class Expander:
    def __init__(self):
        self.dictionary = Dictionary()
        
    def expand_text(self, text: str):
        text = self.dictionary.expand_text(text)
        words = []
        for word in text.split():
            word = date_to_word(word)
            word = num_to_word(word)
            words.append(word)
        return ' '.join(words)