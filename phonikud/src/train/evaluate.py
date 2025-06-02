from torch import nn
import torch
from config import TrainArgs
from torch.utils.data import DataLoader
import wandb
from tqdm import tqdm
from utils import align_logits_and_targets, calculate_wer

def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    step,
):
    model.eval()  # Set the model to evaluation mode
    val_loss = 0
    val_wer = 0
    val_accuracy = 0  # Initialize val_accuracy
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
            batch_wer, accuracy = calculate_wer(active_logits, targets, attention_mask)

            val_loss += loss.item()
            val_wer += batch_wer
            val_accuracy += accuracy.item()  # Convert to scalar

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                    "val_wer": val_wer / (index + 1),
                    "val_accuracy": val_accuracy / (index + 1),
                    "step": step,
                }
            )

    val_loss /= len(val_dataloader)  # Average over all validation batches
    val_wer /= len(val_dataloader)
    val_accuracy /= len(val_dataloader)

    wandb.log(
        {
            "Loss/val": val_loss,
            "WER/val": val_wer,
            "Accuracy/val": val_accuracy
        },
        step=step,
    )

    print(
        f"✅ Validation Loss after step {step}: {val_loss:.4f}, WER: {val_wer:.4f}, Accuracy: {val_accuracy:.4f} 📉"
    )
    model.train()  # Set back to training mode
    return val_loss
