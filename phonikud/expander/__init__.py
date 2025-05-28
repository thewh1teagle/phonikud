"""
Expand dates and numbers into words with nikud
This happens before phonemization
"""

from .numbers import num_to_word
from .dates import date_to_word
from .time_to_word import time_to_word
from .dictionary import Dictionary
from phonikud.log import log


class Expander:
    def __init__(self):
        self.dictionary = Dictionary()

    def expand_text(self, text: str):
        words = []
        for source_word in text.split():
            try:
                word = date_to_word(source_word)
                if word == source_word:
                    word = time_to_word(word)
                if word == source_word:
                    word = num_to_word(word)
                words.append(word)
            except Exception as e:
                log.error(f"Failed to expand {word} with error: {e}")
                words.append(source_word)
        text = " ".join(words)
        text = self.dictionary.expand_text(text)

        return text
