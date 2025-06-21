"""
uv run src/test.py --device cuda
"""

from src.model.phonikud_model import (
    PhoNikudModel,
    NIKUD_HASER,
    remove_nikud,
    PHONETIC_NIKUD,
)
from src.train.config import BASE_PATH
from transformers import AutoTokenizer
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from tap import Tap
from mishkal.utils import normalize
import torch
from jiwer import wer
import random
from tqdm import tqdm

def get_wer(reference: str, hypothesis: str) -> float:
    return wer(reference, hypothesis)




class RunArgs(Tap):
    model: str = BASE_PATH / "./ckpt/best"  # --model, -m
    device = "cuda"
    file: str = BASE_PATH / "./data/train/knesset_nikud_v6.txt"
    val_split: float = 0.05  # Fraction of training data to use as validation (0 to disable)
    split_seed: int = 42

    def configure(self):
        self.add_argument("--model", "-m", help="Path to the model checkpoint")
        return super().configure()


def main():
    args = RunArgs().parse_args()
    model = PhoNikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer: BertTokenizerFast = AutoTokenizer.from_pretrained(args.model)
    model.to(args.device)
    model.eval()
    
    # Read all lines from file
    with open(args.file, "r", encoding="utf-8") as fp:
        all_lines = [line.strip() for line in fp if line.strip()]
    
    # Split data if val_split > 0 - match training approach
    if args.val_split > 0:
        split_idx = int(len(all_lines) * (1 - args.val_split))
        torch.manual_seed(args.split_seed)
        idx = torch.randperm(len(all_lines))
        train_lines = [all_lines[i] for i in idx[:split_idx]]
        val_lines = [all_lines[i] for i in idx[split_idx:]]
        print(f"Split data: {len(train_lines)} training, {len(val_lines)} validation")
    else:
        train_lines = all_lines
        val_lines = []
    
    # Process training data
    print("Processing training data...")
    total_wer = 0.0
    total_count = 0
    
    for src in tqdm(val_lines[:100]):  # Changed from val_lines to train_lines
        src = normalize(src)
        without_nikud = remove_nikud(src, additional=PHONETIC_NIKUD)
        if not without_nikud:
            continue
        predicted = model.predict(
            [without_nikud], tokenizer, mark_matres_lectionis=NIKUD_HASER
        )[0]
        predicted = normalize(predicted)
        src, predicted = remove_nikud(src), remove_nikud(predicted)
        print()
        print(src == predicted, get_wer(predicted, src))
        print(without_nikud)
        print(src)
        print(predicted)
        total_wer += get_wer(predicted, src)
        total_count += 1
    
    print(f"Training Average WER: {total_wer / total_count if total_count > 0 else 0:.4f}")
    
    # Process validation data if available
    if val_lines:
        print("\nProcessing validation data...")
        val_wer = 0.0
        val_count = 0
        
        for src in val_lines:
            src = normalize(src)
            without_nikud = remove_nikud(src, additional=PHONETIC_NIKUD)
            if not without_nikud:
                continue
            predicted = model.predict(
                [without_nikud], tokenizer, mark_matres_lectionis=NIKUD_HASER
            )[0]
            predicted = normalize(predicted)
            src, predicted = remove_nikud(src), remove_nikud(predicted)
            val_wer += get_wer(predicted, src)
            val_count += 1
        
        print(f"Validation Average WER: {val_wer / val_count if val_count > 0 else 0:.4f}")


if __name__ == "__main__":
    main()
