import sys
from pathlib import Path
from tqdm import tqdm
from mishkal import phonemize

target_dir = sys.argv[1]
files = sorted(Path(target_dir).glob("**/*.txt"), key=lambda f: f.stat().st_size)

for file in tqdm(files, desc="Files"):
    # First pass: count lines without storing them
    with open(file, "r", encoding="utf-8") as f:
        num_lines = sum(1 for _ in f)

    # Second pass: process lines with progress bar
    with open(file, "r", encoding="utf-8") as f:
        for line in tqdm(f, total=num_lines, desc=f"{file.name}", leave=False):
            phonemes = phonemize(line)
            # print(phonemes)
