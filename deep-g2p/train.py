"""Main training script for G2P model"""

from config import TrainingConfig
from train_loop import train


if __name__ == "__main__":
    config = TrainingConfig().parse_args()
    train(config)
