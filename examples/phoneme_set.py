"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
from mishkal import get_phoneme_set

phonemes = get_phoneme_set()
print(phonemes)