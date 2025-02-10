"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
from mishkal.phonene_table import get_possible_phonemes

phonemes = get_possible_phonemes()
print(', '.join(phonemes))