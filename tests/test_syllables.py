"""
uv run pytest tests/test_syllables.py
"""

from mishkal.phonemize import Phonemizer
from mishkal.utils import get_letters
from mishkal.hebrew import phonemize_hebrew


phonemizer = Phonemizer()


# def test_syllables():
#     for word, syllables in words.items():
#         letters = get_letters(word)
#         result = phonemize_hebrew(letters, predict_shva_na=False)
#         print(result)
# test_syllables()
