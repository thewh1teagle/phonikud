"""
uv run examples/chars_set.py
"""

from mishkal.lexicon import SET_OUTPUT_CHARACTERS, SET_INPUT_CHARACTERS

print("Expected input: ", sorted(SET_INPUT_CHARACTERS))
print("Expected output: ", sorted(SET_OUTPUT_CHARACTERS))
# Note: you should use mishkal.normalize() when creating datasets to align with the library.
