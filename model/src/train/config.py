from tap import Tap
from typing import Literal
from pathlib import Path

BASE_PATH = Path(__file__).parent / "../.."


class TrainArgs(Tap):
    model_checkpoint: str = (
        "dicta-il/dictabert-large-char-menaked"  # "thewh1teagle/phonikud"
    )
    "Path or name of the pretrained model checkpoint"

    device: Literal["cuda", "cuda:1", "cpu", "mps"] = "cuda:1"

    data_dir: Path = BASE_PATH / "data/"
    "Path with txt files for train"

    output_dir: Path = BASE_PATH / "ckpt/"
    "Path to save checkpoints"

    log_dir: Path = BASE_PATH / "logs/"
    "Path to save TensorBoard logs"

    batch_size: int = 32
    "Batch size"

    epochs: int = 20
    "Train epochs"

    pre_training_step: int = 0
    "Resume training from this step to preserve checkpoint name"

    learning_rate: float = 5e-3
    "Learning rate"

    early_stopping_patience: int = 3
    "Early stop if no improvement multiple times in checkpoint interval. Set to 0 to disable early stopping."

    num_workers: int = 16
    "Number of workers for data loading"

    checkpoint_interval: int = 9000
    "Number of steps between saving checkpoints"

    val_split: float = 0.05
    "Fraction of training data to use as validation (0 to disable)"

    split_seed: int = 42
    "Random seed for train/val split"

    max_lines: int = 0
    "Maximum number of lines to read from dataset (0 for no limit)"

    # Wandb configuration (for TensorBoard sync)
    wandb_entity: str = "Phonikud"
    "Team or username for Weights & Biases"

    wandb_project: str = "phonikud"
    "Project name for Weights & Biases"

    wandb_mode: str = "offline"
    "Wandb mode: 'online', 'offline', or 'disabled' (default: offline for local use)"


def get_opts():
    return TrainArgs().parse_args()
