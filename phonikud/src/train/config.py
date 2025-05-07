from argparse import ArgumentParser


def get_opts():
    parser = ArgumentParser()

    parser.add_argument(
        "-m",
        "--model_checkpoint",
        default="dicta-il/dictabert-large-char-menaked",
        type=str,
        help="Path or name of the pretrained model checkpoint",
    )
    parser.add_argument(
        "-d",
        "--device",
        default="cuda",
        type=str,
        help="Device to train on (cuda or cpu)",
    )
    parser.add_argument(
        "-dd",
        "--data_dir",
        default="data/train",
        type=str,
        help="Directory containing data",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        default="ckpt",
        type=str,
        help="Directory to save model checkpoints",
    )
    parser.add_argument(
        "--batch_size", default=4, type=int, help="Batch size for training"
    )
    parser.add_argument(
        "--epochs", default=10, type=int, help="Number of training epochs"
    )
    parser.add_argument(
        "--pre_training_step",
        default=0,
        type=int,
        help="Resume training from this step",
    )
    parser.add_argument(
        "--learning_rate", default=1e-3, type=float, help="Learning rate"
    )
    parser.add_argument(
        "--num_workers", default=0, type=int, help="Number of workers for data loading"
    )

    parser.add_argument(
        "--checkpoint_interval",
        default=1000,
        type=int,
        help="Number of steps between saving checkpoints",
    )
    parser.add_argument(
        "--components",
        default="stress,shva,prefix",
        type=str,
        help="Comma-separated list of components to train on (stress,shva,prefix)",
    )

    parser.add_argument(
        "--val_split",
        default=0.1,
        type=float,
        help="Fraction of training data to use as validation (0 to disable)",
    )

    parser.add_argument(
        "--split_seed", default=42, type=int, help="Random seed for train/val split"
    )

    parser.add_argument(
        "--use_eval_file",
        action="store_true",
        help="Use data/eval/*.txt as validation set instead of splitting train",
    )

    return parser.parse_args()
