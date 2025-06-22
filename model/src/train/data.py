from typing import List, Tuple
import torch
from dataclasses import dataclass
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizerFast
from src.train.config import TrainArgs
from src.model.phonikud_model import HATAMA_CHAR, MOBILE_SHVA_CHAR, PREFIX_CHAR
from transformers.tokenization_utils_base import BatchEncoding


@dataclass
class Batch:
    text: List[str]  # Unvocalized text (for tokenization)
    vocalized: List[str]  # Vocalized text with diacritics (for evaluation)
    input: BatchEncoding
    outputs: torch.Tensor


def get_dataloader(
    unvocalized_lines: list[str],
    vocalized_lines: list[str],
    args: TrainArgs,
    collator: "Collator",
):
    return DataLoader(
        TrainData(unvocalized_lines, vocalized_lines),
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers,
    )


class TrainData(Dataset):
    def __init__(self, unvocalized_lines: List[str], vocalized_lines: List[str]):
        self.unvocalized_lines = unvocalized_lines
        self.vocalized_lines = vocalized_lines
        self.label_map = {HATAMA_CHAR: 1, MOBILE_SHVA_CHAR: 2, PREFIX_CHAR: 3}

    def __len__(self):
        return len(self.unvocalized_lines)

    def __getitem__(self, idx):
        unvocalized_line = self.unvocalized_lines[idx]
        vocalized_line = self.vocalized_lines[idx]
        
        # Create targets for each character in unvocalized text
        targets = [[1, 0, 0, 0] for _ in unvocalized_line]  # Default "plain" labels
        
        # Find enhanced diacritics and apply to previous character
        for i, char in enumerate(vocalized_line):
            if char in self.label_map:
                # Find the position in unvocalized text (look backwards)
                char_pos = len([c for c in vocalized_line[:i] if c in unvocalized_line]) - 1
                if 0 <= char_pos < len(targets):
                    targets[char_pos][self.label_map[char]] = 1
                    targets[char_pos][0] = 0  # Remove "plain" label
        
        return unvocalized_line, vocalized_line, torch.tensor(targets, dtype=torch.float)


class Collator:
    """Collates individual training examples into batches."""

    def __init__(self, tokenizer: BertTokenizerFast):
        self.tokenizer = tokenizer

    def collate_fn(self, items: List[Tuple[str, str, torch.Tensor]]) -> Batch:
        """Collate individual items into a batch."""
        text_list = [item[0] for item in items]
        vocalized_list = [item[1] for item in items]
        character_targets_list = [item[2] for item in items]

        # Tokenize all texts in the batch
        tokenized_inputs = self.tokenizer(
            text_list,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=1024,
            return_offsets_mapping=True,
            add_special_tokens=True,
        )

        # Create target tensor matching tokenized sequence length
        batch_size = len(text_list)
        sequence_length = tokenized_inputs.input_ids.size(1)
        num_labels = 3  # HATAMA, MOBILE_SHVA, PREFIX

        batch_targets = torch.zeros(batch_size, sequence_length, num_labels)

        # Map character-level targets to token-level targets
        self._map_character_targets_to_tokens(
            character_targets_list, tokenized_inputs.offset_mapping, batch_targets
        )

        # Remove offset mapping from final inputs (not needed for training)
        del tokenized_inputs["offset_mapping"]

        return Batch(
            text=list(text_list),
            vocalized=list(vocalized_list),
            input=tokenized_inputs,
            outputs=batch_targets,
        )

    def _map_character_targets_to_tokens(
        self,
        character_targets_list: List[torch.Tensor],
        offset_mappings: torch.Tensor,
        batch_targets: torch.Tensor,
    ) -> None:
        """Map character-level targets to token-level targets using offset mappings."""
        for batch_idx, (char_targets, token_offsets) in enumerate(
            zip(character_targets_list, offset_mappings)
        ):
            for token_idx, (char_start, char_end) in enumerate(token_offsets):
                char_start, char_end = int(char_start), int(char_end)
                if char_end > 0 and char_start < len(char_targets):
                    # Get the character range this token covers
                    char_end_clamped = min(char_end, len(char_targets))
                    char_range_targets = char_targets[
                        char_start:char_end_clamped, 1:
                    ]  # Skip plain label

                    # Take the maximum label across all characters in this token
                    token_labels = char_range_targets.max(0).values
                    batch_targets[batch_idx, token_idx] = token_labels
