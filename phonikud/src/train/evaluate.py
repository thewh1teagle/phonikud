from torch import nn
import torch
from config import TrainArgs
from torch.utils.data import DataLoader
import wandb
from tqdm import tqdm
from utils import calculate_wer, FocalLoss

def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    step,
    criterion: nn.Module
):
    model.eval()
    val_loss = 0
    val_wer = 0
    val_accuracy = 0

    with torch.no_grad():
        progress_bar = tqdm(
            enumerate(val_dataloader), desc="Eval iter", total=len(val_dataloader)
        )
        for index, batch in progress_bar:
            inputs = {
                "input_ids": batch["input_ids"],
                "attention_mask": batch["attention_mask"],
                "token_type_ids": batch["token_type_ids"],
            }
            targets = batch["targets"]
            attention_mask = batch["attention_mask"]

            inputs = {k: v.to(args.device) for k, v in inputs.items()}
            targets = targets.to(args.device)
            attention_mask = attention_mask.to(args.device)

            output = model(inputs)
            logits = output.additional_logits

            loss = criterion(logits, targets)
            batch_wer, accuracy = calculate_wer(logits, targets, attention_mask)

            val_loss += loss.item()
            val_wer += batch_wer
            val_accuracy += accuracy.item()

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                    "val_wer": val_wer / (index + 1),
                    "val_accuracy": val_accuracy / (index + 1),
                    "step": step,
                }
            )

    val_loss /= len(val_dataloader)
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
    model.train()
    return val_loss

