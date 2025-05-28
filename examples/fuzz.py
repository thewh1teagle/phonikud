"""
fuzzing with millions of words to make sure it works fine
git clone https://github.com/thewh1teagle/hebrew_diacritized
uv run examples/fuzz.py hebrew_diacritized/data
"""

import sys
from pathlib import Path
from tqdm import tqdm
from phonikud import phonemize

target_dir = sys.argv[1]
files = sorted(Path(target_dir).glob("**/*.txt"), key=lambda f: f.stat().st_size)

total_size_bytes = sum(f.stat().st_size for f in files)
total_size_mb = total_size_bytes / (1024 * 1024)
print(f"Found {len(files)} files with total size of {total_size_mb:.2f} MB")

for file in tqdm(files, desc="Files"):
    # First pass: count lines without storing them
    with open(file, "r", encoding="utf-8") as f:
        num_lines = sum(1 for _ in f)

    # Second pass: process lines with progress bar
    with open(file, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=num_lines, desc=f"{file.name}", leave=False):
            phonemes = phonemize(line)
            # print(phonemes)
