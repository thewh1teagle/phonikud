import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import Seq2Seq
from collections import Counter
import pickle


class G2PDataset(Dataset):
    def __init__(self, data_path, char_to_idx=None, phoneme_to_idx=None):
        self.pairs = []
        self.char_to_idx = char_to_idx or {"<pad>": 0, "<sos>": 1, "<eos>": 2}
        self.phoneme_to_idx = phoneme_to_idx or {"<pad>": 0, "<sos>": 1, "<eos>": 2}

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

        for char in chars:
            if char not in self.char_to_idx:
                self.char_to_idx[char] = len(self.char_to_idx)

        for phoneme in phonemes:
            if phoneme not in self.phoneme_to_idx:
                self.phoneme_to_idx[phoneme] = len(self.phoneme_to_idx)

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        text, phonemes = self.pairs[idx]

        text_ids = (
            [self.char_to_idx["<sos>"]]
            + [self.char_to_idx.get(c, 0) for c in text]
            + [self.char_to_idx["<eos>"]]
        )
        phoneme_ids = (
            [self.phoneme_to_idx["<sos>"]]
            + [self.phoneme_to_idx.get(p, 0) for p in phonemes]
            + [self.phoneme_to_idx["<eos>"]]
        )

        return torch.tensor(text_ids), torch.tensor(phoneme_ids)


def collate_fn(batch):
    texts, phonemes = zip(*batch)
    texts = nn.utils.rnn.pad_sequence(texts, batch_first=True, padding_value=0)
    phonemes = nn.utils.rnn.pad_sequence(phonemes, batch_first=True, padding_value=0)
    return texts, phonemes


def train(args):
    dataset = G2PDataset(args.data)
    dataloader = DataLoader(
        dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn
    )

    model = Seq2Seq(len(dataset.char_to_idx), len(dataset.phoneme_to_idx))
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0
        for batch_idx, (src, trg) in enumerate(dataloader):
            optimizer.zero_grad()

            output = model(src, trg)
            output = output[:, 1:].reshape(-1, output.size(-1))
            trg = trg[:, 1:].reshape(-1)

            loss = criterion(output, trg)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if batch_idx % 10 == 0:
                print(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")

        print(f"Epoch {epoch} completed, Avg Loss: {total_loss/len(dataloader):.4f}")

    torch.save(model.state_dict(), args.model_path)
    with open(args.vocab_path, "wb") as f:
        pickle.dump((dataset.char_to_idx, dataset.phoneme_to_idx), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/train.txt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--model_path", default="model.pt")
    parser.add_argument("--vocab_path", default="vocab.pkl")

    args = parser.parse_args()
    train(args)
