"""
Simple evaluation script
"""

import random
from tqdm import tqdm
from jiwer import wer, cer
from transformers import AutoTokenizer
from src.model.phonikud_model import PhoNikudModel, remove_nikud, ENHANCED_NIKUD, NIKUD_HASER
from src.train.config import TrainArgs, BASE_PATH
from src.train.utils import read_lines
from phonikud.utils import normalize
from tap import Tap


class EvalArgs(Tap):
    model: str = str(BASE_PATH / "ckpt/best_wer")
    "Model path or name"
    
    max_lines: int = TrainArgs.max_lines
    "Maximum number of lines to read from dataset (same as training)"
    
    device: str = "cuda"
    "Device to use for inference"
    
    val_split: float = TrainArgs.val_split
    "Validation split fraction"
    
    split_seed: int = TrainArgs.split_seed
    "Random seed for train/val split"
    
    data_dir: str = TrainArgs.data_dir
    "Data directory path"
    
    sample_eval: int = 0
    "Sample N lines from eval split (0 = use all eval lines)"


def main():
    args = EvalArgs().parse_args()

    # Read data exactly like training
    print("📖 Reading data (same as training)...")
    print(f"   Data dir: {args.data_dir}")
    print(f"   Max lines: {args.max_lines}")
    print(f"   Val split: {args.val_split}")
    print(f"   Split seed: {args.split_seed}")
    
    _train_lines, eval_lines = read_lines(
        args.data_dir,
        val_split=args.val_split,
        split_seed=args.split_seed,
        max_lines=args.max_lines,  # Same as training
    )
    
    # Use eval lines (optionally sample)
    eval_texts = [line.vocalized for line in eval_lines]
    if args.sample_eval > 0 and len(eval_texts) > args.sample_eval:
        eval_texts = random.sample(eval_texts, args.sample_eval)
        print(f"📝 Sampled {len(eval_texts)} lines from {len(eval_lines)} eval lines")
    else:
        print(f"📝 Using all {len(eval_texts)} eval lines")

    # Load model
    print(f"🧠 Loading model: {args.model}")
    model = PhoNikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model.to(args.device)  # type: ignore
    model.eval()

    # Evaluate
    gts, preds = [], []
    print("🔬 Evaluating...")
    
    for line in tqdm(eval_texts):
        src = remove_nikud(line, additional=ENHANCED_NIKUD)
        if not src:
            continue
        pred = model.predict([src], tokenizer, mark_matres_lectionis=NIKUD_HASER)[0]
        
        gts.append(remove_nikud(line))
        preds.append(remove_nikud(normalize(pred)))

    # Calculate metrics
    w = float(wer(gts, preds))  # type: ignore
    c = float(cer(gts, preds))  # type: ignore

    # Print examples
    print("\n🔤 Examples:")
    for i in range(min(5, len(gts))):
        print(f"   GT:   {gts[i]}")
        print(f"   Pred: {preds[i]}")
        print()

    # Print results
    print("📊 Results:")
    print(f"   Lines: {len(gts)}")
    print(f"   WER: {w:.3f} (Acc: {(1-w)*100:.1f}%)")
    print(f"   CER: {c:.3f} (Acc: {(1-c)*100:.1f}%)")


if __name__ == "__main__":
    main() 