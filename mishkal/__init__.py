"""
High level phonemize functions
"""
from .phonemize import Phonemizer, Token

phonemizer = Phonemizer()

def phonemize(text: str, preserve_punctuation = True, return_tokens = False) -> str | list[Token]:
    phonemes = phonemizer.phonemize(text, preserve_punctuation=preserve_punctuation, return_tokens=return_tokens)
    return phonemes
