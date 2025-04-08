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
    use_expander=True,
    use_post_normalize=True,  # For TTS
    predict_stress=False,
    fallback: Callable[[str], str] = None,
) -> str:
    phonemes = phonemizer.phonemize(
        text,
        preserve_punctuation=preserve_punctuation,
        preserve_stress=preserve_stress,
        fallback=fallback,
        use_expander=use_expander,
        use_post_normalize=use_post_normalize,
        predict_stress=predict_stress,
    )
    return phonemes
