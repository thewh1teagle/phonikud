from tap import Tap
from typing import Literal


class TrainArgs(Tap):
    model_checkpoint: str = "dicta-il/dictabert-large-char-menaked"
    """Path or name of the pretrained model checkpoint"""

    device: Literal["cuda", "cpu"] = "cuda"
    """Device to train on (cuda or cpu)"""

    data_dir: str = "data/train"
    """Directory containing data"""

    output_dir: str = "ckpt"
    """Directory to save model checkpoints"""

    batch_size: int = 4
    """Batch size for training"""

    epochs: int = 10
    """Number of training epochs"""

    pre_training_step: int = 0
    """Resume training from this step"""

    learning_rate: float = 1e-3
    """Learning rate"""

    num_workers: int = 0
    """Number of workers for data loading"""

    checkpoint_interval: int = 1000
    """Number of steps between saving checkpoints"""

    components: str = "stress,shva,prefix"
    """Comma-separated list of components to train on (stress,shva,prefix)"""

    val_split: float = 0.1
    """Fraction of training data to use as validation (0 to disable)"""

    split_seed: int = 42
    """Random seed for train/val split"""

    use_eval_file: bool = False
    """Use data/eval/*.txt as validation set instead of splitting train"""


def get_opts():
    return TrainArgs().parse_args()
