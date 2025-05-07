"""
Train from scratch:
    uv run src/train.py --device cpu --epochs 1
Train from checkpoint:
    uv run src/train.py --device cuda --epochs 5 --batch_size 8 --learning_rate 5e-4 --num_workers 2 \
        --model_checkpoint ./ckpt/step_21441_loss_0.0081/
Train with specific components:
    uv run src/train.py --device cuda --epochs 3 --components stress,prefix \
        --model_checkpoint dicta-il/dictabert-large-char-menaked
On V100:
    uv run src/train.py --device cuda --epochs 5 --batch_size 64 --num_workers 8
    TODO: we may be able to train on very large epoch, with LR tunning
"""

from config import get_opts
from data import TrainData, Collator, COMPONENT_INDICES
from train_loop import train_model
from evaluate import evaluate_model
from transformers import AutoTokenizer
from phonikud.src.model import PhoNikudModel
from torch.utils.data import DataLoader


def main():
    args = get_opts()
    components = args.components.split(",")
    print(f"🟢 Active components: {components}")
    print(f"🧠 Loading model from {args.model_checkpoint}...")

    model = PhoNikudModel.from_pretrained(args.model_checkpoint, trust_remote_code=True)
    model.to(args.device)
    model.freeze_base_model()

    frozen = [name for name in COMPONENT_INDICES if name not in components]
    if frozen:
        model.freeze_mlp_components([COMPONENT_INDICES[n] for n in frozen])

    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    collator = Collator(tokenizer, components)
    dataset = TrainData(args)

    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers,
    )

    train_model(model, tokenizer, dataloader, args, components)
    evaluate_model(model, tokenizer, args, components)


if __name__ == "__main__":
    main()
