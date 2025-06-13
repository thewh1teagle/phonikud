from torch import nn
import torch
from config import TrainArgs
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import wandb
from src.model.phonikud_model import align_logits_and_targets

def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    writer: SummaryWriter,
    step,
):
    model.eval()  # Set the model to evaluation mode
    val_loss = 0
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

            val_loss += loss.item()

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                }
            )

    val_loss /= len(val_dataloader)  # Average over all validation batches

    wandb.log(
        {
            "Loss/val": val_loss,
        },
        step=step,
    )

    print(f"✅ Validation Loss after step {step}: {val_loss:.4f} 📉")
    return val_loss
