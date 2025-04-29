"""
uv run pytest tests/test_syllables.py
"""

from mishkal.phonemize import Phonemizer
from mishkal.utils import get_letters, get_syllables
from mishkal.hebrew import phonemize_hebrew

phonemizer = Phonemizer()

test_data = {
    "אוֹפַנַּיִים": ["ʔo", "fa", "na", "jim"],
    "אֵיתָנוּת": ["ʔej", "ta", "nut"],
    "רֵיחַ": ["re", "ax"],
    "אֵיתָנוּת": ["ʔej", "ta", "nut"],
    "אֵיר֫וֹפָּה": ["ʔej", "rˈo", "pah"],
    "צָהֳרַ֫יִם": ["tso", "ho", "rˈa", "jim"],
    "דַּוָָר": ["da", "var"],
    "עַכְשָׁ֫יו": ["ʔax", "ʃˈav"],
    "כׇּל": ["kol"],
    "הַמָּלֵ": ["ha", "ma", "le"],
    "רוּחַ": ["ru", "ax"],
    "אֶנְצִיקְלוֹפֶּ֫דְיָה": ["ʔen", "tsik", "lo", "pˈed", "jah"],
}

# def test_syllables():
#     for w, s in test_data.items():
#         letters = get_letters(w)
#         phonemes = phonemize_hebrew(letters, False)
#         result = get_syllables(phonemes)
#         assert result == s
