"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
from mishkal import get_phoneme_set
from pprint import pprint

phoneme_set = get_phoneme_set()
pprint(phoneme_set)
print(f'Phonemes {len(phoneme_set)}: ', ', '.join(phoneme_set))