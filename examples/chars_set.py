"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
from mishkal.chars_set import get_chars_set, pretty_chars_set

pretty_chars = pretty_chars_set()
chars = get_chars_set()
print(f'Pretty chars {len(pretty_chars)}: ', ' '.join(pretty_chars))
print(f'Chars {len(chars)}: ', ' '.join(chars))