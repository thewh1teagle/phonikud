from pathlib import Path
from typing import List, Tuple

import humanize
import torch
from src.model.phonikud_model import (
    HATAMA_CHAR,
    MOBILE_SHVA_CHAR,
    NIKUD_HASER,
    PREFIX_CHAR,
    remove_nikud,
)
from tqdm import tqdm


def print_model_size(model):
    def count_params(module):
        return sum(p.numel() for p in module.parameters())

    def pretty(n):
        return humanize.intword(n)

    print("🔍 Model breakdown:")
    print(f"  ⚙️  MLP: {pretty(count_params(model.mlp))} parameters")
    print(f"  📘 Menaked: {pretty(count_params(model.menaked))} parameters")
    print(f"  🧠  BERT: {pretty(count_params(model.bert))} parameters")


def read_lines(
    data_path: str,
    max_context_length: int = 2048,
    val_split: float = 0.1,
    split_seed: int = 42,
) -> Tuple[List[str], List[str]]:
    files = list(Path(data_path).glob("**/*.txt"))
    total_bytes = sum(f.stat().st_size for f in files)

    lines = []
    with tqdm(
        total=total_bytes, desc="📚 Loading text files...", unit="B", unit_scale=True
    ) as pbar:
        for file in files:
            with open(file, "r", encoding="utf-8") as fp:
                for line in fp:
                    pbar.update(len(line.encode("utf-8")))
                    # Split lines into chunks if they are too long
                    while len(line) > max_context_length:
                        lines.append(line[:max_context_length].strip())
                        line = line[max_context_length:]

                    if line.strip():
                        lines.append(line.strip())

    # Preprocess lines (remove nikud and other components)
    lines = [remove_nikud(i, additional=NIKUD_HASER) for i in lines]

    # Split into train and validation sets
    split_idx = int(len(lines) * (1 - val_split))
    torch.manual_seed(split_seed)
    idx = torch.randperm(len(lines))
    train_lines = [lines[i] for i in idx[:split_idx]]
    val_lines = [lines[i] for i in idx[split_idx:]]

    # Print samples
    print("🛤️ Train samples:")
    for i in train_lines[:3]:
        print(f"  • {i}")
    print("🧪 Validation samples:")
    for i in val_lines[:3]:
        print(f"  • {i}")

    return train_lines, val_lines
