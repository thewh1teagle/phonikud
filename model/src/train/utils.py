from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass
import torch
from src.model.phonikud_model import (
    PhoNikudModel,
    remove_enhanced_nikud,
)
from tqdm import tqdm


@dataclass
class TrainingLine:
    vocalized: str  # Vocalized text with diacritics (nikud)
    unvocalized: str  # Unvocalized text without diacritics


def print_model_size(model: PhoNikudModel):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"💾 Total Parameters: {total_params:,}")
    print(f"🔧 Trainable Parameters: {trainable_params:,}")


def read_lines(
    data_path: str,
    max_context_length: int = 2048,
    val_split: float = 0.1,
    split_seed: int = 42,
) -> Tuple[List[TrainingLine], List[TrainingLine]]:
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
                        vocalized = line[:max_context_length].strip()
                        unvocalized = remove_enhanced_nikud(vocalized)
                        lines.append(TrainingLine(vocalized, unvocalized))
                        line = line[max_context_length:]

                    if line.strip():
                        vocalized = line.strip()
                        unvocalized = remove_enhanced_nikud(vocalized)
                        lines.append(TrainingLine(vocalized, unvocalized))

    # Split into train and validation sets (keeping pairs together)
    split_idx = int(len(lines) * (1 - val_split))
    torch.manual_seed(split_seed)
    idx = torch.randperm(len(lines))

    train_lines: List[TrainingLine] = [lines[i] for i in idx[:split_idx]]
    val_lines: List[TrainingLine] = [lines[i] for i in idx[split_idx:]]

    # Print samples
    print("🛤️ Train samples:")
    for i in train_lines[:3]:
        print(f"\t{i.unvocalized}")
    print("🧪 Validation samples:")
    for i in val_lines[:3]:
        print(f"\t{i.unvocalized}")

    return train_lines, val_lines
