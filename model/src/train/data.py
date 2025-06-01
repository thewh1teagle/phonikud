from typing import List
import torch
from src.train.config import TrainArgs
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizerFast
from typing import Tuple
from src.model.phonikud_model import (
    HATAMA_CHAR,
    MOBILE_SHVA_CHAR,
    PREFIX_CHAR,
)


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

        for char in line:
            # Feature char (apply to previous real char)
            if char in (HATAMA_CHAR, MOBILE_SHVA_CHAR, PREFIX_CHAR):
                # Map feature char to class index and queue it
                label_idx = {HATAMA_CHAR: 1, MOBILE_SHVA_CHAR: 2, PREFIX_CHAR: 3}[char]
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
    def __init__(self, tokenizer: BertTokenizerFast):
        self.tokenizer = tokenizer

    def collate_fn(self, items: List[Tuple[str, torch.Tensor]]):
        texts = [x[0] for x in items]
        char_targets_list = [
            x[1] for x in items
        ]  # List of [seq_len, num_classes] tensors
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=1024,
            return_offsets_mapping=True,
            add_special_tokens=True,
        )
        # Build token-level targets for each item in batch
        batch_token_targets = []
        for i, char_targets in enumerate(char_targets_list):
            # Get offset mapping for this specific item
            offset_mapping = inputs.offset_mapping[i]

            # Initialize token targets (exclude class 0 "plain", keep classes 1-3)
            token_targets = torch.zeros(len(offset_mapping), 3)

            for token_idx, (start, end) in enumerate(offset_mapping):
                if end == 0:  # CLS/SEP/pad tokens → leave zeros
                    continue

                # Get max values across character range for this token
                # char_targets shape: [seq_len, 4], we want classes 1-3
                if start < len(char_targets):
                    end_idx = min(end, len(char_targets))
                    token_targets[token_idx] = (
                        char_targets[start:end_idx, 1:].max(0).values
                    )

            batch_token_targets.append(token_targets)

        # Stack token targets and remove offset_mapping from inputs
        targets = torch.stack(batch_token_targets)
        inputs.pop(
            "offset_mapping"
        )  # Remove offset_mapping as it's not needed for model

        return inputs, targets
