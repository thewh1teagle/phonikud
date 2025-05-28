from torch import nn
import torch
from config import TrainArgs
from torch.utils.data import DataLoader
import wandb
from tqdm import tqdm


def align_logits_and_targets(logits, targets):
    """Align logits and targets to the same sequence length."""
    min_seq_len = min(logits.size(1), targets.size(1))
    aligned_logits = logits[:, :min_seq_len, :]
    aligned_targets = targets[:, :min_seq_len, :]
    return aligned_logits, aligned_targets


def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    step,
):
    model.eval()  # Set the model to evaluation mode
    val_loss = 0
    criterion = nn.BCEWithLogitsLoss()

    with torch.no_grad():  # No gradients needed during evaluation
        progress_bar = tqdm(
            enumerate(val_dataloader), desc="Eval iter", total=len(val_dataloader)
        )
        for index, (inputs, targets) in progress_bar:
            inputs = inputs.to(args.device)
            targets = targets.to(args.device)

            output = model(inputs)
            active_logits = output.additional_logits

            # Align sequence lengths using the same function as training
            active_logits, targets = align_logits_and_targets(active_logits, targets)

            loss = criterion(active_logits, targets.float())
            val_loss += loss.item()
            progress_bar.set_postfix({"val_loss": val_loss / (index + 1)})

    val_loss /= len(val_dataloader)  # Average over all validation batches
    wandb.log({"Loss/val": val_loss}, step=step)  # Log validation loss
    print(f"✅ Validation Loss after step {step}: {val_loss:.4f} 📉")
    return val_loss
