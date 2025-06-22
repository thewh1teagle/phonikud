"""
Test train:
    uv run src/train/main.py --device mps --epochs 100 --num_workers 1 --checkpoint_interval 10
Train from scratch:
    uv run src/train/main.py --device cpu --epochs 1 --device mps
Train from checkpoint:
    uv run src/train/main.py --device cuda --epochs 5 --batch_size 8 --learning_rate 5e-4 --num_workers 2 \
        --model_checkpoint ./ckpt/step_21441_loss_0.0081/
    uv run src/train/main.py --device cuda --epochs 3 --model_checkpoint dicta-il/dictabert-large-char-menaked
On V100:
    uv run src/train/main.py --device cuda --epochs 5 --batch_size 64 --num_workers 8
    TODO: we may be able to train on very large epoch, with LR tunning
"""

from src.train.config import get_opts
from src.train.data import Collator, get_dataloader
from src.train.train_loop import train_model
from transformers import AutoTokenizer
from src.model.phonikud_model import PhoNikudModel
from src.train.utils import print_model_size, read_lines


def main():
    args = get_opts()
    print(f"🧠 Loading model from {args.model_checkpoint}...")

    model = PhoNikudModel.from_pretrained(args.model_checkpoint, trust_remote_code=True)
    print_model_size(model)

    model.to(args.device) # type: ignore
    model.freeze_base_model()

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_checkpoint, trust_remote_code=True
    )
    collator = Collator(tokenizer)

    # Data split
    print("📖🔍 Reading lines from dataset...")
    max_lines = None if args.max_lines == -1 else args.max_lines
    train_lines, val_lines = read_lines(args.data_dir, max_lines=max_lines)
    print(
        f"✅ Loaded {len(train_lines)} training lines and {len(val_lines)} validation lines."
    )

    # Data loader - provide both unvocalized and vocalized text
    train_dataloader = get_dataloader(
        [line.unvocalized for line in train_lines],
        [line.vocalized for line in train_lines],
        args,
        collator,
    )
    val_dataloader = get_dataloader(
        [line.unvocalized for line in val_lines],
        [line.vocalized for line in val_lines],
        args,
        collator,
    )

    # Train
    train_model(model, tokenizer, train_dataloader, val_dataloader, args)


if __name__ == "__main__":
    main()
