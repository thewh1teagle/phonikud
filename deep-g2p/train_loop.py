import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import json
import random
import os
from tqdm import tqdm
from data import G2PDataset, collate_fn
from model import Seq2Seq


def save_vocab(char_to_idx, phoneme_to_idx, vocab_path):
    """Save vocabulary as JSON with additional metadata"""
    vocab = {
        "char_to_idx": char_to_idx,
        "phoneme_to_idx": phoneme_to_idx,
        "idx_to_char": {idx: char for char, idx in char_to_idx.items()},
        "idx_to_phoneme": {idx: phoneme for phoneme, idx in phoneme_to_idx.items()},
        "char_vocab_size": len(char_to_idx),
        "phoneme_vocab_size": len(phoneme_to_idx),
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


def train(config):
    # Set random seeds for reproducibility
    torch.manual_seed(config.seed)
    random.seed(config.seed)

    device = torch.device(config.device)
    print(f"Using device: {device}")

    # Create checkpoint directory if it doesn't exist
    os.makedirs(config.checkpoint_path, exist_ok=True)

    # Load full dataset
    full_dataset = G2PDataset(config.data)

    # Split into train and validation
    total_size = len(full_dataset)
    train_size = int((1 - config.val_split) * total_size)
    val_size = total_size - train_size

    train_dataset, val_dataset = random_split(
        full_dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(config.seed),
    )

    print(f"Dataset split: {train_size} train, {val_size} validation")

    # Save vocabulary early (before training starts)
    save_vocab(full_dataset.char_to_idx, full_dataset.phoneme_to_idx, config.vocab_path)
    print(f"Vocabulary saved to: {config.vocab_path}")

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset, batch_size=config.batch_size, shuffle=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset, batch_size=config.batch_size, shuffle=False, collate_fn=collate_fn
    )

    # Initialize model
    model = Seq2Seq(len(full_dataset.char_to_idx), len(full_dataset.phoneme_to_idx)).to(
        device
    )
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    # Training loop with validation
    best_val_loss = float("inf")
    patience_counter = 0
    global_step = 0

    # Main epoch progress bar
    epoch_pbar = tqdm(range(config.epochs), desc="Training", unit="epoch")

    for epoch in epoch_pbar:
        # Training phase
        model.train()
        total_train_loss = 0
        num_train_batches = 0

        # Batch progress bar for training
        train_pbar = tqdm(
            train_loader,
            desc=f"Epoch {epoch+1}/{config.epochs}",
            leave=False,
            unit="batch",
        )

        for batch_idx, (src, trg) in enumerate(train_pbar):
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
            global_step += 1

            # Update progress bar with current loss and running average
            running_avg_loss = total_train_loss / num_train_batches
            train_pbar.set_postfix(
                {
                    "curr_loss": f"{loss.item():.4f}",
                    "avg_loss": f"{running_avg_loss:.4f}",
                    "step": global_step,
                }
            )

            # Save checkpoint at specified intervals
            if global_step % config.checkpoint_interval == 0:
                checkpoint_data = {
                    "epoch": epoch,
                    "global_step": global_step,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "loss": loss.item(),
                    "char_to_idx": full_dataset.char_to_idx,
                    "phoneme_to_idx": full_dataset.phoneme_to_idx,
                }

                # Save numbered checkpoint
                checkpoint_path = os.path.join(
                    config.checkpoint_path, f"checkpoint_step_{global_step}.pt"
                )
                torch.save(checkpoint_data, checkpoint_path)
                print(f"\nCheckpoint saved at step {global_step}: {checkpoint_path}")

                # Also save as "last" checkpoint
                last_checkpoint_path = os.path.join(config.checkpoint_path, "last")
                torch.save(checkpoint_data, last_checkpoint_path)
                print(f"Latest checkpoint saved: {last_checkpoint_path}")

        avg_train_loss = total_train_loss / num_train_batches

        # Validation phase
        avg_val_loss = validate(model, val_loader, criterion, device)

        # Update epoch progress bar
        epoch_pbar.set_postfix(
            {
                "train": f"{avg_train_loss:.4f}",
                "val": f"{avg_val_loss:.4f}",
                "best": f"{best_val_loss:.4f}",
                "patience": f"{patience_counter}/{config.patience}",
            }
        )

        print(
            f"Epoch {epoch+1}: Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}"
        )

        # Early stopping
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), config.model_path)
            print(f"New best model saved! Val Loss: {best_val_loss:.4f}")

            # Also save as "last" checkpoint
            checkpoint_data = {
                "epoch": epoch,
                "global_step": global_step,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": avg_val_loss,
                "char_to_idx": full_dataset.char_to_idx,
                "phoneme_to_idx": full_dataset.phoneme_to_idx,
            }
            last_checkpoint_path = os.path.join(config.checkpoint_path, "last")
            torch.save(checkpoint_data, last_checkpoint_path)
        else:
            patience_counter += 1
            if patience_counter >= config.patience:
                print(f"Early stopping after {epoch + 1} epochs")
                break

    epoch_pbar.close()

    print(f"Training completed. Best val loss: {best_val_loss:.4f}")
    print(f"Model saved to: {config.model_path}")
    print(f"Vocabulary saved to: {config.vocab_path}")
