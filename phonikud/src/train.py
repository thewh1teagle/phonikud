"""
Train from scratch:
    uv run src/train.py --device cpu --epochs 1
Train from checkpoint:
    uv run src/train.py --device cuda --epochs 5 --batch_size 8 --learning_rate 5e-4 --num_workers 2 \
        --model_checkpoint ./ckpt/step_21441_loss_0.0081/
Train with specific components:
    uv run src/train.py --device cuda --epochs 3 --components stress,prefix \
        --model_checkpoint dicta-il/dictabert-large-char-menaked
"""

import re
from argparse import ArgumentParser
from transformers import AutoTokenizer
from glob import glob
import os
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, trange
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence
from model import PhoNikudModel, STRESS_CHAR, MOBILE_SHVA_CHAR, PREFIX_CHAR


def get_opts():
    parser = ArgumentParser()
    parser.add_argument(
        "-m",
        "--model_checkpoint",
        default="dicta-il/dictabert-large-char-menaked",
        type=str,
    )
    parser.add_argument("-d", "--device", default="cuda", type=str)
    parser.add_argument("-dd", "--data_dir", default="data/", type=str)
    parser.add_argument("-o", "--output_dir", default="ckpt", type=str)
    parser.add_argument("--batch_size", default=4, type=int)
    parser.add_argument("--epochs", default=10, type=int)
    parser.add_argument("--pre_training_step", default=0, type=int)
    parser.add_argument("--learning_rate", default=1e-3, type=float)
    parser.add_argument("--num_workers", default=0, type=int)
    parser.add_argument(
        "--checkpoint_interval",
        default=1000,
        type=int,
        help="Number of steps between checkpoints",
    )
    parser.add_argument(
        "--components",
        default="stress,shva,prefix",
        type=str,
        help="Comma-separated list of components to train on (stress,shva,prefix)",
    )

    return parser.parse_args()


class AnnotatedLine:
    def __init__(self, raw_text, components):
        self.components = components
        component_indices = {"stress": 0, "shva": 1, "prefix": 2}

        # Get indices for active components
        self.active_indices = [component_indices[comp] for comp in components]

        # filter based on components
        raw_text = "".join(
            char
            for char in raw_text
            if not (char == STRESS_CHAR and "stress" not in components)
            and not (char == MOBILE_SHVA_CHAR and "shva" not in components)
            and not (char == PREFIX_CHAR and "prefix" not in components)
        )

        self.text = ""  # will contain plain hebrew text
        stress = []  # will contain 0/1 for each character (1=stressed)
        mobile_shva = []  # will contain 0/1 for each character (1=mobile shva)
        prefix = []  # will contain 0/1 for each character (1=prefix)

        for i, char in enumerate(raw_text):
            if char == STRESS_CHAR:
                stress[-1] = 1
            elif char == MOBILE_SHVA_CHAR:
                mobile_shva[-1] = 1
            elif char == PREFIX_CHAR:
                prefix[-1] = 1
            else:
                self.text += char
                stress += [0]
                mobile_shva += [0]
                prefix += [0]  # No prefix for this character by default

        assert len(self.text) == len(stress) == len(mobile_shva) == len(prefix)

        # Create tensor for all features
        all_features = [
            torch.tensor(stress),
            torch.tensor(mobile_shva),
            torch.tensor(prefix),
        ]

        # Only use the features for active components
        self.target = torch.stack([all_features[i] for i in self.active_indices])
        # ^ shape: (n_active_components, n_chars)


class TrainData(Dataset):
    def __init__(self, args):
        self.max_context_length = 2048
        self.components = args.components.split(",")
        print(f"🔤 Training with components: {', '.join(self.components)}")

        files = glob(
            os.path.join(args.data_dir, "train", "**", "*.txt"), recursive=True
        )
        print(len(files), "text files found; using them for training data...")
        self.lines = self._load_lines(files)

    def _load_lines(self, files: list[str]):
        lines = []
        for file in files:
            with open(file, "r", encoding="utf-8") as fp:
                for line in fp:
                    # While the line is longer than max_context_length, split it into chunks
                    while len(line) > self.max_context_length:
                        lines.append(
                            line[: self.max_context_length].strip()
                        )  # Add the first chunk
                        line = line[
                            self.max_context_length :
                        ]  # Keep the remainder of the line

                    # Add the remaining part of the line if it fits within the max_context_length
                    if line.strip():
                        lines.append(line.strip())
        return lines

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        text = self.lines[idx]
        return AnnotatedLine(text, components=self.components)


class Collator:
    def __init__(self, tokenizer, components):
        self.tokenizer = tokenizer
        self.components = components

    def collate_fn(self, items):
        inputs = self.tokenizer(
            [x.text for x in items], padding=True, truncation=True, return_tensors="pt"
        )
        targets = pad_sequence([x.target.T for x in items], batch_first=True)
        # ^ shape: (batch_size, n_chars_padded, n_active_components)

        return inputs, targets


def main():
    args = get_opts()

    if args.pre_training_step == 0 and "ckpt/" in args.model_checkpoint:
        # Try to get pre_training_step from the name
        match = re.search(r"step_(\d+)", args.model_checkpoint)
        if match:
            args.pre_training_step = int(match.group(1))

    components = args.components.split(",")
    print(f"🧠 Loading model from {args.model_checkpoint}...")

    model = PhoNikudModel.from_pretrained(args.model_checkpoint, trust_remote_code=True)
    model.to(args.device)
    model.freeze_base_model()
    # ^ we will only train extra layers

    # Freeze components
    component_indices = {"stress": 0, "shva": 1, "prefix": 2}
    frozen_components = [
        name for name in component_indices.keys() if name not in components
    ]
    if frozen_components:
        print(f"❄️🧊 Frozen components: {', '.join(frozen_components)}")
        model.freeze_mlp_components(
            [component_indices[name] for name in frozen_components]
        )

    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    collator = Collator(tokenizer, components=components)

    print("Loading data...")
    data = TrainData(args)

    print("Training...")

    dl = DataLoader(
        data,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()

    step = 0 + args.pre_training_step
    for _ in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(dl, desc="Train iter")
        for inputs, targets in pbar:
            optimizer.zero_grad()

            inputs = inputs.to(args.device)
            targets = targets.to(args.device)
            # ^ shape: (batch_size, n_chars_padded, n_active_components)
            output = model(inputs)
            # ^ shape: (batch_size, n_chars_padded, 3)
            additional_logits = output.additional_logits

            # Get only the logits for the components we're training on
            component_indices = {"stress": 0, "shva": 1, "prefix": 2}
            active_indices = [component_indices[comp] for comp in components]
            active_logits = additional_logits[
                :, 1:-1, active_indices
            ]  # skip BOS and EOS symbols

            loss = criterion(
                active_logits,
                targets.float(),
            )

            loss.backward()
            optimizer.step()

            pbar.set_description(f"Train iter (L={loss.item():.4f})")
            step += 1

            if args.checkpoint_interval > 0 and step % args.checkpoint_interval == 0:
                save_dir = f"{args.output_dir}/last.ckpt"
                print(f"Saving checkpoint at step {step} to:", save_dir)
                model.save_pretrained(save_dir)
                tokenizer.save_pretrained(save_dir)

    epoch_loss = loss.item()
    save_dir = f"{args.output_dir}/step_{step + 1}_loss_{epoch_loss:.4f}"
    print("Saving trained model to:", save_dir)
    model.save_pretrained(save_dir)
    tokenizer.save_pretrained(save_dir)
    print("Model saved.")

    print("Testing...")

    model.eval()

    test_fn = os.path.join(args.data_dir, "test.txt")
    with open(test_fn, "r", encoding="utf-8") as f:
        test_text = f.read().strip()

    for line in test_text.splitlines():
        if not line.strip():
            continue
        print(line)
        print(model.predict([line], tokenizer, mark_matres_lectionis="*"))
        print()


if __name__ == "__main__":
    main()
