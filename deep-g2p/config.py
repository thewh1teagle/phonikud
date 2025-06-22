import torch
from tap import Tap


class TrainingConfig(Tap):
    data: str = "data/train.txt"  # Path to training data
    epochs: int = 100  # Number of training epochs
    batch_size: int = 32  # Batch size for training
    lr: float = 1e-3  # Learning rate
    val_split: float = 0.2  # Validation split ratio (0.0-1.0)
    patience: int = 10  # Early stopping patience
    seed: int = 42  # Random seed for reproducibility
    model_path: str = "model.pt"  # Path to save the model
    vocab_path: str = "vocab.json"  # Path to save the vocabulary
    checkpoint_interval: int = 1000  # Save checkpoint every N batches
    checkpoint_path: str = "./ckpt"  # Directory to save checkpoints
    device: str = (
        "cuda" if torch.cuda.is_available() else "cpu"
    )  # Device to use for training
