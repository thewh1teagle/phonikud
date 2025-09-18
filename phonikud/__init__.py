"""
High level phonemize functions
"""

from .phonemize import Phonemizer
from .phonemize_fst import PhonemizerFST
from .utils import normalize  # noqa: F401
from typing import Callable, Literal

phonemizer = Phonemizer()
phonemizer_fst = PhonemizerFST()


def phonemize(
    text: str,
    preserve_punctuation=True,
    preserve_stress=True,
    use_expander=True,
    use_post_normalize=True,  # For TTS
    predict_stress=True,
    predict_vocal_shva=True,
    stress_placement: Literal["syllable", "vowel"] = "vowel",
    schema: Literal["plain", "modern"] = "modern",
    fallback: Callable[[str], str] = None,
) -> str:
    """
    Set stress_at_start=True to place stress at syllable start.
    """
    phonemes = phonemizer.phonemize(
        text,
        preserve_punctuation=preserve_punctuation,
        preserve_stress=preserve_stress,
        fallback=fallback,
        use_expander=use_expander,
        use_post_normalize=use_post_normalize,
        predict_stress=predict_stress,
        schema=schema,
        predict_vocal_shva=predict_vocal_shva,
        stress_placement=stress_placement,
    )
    return phonemes


def phonemize_fst(text: str) -> str:
    return phonemizer_fst.phonemize(text)
