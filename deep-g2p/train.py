import argparse
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from model import Seq2Seq
from collections import Counter
import json
import random


class G2PDataset(Dataset):
    def __init__(self, data_path, char_to_idx=None, phoneme_to_idx=None):
        self.pairs = []
        self.char_to_idx = char_to_idx or {"<pad>": 0, "<sos>": 1, "<eos>": 2, "<unk>": 3}
        self.phoneme_to_idx = phoneme_to_idx or {"<pad>": 0, "<sos>": 1, "<eos>": 2, "<unk>": 3}

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
            + [self.phoneme_to_idx.get(p, self.phoneme_to_idx["<unk>"]) for p in phonemes]
            + [self.phoneme_to_idx["<eos>"]]
        )

        return torch.tensor(text_ids), torch.tensor(phoneme_ids)


def collate_fn(batch):
    texts, phonemes = zip(*batch)
    texts = nn.utils.rnn.pad_sequence(list(texts), batch_first=True, padding_value=0)
    phonemes = nn.utils.rnn.pad_sequence(list(phonemes), batch_first=True, padding_value=0)
    return texts, phonemes


def save_vocab(char_to_idx, phoneme_to_idx, vocab_path):
    """Save vocabulary as JSON with additional metadata"""
    vocab = {
        "char_to_idx": char_to_idx,
        "phoneme_to_idx": phoneme_to_idx,
        "idx_to_char": {idx: char for char, idx in char_to_idx.items()},
        "idx_to_phoneme": {idx: phoneme for phoneme, idx in phoneme_to_idx.items()},
        "char_vocab_size": len(char_to_idx),
        "phoneme_vocab_size": len(phoneme_to_idx)
    }
    
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)


def validate(model, val_loader, criterion, device):
    """Validate the model"""
    model.eval()
    total_loss = 0
    num_batches = 0
    
    with torch.no_grad():
        for src, trg in val_loader:
            src, trg = src.to(device), trg.to(device)
            
            output = model(src, trg)
            output = output[:, 1:].reshape(-1, output.size(-1))
            trg = trg[:, 1:].reshape(-1)
            
            loss = criterion(output, trg)
            total_loss += loss.item()
            num_batches += 1
    
    return total_loss / num_batches


def train(args):
    # Set random seeds for reproducibility
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load full dataset
    full_dataset = G2PDataset(args.data)
    
    # Split into train and validation
    total_size = len(full_dataset)
    train_size = int((1 - args.val_split) * total_size)
    val_size = total_size - train_size
    
    train_dataset, val_dataset = random_split(
        full_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(args.seed)
    )
    
    print(f"Dataset split: {train_size} train, {val_size} validation")
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size, shuffle=False, collate_fn=collate_fn
    )

    # Initialize model
    model = Seq2Seq(len(full_dataset.char_to_idx), len(full_dataset.phoneme_to_idx)).to(device)
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Training loop with validation
    best_val_loss = float('inf')
    patience_counter = 0
    
    for epoch in range(args.epochs):
        # Training phase
        model.train()
        total_train_loss = 0
        num_train_batches = 0
        
        for batch_idx, (src, trg) in enumerate(train_loader):
            src, trg = src.to(device), trg.to(device)
            
            optimizer.zero_grad()
            output = model(src, trg)
            output = output[:, 1:].reshape(-1, output.size(-1))
            trg = trg[:, 1:].reshape(-1)

            loss = criterion(output, trg)
            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()
            num_train_batches += 1

            if batch_idx % 10 == 0:
                print(f"Epoch {epoch}, Batch {batch_idx}, Train Loss: {loss.item():.4f}")

        avg_train_loss = total_train_loss / num_train_batches
        
        # Validation phase
        avg_val_loss = validate(model, val_loader, criterion, device)
        
        print(f"Epoch {epoch}: Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
        
        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), args.model_path)
            print(f"New best model saved! Val Loss: {best_val_loss:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"Early stopping after {epoch + 1} epochs")
                break

    # Save vocabulary
    save_vocab(full_dataset.char_to_idx, full_dataset.phoneme_to_idx, args.vocab_path)
    print(f"Training completed. Best val loss: {best_val_loss:.4f}")
    print(f"Model saved to: {args.model_path}")
    print(f"Vocabulary saved to: {args.vocab_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/train.txt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--val_split", type=float, default=0.2, help="Validation split ratio (0.0-1.0)")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--model_path", default="model.pt")
    parser.add_argument("--vocab_path", default="vocab.json")

    args = parser.parse_args()
    train(args)
