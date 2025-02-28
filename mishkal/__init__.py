"""
High level phonemize functions
"""

from .phonemize import Phonemizer
from .utils import normalize  # noqa: F401
from typing import Callable

phonemizer = Phonemizer()


def phonemize(
    text: str,
    preserve_punctuation=True,
    preserve_stress=True,
    fallback: Callable[[str], str] = None,
) -> str:
    phonemes = phonemizer.phonemize(
        text,
        preserve_punctuation=preserve_punctuation,
        preserve_stress=preserve_stress,
        fallback=fallback,
    )
    return phonemes
