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


def calculate_wer(predictions, targets, attention_mask=None):
    """Calculate Word Error Rate between predictions and targets."""
    # Convert logits to binary predictions
    pred_binary = (torch.sigmoid(predictions) > 0.5).float()

    # If attention mask is provided, only consider non-padded tokens
    if attention_mask is not None:
        # Expand attention mask to match the shape of predictions
        mask = attention_mask.unsqueeze(-1).expand_as(pred_binary)
        pred_binary = pred_binary * mask
        targets = targets * mask

    # Calculate token-level accuracy
    correct_tokens = (pred_binary == targets).all(dim=-1).float()
    if attention_mask is not None:
        # Only count non-padded tokens
        total_tokens = attention_mask.sum()
        correct_count = (correct_tokens * attention_mask).sum()
    else:
        total_tokens = correct_tokens.numel()
        correct_count = correct_tokens.sum()

    # WER = 1 - accuracy (error rate)
    accuracy = correct_count / total_tokens if total_tokens > 0 else 0.0
    wer = 1.0 - accuracy
    return wer.item()


def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    step,
):
    model.eval()  # Set the model to evaluation mode
    val_loss = 0
    val_wer = 0
    criterion = nn.BCEWithLogitsLoss()

    with torch.no_grad():  # No gradients needed during evaluation
        progress_bar = tqdm(
            enumerate(val_dataloader), desc="Eval iter", total=len(val_dataloader)
        )
        for index, batch in progress_bar:
            # Handle both tuple and dict batch formats
            if isinstance(batch, tuple):
                inputs, targets = batch
                attention_mask = None
            else:
                inputs = {
                    "input_ids": batch["input_ids"],
                    "attention_mask": batch["attention_mask"],
                    "token_type_ids": batch["token_type_ids"],
                }
                targets = batch["targets"]
                attention_mask = inputs["attention_mask"]

            inputs = inputs.to(args.device)
            targets = targets.to(args.device)

            output = model(inputs)
            active_logits = output.additional_logits

            # Align sequence lengths using the same function as training
            active_logits, targets = align_logits_and_targets(active_logits, targets)

            # Align attention mask if present
            if attention_mask is not None:
                attention_mask = attention_mask.to(args.device)
                attention_mask = attention_mask[:, : active_logits.size(1)]

            loss = criterion(active_logits, targets.float())
            batch_wer = calculate_wer(active_logits, targets, attention_mask)

            val_loss += loss.item()
            val_wer += batch_wer

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                    "val_wer": val_wer / (index + 1),
                }
            )

    val_loss /= len(val_dataloader)  # Average over all validation batches
    val_wer /= len(val_dataloader)

    wandb.log(
        {
            "Loss/val": val_loss,
            "WER/val": val_wer,
        },
        step=step,
    )

    print(
        f"✅ Validation Loss after step {step}: {val_loss:.4f}, WER: {val_wer:.4f} 📉"
    )
    return val_loss
