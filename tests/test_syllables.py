"""
uv run pytest tests/test_syllables.py
"""

from mishkal.phonemize import Phonemizer, Syllable, normalize
from mishkal.utils import get_letters


phonemizer = Phonemizer()

words = {
    "שָׁלוֹם": [
        Syllable("שָׁ", 'ʃa'),
        Syllable("לוֹם", 'lom')
    ],
    "הַמָּלֵא": [
        Syllable("הַ", 'ha'),
        Syllable("מָּ", 'ma'),
        Syllable("לֵא", 'leʔ'),
    ],
    "אֶנְצִיקְלוֹפֶּדְיָה": [
        Syllable("אֶנְ", 'en'),
        Syllable("צִי", 'tsi'),
        Syllable("קְלוֹ", 'klo'),
        Syllable("פֶּדְ", 'ped'),
        Syllable("יָה", 'ja'),
    ]
}

def test_syllables():
    for word, syllables in words.items():
        letters = get_letters(word)
        result = phonemizer.phonemize_hebrew(letters, predict_shva_na=False)
        print(result)
test_syllables()
