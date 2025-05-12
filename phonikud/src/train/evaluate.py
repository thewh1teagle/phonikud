from torch import nn
import torch
from data import COMPONENT_INDICES
from config import TrainArgs
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


def calculate_accuracy(predictions, targets):
    """
    Calculate accuracy metrics from binary predictions and targets
    
    Args:
        predictions: Binary tensor of shape (batch_size, seq_len, n_components)
        targets: Binary tensor of shape (batch_size, seq_len, n_components)
    
    Returns:
        dict: Dictionary containing accuracy metrics
    """
    # Overall accuracy (all components)
    correct = (predictions == targets).float()
    
    # Create mask for valid positions (non-padding)
    valid_mask = (targets.sum(dim=2) > 0).float()
    n_valid = valid_mask.sum().item()
    
    # Calculate accuracy metrics
    overall_accuracy = (correct.sum(dim=2) * valid_mask).sum().item() / (n_valid * targets.size(2)) if n_valid > 0 else 0
    
    # Per-component accuracy
    component_accuracy = {}
    for i in range(targets.size(2)):
        comp_correct = (predictions[:, :, i] == targets[:, :, i]).float() * valid_mask
        comp_accuracy = comp_correct.sum().item() / n_valid if n_valid > 0 else 0
        component_accuracy[f"component_{i}"] = comp_accuracy
    
    # Calculate F1 score components
    true_positives = ((predictions == 1) & (targets == 1)).float().sum(dim=(0, 1))
    false_positives = ((predictions == 1) & (targets == 0)).float().sum(dim=(0, 1))
    false_negatives = ((predictions == 0) & (targets == 1)).float().sum(dim=(0, 1))
    
    # Per-component precision, recall, f1
    precision = {}
    recall = {}
    f1 = {}
    
    for i in range(targets.size(2)):
        prec = true_positives[i] / (true_positives[i] + false_positives[i]) if (true_positives[i] + false_positives[i]) > 0 else 0
        rec = true_positives[i] / (true_positives[i] + false_negatives[i]) if (true_positives[i] + false_negatives[i]) > 0 else 0
        
        precision[f"component_{i}"] = prec.item()
        recall[f"component_{i}"] = rec.item()
        f1[f"component_{i}"] = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        if isinstance(f1[f"component_{i}"], torch.Tensor):
            f1[f"component_{i}"] = f1[f"component_{i}"].item()
    
    # Overall precision, recall, f1
    overall_tp = true_positives.sum().item()
    overall_fp = false_positives.sum().item()
    overall_fn = false_negatives.sum().item()
    
    overall_precision = overall_tp / (overall_tp + overall_fp) if (overall_tp + overall_fp) > 0 else 0
    overall_recall = overall_tp / (overall_tp + overall_fn) if (overall_tp + overall_fn) > 0 else 0
    overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0
    
    return {
        "accuracy": overall_accuracy,
        "precision": overall_precision,
        "recall": overall_recall,
        "f1": overall_f1,
        "component_accuracy": component_accuracy,
        "component_precision": precision,
        "component_recall": recall,
        "component_f1": f1
    }


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
    
    # Initialize accuracy tracking
    all_predictions = []
    all_targets = []

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
            
            # Get binary predictions
            predictions = (torch.sigmoid(active_logits) > 0.5).float()
            
            # Store predictions and targets for accuracy calculation
            all_predictions.append(predictions.cpu())
            all_targets.append(targets.cpu())

    val_loss /= len(val_dataloader)  # Average over all validation batches
    writer.add_scalar("Loss/val", val_loss, step)  # Log validation loss
    
    # Concatenate all batches
    all_predictions = torch.cat(all_predictions, dim=0)
    all_targets = torch.cat(all_targets, dim=0)
    
    # Calculate accuracy metrics
    accuracy_metrics = calculate_accuracy(all_predictions, all_targets)
    
    # Log accuracy metrics
    writer.add_scalar("Accuracy/val", accuracy_metrics["accuracy"], step)
    writer.add_scalar("F1/val", accuracy_metrics["f1"], step)
    
    # Log component-specific metrics
    for i, comp in enumerate(components):
        writer.add_scalar(f"Accuracy/{comp}", accuracy_metrics["component_accuracy"][f"component_{i}"], step)
        writer.add_scalar(f"F1/{comp}", accuracy_metrics["component_f1"][f"component_{i}"], step)
    
    print(f"✅ Validation Loss after step {step}: {val_loss:.4f} 📉")
    print(f"📊 Overall Accuracy: {accuracy_metrics['accuracy']:.4f}, F1: {accuracy_metrics['f1']:.4f}")
    
    # Return both loss and accuracy metrics
    return val_loss, accuracy_metrics.get("overall_accuracy", 0)
