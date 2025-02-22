"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
from mishkal.vocab import SET_OUTPUT_CHARACTERS

print(sorted(SET_OUTPUT_CHARACTERS))