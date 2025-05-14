from typing import List

import torch
from src.train.config import TrainArgs
from src.model.phonikud_model import (
    HATAMA_CHAR,
    MOBILE_SHVA_CHAR,
    PREFIX_CHAR,
)
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset


def get_dataloader(lines: list[str], args: TrainArgs, collator: "Collator"):
    train_data = TrainData(lines)

    loader = DataLoader(
        train_data,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers,
    )
    return loader


class AnnotatedLine:
    def __init__(self, raw_text):
        print(f"raw text {raw_text}")

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
        features = [
            torch.tensor(hatama),
            torch.tensor(mobile_shva),
            torch.tensor(prefix),
        ]

        self.target = torch.stack(features)
        # ^ shape: (n_active_components, n_chars)


class TrainData(Dataset):
    def __init__(self, lines: List[str]):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        text = self.lines[idx]
        return AnnotatedLine(text)


class Collator:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def collate_fn(self, items):
        inputs = self.tokenizer(
            [x.text for x in items], padding=True, truncation=True, return_tensors="pt"
        )
        targets = pad_sequence([x.target.T for x in items], batch_first=True)
        # ^ shape: (batch_size, n_chars_padded, n_active_components)

        return inputs, targets
