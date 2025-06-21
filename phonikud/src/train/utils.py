from pathlib import Path
from typing import List, Tuple

import humanize
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from phonikud.src.model.phonikud_model import (
    NIKUD_HASER,
    remove_nikud,
)
from tqdm import tqdm


class FocalLossBCE(torch.nn.Module):
    def __init__(
            self,
            alpha: float = 0.25,
            gamma: float = 2,
            reduction: str = "mean",
            bce_weight: float = 1.0,
            focal_weight: float = 1.0,
    ):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.bce = torch.nn.BCEWithLogitsLoss(reduction=reduction)
        self.bce_weight = bce_weight
        self.focal_weight = focal_weight

    def forward(self, logits, targets):
        focall_loss = torchvision.ops.focal_loss.sigmoid_focal_loss(
            inputs=logits,
            targets=targets,
            alpha=self.alpha,
            gamma=self.gamma,
            reduction=self.reduction,
        )
        bce_loss = self.bce(logits, targets)
        return self.bce_weight * bce_loss + self.focal_weight * focall_loss



class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance in multi-label classification.
    """
    def __init__(self, alpha=0.25, gamma=2, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        """
        Args:
            inputs: logits of shape (N, C) or (N, L, C)
            targets: binary targets of shape (N, C) or (N, L, C)
        """
        # Apply sigmoid to get probabilities
        probs = torch.sigmoid(inputs)
        
        # Calculate binary cross entropy
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        
        # Calculate focal weight
        pt = torch.where(targets == 1, probs, 1 - probs)
        focal_weight = self.alpha * (1 - pt) ** self.gamma
        
        # Apply focal weight
        focal_loss = focal_weight * bce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


def print_model_size(model):
    def count_params(module):
        return sum(p.numel() for p in module.parameters())

    def pretty(n):
        return humanize.intword(n)

    print("🔍 Model breakdown:")
    print(f"  ⚙️  MLP: {pretty(count_params(model.mlp))} parameters")
    print(f"  📘 Menaked: {pretty(count_params(model.menaked))} parameters")
    print(f"  🧠  BERT: {pretty(count_params(model.bert))} parameters")


def read_lines(
    data_path: str,
    max_context_length: int = 2048,
    val_split: float = 0.1,
    split_seed: int = 42,
) -> Tuple[List[str], List[str]]:
    files = list(Path(data_path).glob("**/*.txt"))
    total_bytes = sum(f.stat().st_size for f in files)

    lines = []
    with tqdm(
        total=total_bytes, desc="📚 Loading text files...", unit="B", unit_scale=True
    ) as pbar:
        for file in files:
            with open(file, "r", encoding="utf-8") as fp:
                for line in fp:
                    pbar.update(len(line.encode("utf-8")))
                    # Split lines into chunks if they are too long
                    while len(line) > max_context_length:
                        lines.append(line[:max_context_length].strip())
                        line = line[max_context_length:]

                    if line.strip():
                        lines.append(line.strip())

    # Preprocess lines (remove nikud and other components)
    lines = [remove_nikud(i, additional=NIKUD_HASER) for i in lines]

    # Split into train and validation sets
    split_idx = int(len(lines) * (1 - val_split))
    torch.manual_seed(split_seed)
    idx = torch.randperm(len(lines))
    train_lines = [lines[i] for i in idx[:split_idx]]
    val_lines = [lines[i] for i in idx[split_idx:]]

    # Print samples
    print("🛤️ Train samples:")
    for i in train_lines[:3]:
        print(f"\t{i}")
    print("🧪 Validation samples:")
    for i in val_lines[:3]:
        print(f"\t{i}")

    return train_lines, val_lines


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
    return wer.item(), accuracy
