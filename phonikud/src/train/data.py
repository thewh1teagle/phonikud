from typing import List
import torch
from src.train.config import TrainArgs
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
        num_classes = 3  # Only classes 1-3 (hatama, mobile_shva, prefix)
        targets = []

        for char in line:
            # Feature char (apply to previous real char)
            if char in (HATAMA_CHAR, MOBILE_SHVA_CHAR, PREFIX_CHAR):
                # Map feature char to class index and queue it
                label_idx = {HATAMA_CHAR: 0, MOBILE_SHVA_CHAR: 1, PREFIX_CHAR: 2}[char]
                if len(targets) > 0:
                    # Set the label for the previous char (multi-label allowed)
                    targets[-1][label_idx] = 1
            else:
                # Real Hebrew character: start with no labels
                arr = [0] * num_classes
                targets.append(arr)
                text += char

        assert len(text) == len(targets)

        # Output shape: [seq_len, num_classes], dtype float
        targets_tensor = torch.tensor(targets, dtype=torch.float)
        return text, targets_tensor


class Collator:
    def __init__(self, tokenizer: BertTokenizerFast):
        self.tokenizer = tokenizer

    def collate_fn(self, items: List):
        texts = [x[0] for x in items]
        char_targets_list = [x[1] for x in items]
        
        # Tokenize without offset mapping - keep it simple
        inputs = self.tokenizer(
            texts, 
            padding=True, 
            truncation=True, 
            return_tensors="pt", 
            max_length=1024,
            add_special_tokens=True
        )
        
        # Create token-level targets by duplicating character targets
        # This is a simplification - each token gets the same label as its first character
        batch_token_targets = []
        max_tokens = inputs.input_ids.size(1)
        
        for i, char_targets in enumerate(char_targets_list):
            # Initialize token targets with zeros
            token_targets = torch.zeros(max_tokens, 3)
            
            # Map character targets to tokens (simple approach)
            text = texts[i]
            token_ids = inputs.input_ids[i]
            
            # Skip special tokens and map remaining tokens to characters
            text_tokens = token_ids[1:-1]  # Remove [CLS] and [SEP]
            char_idx = 0
            
            for token_idx in range(1, min(len(token_ids) - 1, len(char_targets) + 1)):
                if char_idx < len(char_targets):
                    token_targets[token_idx] = char_targets[char_idx]
                    char_idx += 1
            
            batch_token_targets.append(token_targets)
        
        targets = torch.stack(batch_token_targets)
        
        return {
            "input_ids": inputs.input_ids,
            "attention_mask": inputs.attention_mask,
            "token_type_ids": inputs.token_type_ids,
            "targets": targets,
            "texts": texts
        }