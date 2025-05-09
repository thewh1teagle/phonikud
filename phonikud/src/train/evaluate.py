from torch import nn
import torch
from data import COMPONENT_INDICES
from config import TrainArgs
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


def evaluate_model(
    model,
    val_dataloader: DataLoader,
    args: TrainArgs,
    components,
    writer: SummaryWriter,
    step,
):
    model.eval()  # Set the model to evaluation mode
    val_loss = 0
    criterion = nn.BCEWithLogitsLoss()

    with torch.no_grad():  # No gradients needed during evaluation
        for inputs, targets in tqdm(val_dataloader, desc="Evaluating 🧠"):
            inputs = inputs.to(args.device)
            targets = targets.to(args.device)

            output = model(inputs)
            active_indices = [COMPONENT_INDICES[comp] for comp in components]
            active_logits = output.additional_logits[
                :, 1:-1, active_indices
            ]  # skip BOS and EOS

            loss = criterion(active_logits, targets.float())
            val_loss += loss.item()

    val_loss /= len(val_dataloader)  # Average over all validation batches
    writer.add_scalar("Loss/val", val_loss, step)  # Log validation loss
    print(f"✅ Validation Loss after step {step}: {val_loss:.4f} 📉")
    return val_loss
