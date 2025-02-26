"""
High level phonemize functions
"""

from .phonemize import Phonemizer, Token
from .utils import normalize  # noqa: F401

phonemizer = Phonemizer()


def phonemize(
    text: str, preserve_punctuation=True, preserve_stress=True, return_tokens=False
) -> str | list[Token]:
    phonemes = phonemizer.phonemize(
        text,
        preserve_punctuation=preserve_punctuation,
        preserve_stress=preserve_stress,
        return_tokens=return_tokens,
    )
    return phonemes
