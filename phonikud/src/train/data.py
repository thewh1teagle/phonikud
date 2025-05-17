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
import torch.nn.functional as F


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



class TrainData(Dataset):
    def __init__(self, lines: List[str]):
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        line = self.lines[idx]
        text = ""
        num_classes = 4
        targets = []  # list of [num_classes] binary arrays

        # Track which labels apply to the previous char
        pending_labels = set()

        for char in line:
            # Feature char (apply to previous real char)
            if char in (HATAMA_CHAR, MOBILE_SHVA_CHAR, PREFIX_CHAR):
                # Map feature char to class index and queue it
                label_idx = {
                    HATAMA_CHAR: 1,
                    MOBILE_SHVA_CHAR: 2,
                    PREFIX_CHAR: 3
                }[char]
                if len(targets) > 0:
                    # Set the label for the previous char (multi-label allowed)
                    targets[-1][label_idx] = 1
            else:
                # Real Hebrew character: start with no labels
                arr = [0] * num_classes
                arr[0] = 1  # Default "plain" unless any other is present
                targets.append(arr)
                text += char

        # Remove "plain" (arr[0]) when any other label is set (optional)
        for arr in targets:
            if sum(arr[1:]) > 0:
                arr[0] = 0

        assert len(text) == len(targets)

        # Output shape: [seq_len, num_classes], dtype float
        targets_tensor = torch.tensor(targets, dtype=torch.float)
        return text, targets_tensor


class Collator:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def collate_fn(self, items):
        inputs = self.tokenizer(
            [x[0] for x in items], padding=True, truncation=True, return_tensors="pt"
        )
        targets = pad_sequence([x[1] for x in items], batch_first=True)
        # ^ shape: (batch_size, n_chars_padded, n_active_components)

        return inputs, targets