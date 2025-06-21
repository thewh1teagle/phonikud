"""
Examples:
    Evaluate on a specific file:
        uv run src/run/check_error_rate.py -m ./ckpt/last -f ./data/train/example.txt -n 100

    Evaluate on training split:
        uv run src/run/check_error_rate.py -m ./ckpt/last --split train -n 100

    Evaluate on eval/dev split:
        uv run src/run/check_error_rate.py -m ./ckpt/last --split eval -n 100
"""

import random
from pathlib import Path
from tqdm import tqdm
from jiwer import wer, cer
from transformers import AutoTokenizer
from src.model.phonikud_model import (
    PhoNikudModel,
    remove_nikud,
    ENHANCED_NIKUD,
    NIKUD_HASER,
)
from src.train.config import BASE_PATH, TrainArgs
from phonikud.utils import normalize
from tap import Tap
from src.train.utils import read_lines


class Args(Tap):
    file: str = None
    split: str = None  # 'train' or 'eval'
    model: str = BASE_PATH / "./ckpt/best"
    device: str = "cuda"
    n: int = 100

    def configure(self):
        self.add_argument("--file", "-f", help="Evaluate on specific file")
        self.add_argument(
            "--split", choices=["train", "eval"], help="Evaluate on train/eval split"
        )
        self.add_argument("--model", "-m")
        self.add_argument("--n", "-n", type=int)
        return super().configure()


def main():
    args = Args().parse_args()

    if args.file:
        lines = Path(args.file).read_text(encoding="utf-8").splitlines()
    elif args.split:
        train_lines, eval_lines = read_lines(
            TrainArgs.data_dir,
            val_split=TrainArgs.val_split,
            split_seed=TrainArgs.split_seed,
        )
        lines = train_lines if args.split == "train" else eval_lines
    else:
        raise ValueError("You must provide either --file or --split")

    lines = [normalize(l.strip()) for l in lines if l.strip()]
    lines = random.sample(lines, min(args.n, len(lines)))

    model = PhoNikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model.to(args.device)
    model.eval()

    gts, preds = [], []

    for line in tqdm(lines, desc="Evaluating"):
        src = remove_nikud(line, additional=ENHANCED_NIKUD)
        if not src:
            continue
        pred = model.predict([src], tokenizer, mark_matres_lectionis=NIKUD_HASER)[0]
        gts.append(remove_nikud(line))
        preds.append(remove_nikud(normalize(pred)))

    w = wer(gts, preds)  # wer
    c = cer(gts, preds)  # cer

    print("\n📊 Evaluation Report:")
    print(f"📝 Lines evaluated: {len(gts)}")

    print(f"📉 WER: {w:.3f} (Acc: {(1 - w) * 100:.1f}%)")
    print(f"🔡 CER: {c:.3f} (Acc: {(1 - c) * 100:.1f}%)")


if __name__ == "__main__":
    main()
