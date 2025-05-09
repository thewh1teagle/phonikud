from pathlib import Path
from typing import List, Tuple

import torch
import sys
sys.path.append("/home/maxm/mishkal")
from phonikud.src.model import (
    MOBILE_SHVA_CHAR,
    NIKUD_HASER,
    PREFIX_CHAR,
    HATAMA_CHAR,
    remove_nikud,
)
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

COMPONENT_INDICES = {"hatama": 0, "shva": 1, "prefix": 2}


def get_dataloader(lines, args, components, collator: "Collator"):
    train_data = TrainData(lines, components)
    
    loader = DataLoader(
        train_data,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers,
    )
    return loader


def read_lines(
    data_path: str,
    components: List[str],
    max_context_length: int = 2048,
    val_split: float = 0.1,
    split_seed: int = 42,
) -> Tuple[List[str], List[str]]:
    files = list(Path(data_path).glob("**/*.txt"))

    lines = []
    for file in files:
        with open(file, "r", encoding="utf-8") as fp:
            for line in fp:
                # Split lines into chunks if they are too long
                while len(line) > max_context_length:
                    lines.append(line[:max_context_length].strip())
                    line = line[max_context_length:]

                if line.strip():
                    lines.append(line.strip())

    # Preprocess lines (remove nikud and other components)
    lines = [
        remove_nikud(i, additional=get_diac_to_remove(components=components))
        for i in lines
    ]

    # Split into train and validation sets
    split_idx = int(len(lines) * (1 - val_split))
    torch.manual_seed(split_seed)
    idx = torch.randperm(len(lines))
    train_lines = [lines[i] for i in idx[:split_idx]]
    val_lines = [lines[i] for i in idx[split_idx:]]

    return train_lines, val_lines


def get_diac_to_remove(components: str):
    """
    We train on specific phonetic diacritics
    """
    phonetic_diac_to_remove = NIKUD_HASER
    if "shva" not in components:
        # Won't train on shva
        phonetic_diac_to_remove += MOBILE_SHVA_CHAR
    if "hatama" not in components:
        # Won't train on hatama
        phonetic_diac_to_remove += HATAMA_CHAR
    if "prefix" not in components:
        # Won't train on prefix
        phonetic_diac_to_remove += PREFIX_CHAR
    return phonetic_diac_to_remove


class AnnotatedLine:
    def __init__(self, raw_text, components):
        self.components = components

        # Get indices for active components
        self.active_indices = [COMPONENT_INDICES[comp] for comp in components]

        # filter based on components
        raw_text = "".join(
            char
            for char in raw_text
            if not (char == HATAMA_CHAR and "hatama" not in components)
            and not (char == MOBILE_SHVA_CHAR and "shva" not in components)
            and not (char == PREFIX_CHAR and "prefix" not in components)
        )

        self.text = ""  # will contain plain hebrew text
        hatama = []  # will contain 0/1 for each character (1=active hatama)
        mobile_shva = []  # will contain 0/1 for each character (1=mobile shva)
        prefix = []  # will contain 0/1 for each character (1=prefix)

        for i, char in enumerate(raw_text):
            if char == HATAMA_CHAR:
                hatama[-1] = 1
            elif char == MOBILE_SHVA_CHAR:
                mobile_shva[-1] = 1
            elif char == PREFIX_CHAR:
                prefix[-1] = 1
            else:
                self.text += char
                hatama += [0]
                mobile_shva += [0]
                prefix += [0]  # No prefix for this character by default

        assert len(self.text) == len(hatama) == len(mobile_shva) == len(prefix)

        # Create tensor for all features
        all_features = [
            torch.tensor(hatama),
            torch.tensor(mobile_shva),
            torch.tensor(prefix),
        ]

        # Only use the features for active components
        self.target = torch.stack([all_features[i] for i in self.active_indices])
        # ^ shape: (n_active_components, n_chars)


class TrainData(Dataset):
    def __init__(self, lines: List[str], components: List[str]):
        self.lines = lines
        self.components = components

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        text = self.lines[idx]
        return AnnotatedLine(text, components=self.components)


class Collator:
    def __init__(self, tokenizer, components):
        self.tokenizer = tokenizer
        self.components = components

    def collate_fn(self, items):
        inputs = self.tokenizer(
            [x.text for x in items], padding=True, truncation=True, return_tensors="pt"
        )
        targets = pad_sequence([x.target.T for x in items], batch_first=True)
        # ^ shape: (batch_size, n_chars_padded, n_active_components)

        return inputs, targets
