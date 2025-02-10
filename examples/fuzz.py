"""
fuzzing with millions of words to make sure it works fine
git clone https://github.com/thewh1teagle/hebrew_diacritized
uv run examples/fuzz.py hebrew_diacritized/data
"""

from mishkal import phonemize
from pathlib import Path
import sys


target_dir = sys.argv[1]
files = Path(target_dir).glob('**/*.txt')

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            phonemes = phonemize(line)
            print(phonemes)