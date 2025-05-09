from typing import List

import torch
from src.model.phonikud_model import (
    HATAMA_CHAR,
    MOBILE_SHVA_CHAR,
    PREFIX_CHAR,
)
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset

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
