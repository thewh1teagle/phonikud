from tap import Tap
from typing import Literal
from pathlib import Path

BASE_PATH = Path(__file__).parent / "../.."


class TrainArgs(Tap):
    model_checkpoint: str = "dicta-il/dictabert-large-char-menaked"
    "Path or name of the pretrained model checkpoint"

    device: Literal["cuda", "cpu", "mps"] = "cuda"

    data_dir: str = BASE_PATH / "data/train"
    "Path with txt files for train"

    output_dir: str = BASE_PATH / "ckpt/"
    "Path to save checkpoints"

    batch_size: int = 16
    "Batch size"

    epochs: int = 1000
    "Train epochs"

    pre_training_step: int = 0
    "Resume training from this step to preserve checkpoint name"

    learning_rate: float = 1e-3
    "Learning rate"

    early_stopping_patience = 10
    "Early stop if no improvement multiple times in checkpoint interval"

    num_workers: int = 0
    "Number of workers for data loading"

    checkpoint_interval: int = 100
    "Number of steps between saving checkpoints"

    val_split: float = 0.1
    "Fraction of training data to use as validation (0 to disable)"

    split_seed: int = 42
    "Random seed for train/val split"

    use_eval_file: bool = False
    "Use data/eval/*.txt as validation set instead of splitting train"


def get_opts():
    return TrainArgs().parse_args()
