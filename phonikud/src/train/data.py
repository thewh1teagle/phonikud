import os
from glob import glob

import torch
from phonikud.src.model import (
    MOBILE_SHVA_CHAR,
    NIKUD_HASER,
    PREFIX_CHAR,
    STRESS_CHAR,
    remove_nikud,
)
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset

COMPONENT_INDICES = {"stress": 0, "shva": 1, "prefix": 2}


def get_diac_to_remove(components: str):
    """
    We train on specific phonetic diacritics
    """
    phonetic_diac_to_remove = NIKUD_HASER
    if "shva" not in components:
        # Won't train on shva
        phonetic_diac_to_remove += MOBILE_SHVA_CHAR
    if "stress" not in components:
        # Won't train on stress
        phonetic_diac_to_remove += STRESS_CHAR
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
            if not (char == STRESS_CHAR and "stress" not in components)
            and not (char == MOBILE_SHVA_CHAR and "shva" not in components)
            and not (char == PREFIX_CHAR and "prefix" not in components)
        )

        self.text = ""  # will contain plain hebrew text
        stress = []  # will contain 0/1 for each character (1=stressed)
        mobile_shva = []  # will contain 0/1 for each character (1=mobile shva)
        prefix = []  # will contain 0/1 for each character (1=prefix)

        for i, char in enumerate(raw_text):
            if char == STRESS_CHAR:
                stress[-1] = 1
            elif char == MOBILE_SHVA_CHAR:
                mobile_shva[-1] = 1
            elif char == PREFIX_CHAR:
                prefix[-1] = 1
            else:
                self.text += char
                stress += [0]
                mobile_shva += [0]
                prefix += [0]  # No prefix for this character by default

        assert len(self.text) == len(stress) == len(mobile_shva) == len(prefix)

        # Create tensor for all features
        all_features = [
            torch.tensor(stress),
            torch.tensor(mobile_shva),
            torch.tensor(prefix),
        ]

        # Only use the features for active components
        self.target = torch.stack([all_features[i] for i in self.active_indices])
        # ^ shape: (n_active_components, n_chars)


class TrainData(Dataset):
    def __init__(self, args):
        self.max_context_length = 2048
        self.components: list[str] = args.components.split(",")
        print(f"🔤 Training with components: {', '.join(self.components)}")

        files = glob(
            os.path.join(args.data_dir, "train", "**", "*.txt"), recursive=True
        )
        print(f"📝 Found {len(files)} text files for training.")
        self.lines = self._load_lines(files)
        print(f"📄 Loaded {len(self.lines)} lines.")
        print("🔍 Sample lines:")
        for line in self.lines[:3]:
            print("   ", line)

    def _load_lines(self, files: list[str]):
        lines = []
        for file in files:
            with open(file, "r", encoding="utf-8") as fp:
                for line in fp:
                    # While the line is longer than max_context_length, split it into chunks
                    while len(line) > self.max_context_length:
                        lines.append(
                            line[: self.max_context_length].strip()
                        )  # Add the first chunk
                        line = line[
                            self.max_context_length :
                        ]  # Keep the remainder of the line

                    # Add the remaining part of the line if it fits within the max_context_length
                    if line.strip():
                        lines.append(line.strip())
        lines = [
            remove_nikud(i, additional=get_diac_to_remove(components=self.components))
            for i in lines
        ]
        return lines

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
