import torch
import torch.nn as nn
from torch.utils.data import Dataset
from collections import Counter


class G2PDataset(Dataset):
    def __init__(self, data_path, char_to_idx=None, phoneme_to_idx=None):
        self.pairs = []
        self.char_to_idx = char_to_idx or {
            "<pad>": 0,
            "<sos>": 1,
            "<eos>": 2,
            "<unk>": 3,
        }
        self.phoneme_to_idx = phoneme_to_idx or {
            "<pad>": 0,
            "<sos>": 1,
            "<eos>": 2,
            "<unk>": 3,
        }

        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                if "\t" in line:
                    text, phonemes = line.strip().split("\t")
                    self.pairs.append((text, phonemes))

        if char_to_idx is None:
            self._build_vocab()

    def _build_vocab(self):
        chars = Counter()
        phonemes = Counter()

        for text, phoneme in self.pairs:
            chars.update(text)
            phonemes.update(phoneme)

        for char in sorted(chars.keys()):
            if char not in self.char_to_idx:
                self.char_to_idx[char] = len(self.char_to_idx)

        for phoneme in sorted(phonemes.keys()):
            if phoneme not in self.phoneme_to_idx:
                self.phoneme_to_idx[phoneme] = len(self.phoneme_to_idx)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        text, phonemes = self.pairs[idx]

        text_ids = (
            [self.char_to_idx["<sos>"]]
            + [self.char_to_idx.get(c, self.char_to_idx["<unk>"]) for c in text]
            + [self.char_to_idx["<eos>"]]
        )
        phoneme_ids = (
            [self.phoneme_to_idx["<sos>"]]
            + [
                self.phoneme_to_idx.get(p, self.phoneme_to_idx["<unk>"])
                for p in phonemes
            ]
            + [self.phoneme_to_idx["<eos>"]]
        )

        return torch.tensor(text_ids), torch.tensor(phoneme_ids)


def collate_fn(batch):
    texts, phonemes = zip(*batch)
    texts = nn.utils.rnn.pad_sequence(list(texts), batch_first=True, padding_value=0)
    phonemes = nn.utils.rnn.pad_sequence(
        list(phonemes), batch_first=True, padding_value=0
    )
    return texts, phonemes
