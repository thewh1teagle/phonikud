"""
Simple evaluation script
"""

import json
from pathlib import Path
from typing import List
from tqdm import tqdm
from jiwer import wer, cer
from transformers import AutoTokenizer
from src.model.phonikud_model import (
    PhonikudModel,
    remove_nikud,
    ENHANCED_NIKUD,
    NIKUD_HASER,
)
from src.train.config import BASE_PATH
from src.train.utils import read_lines, prepare_indices
from phonikud.utils import normalize
from tap import Tap


def verify_data_consistency(lines: List, eval_data: dict) -> bool:
    """Verify that the loaded data matches what was saved during training"""
    verification = eval_data.get("verification", {})

    if not verification:
        print("⚠️ No verification data")
        return True

    eval_indices = eval_data["eval_indices"]
    sorted_indices = sorted(eval_indices)
    current_first = lines[sorted_indices[0]].vocalized
    current_last = lines[sorted_indices[-1]].vocalized

    if (
        current_first == verification["first_line"]
        and current_last == verification["last_line"]
    ):
        print("✅ Content verification passed!")
        return True
    else:
        print("❌ Content verification failed!")
        print(f"   Expected first: {verification['first_line'][:50]}...")
        print(f"   Got first:      {current_first[:50]}...")
        return False


class EvalArgs(Tap):
    model: str = str(BASE_PATH / "ckpt/best_wer")
    "Model path or name"

    device: str = "cuda"
    "Device to use for inference"

    input: str = ""
    "Optional input txt file to evaluate on (if not provided, uses training validation data)"


def evaluate_model(model, tokenizer, eval_texts: List[str], device: str):
    """Evaluate model on given texts and return metrics"""
    model.to(device)  # type: ignore
    model.eval()

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
    print(f"   WER: {w:.3f} (Acc: {(1 - w) * 100:.1f}%)")
    print(f"   CER: {c:.3f} (Acc: {(1 - c) * 100:.1f}%)")

    return w, c


def eval_with_input_file(args: EvalArgs):
    """Evaluate using provided input file"""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Input file not found: {input_path}")
        return

    print(f"📖 Loading input file: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        eval_texts = [line.strip() for line in f if line.strip()]

    print(f"📝 Loaded {len(eval_texts)} lines from input file")

    # Load model
    print(f"🧠 Loading model: {args.model}")
    model = PhonikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    # Evaluate
    evaluate_model(model, tokenizer, eval_texts, args.device)


def eval_against_train_data(args: EvalArgs):
    """Evaluate against training validation data with verification"""
    # Load saved eval indices
    model_path = Path(args.model)
    indices_file = model_path.parent / "train_metadata.json"

    if not indices_file.exists():
        print(f"❌ No train_metadata.json found in {model_path}")
        print("   Run training first to generate eval indices")
        return

    print(f"📖 Loading saved eval data from: {indices_file}")
    with open(indices_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    params = eval_data["params"]
    verification = eval_data.get("verification", {})

    print(
        f"   Data params: val_split={params['val_split']}, seed={params['split_seed']}, max_lines={params['max_lines']}"
    )

    # Read all data using same params as training, but we need the original lines for verification
    print("📚 Reading data...")

    # Read all lines first
    lines = read_lines(
        data_dir=params["data_dir"],
        max_context_length=2048,  # use default
        max_lines=params["max_lines"],
    )

    # Get the validation indices
    _train_indices, val_indices = prepare_indices(
        lines, val_split=params["val_split"], split_seed=params["split_seed"]
    )

    # Create validation lines
    val_lines = [lines[i] for i in val_indices]

    # Verify content consistency
    if not verify_data_consistency(lines, eval_data):
        return

    # Use val_lines directly (same as training does)
    eval_texts = [line.vocalized for line in val_lines]

    print(f"📝 Using {len(eval_texts)} eval lines (same as training)")

    # Always print first few lines to verify they match training validation
    print(f"🔤 First 3 validation lines:")
    for i, line in enumerate(val_lines[:3]):
        print(f"   {i + 1}: {line.vocalized}")
    print(f"🔤 Last 3 validation lines:")
    for i, line in enumerate(val_lines[-3:], len(val_lines) - 2):
        print(f"   {i}: {line.vocalized}")

    # Load model
    print(f"🧠 Loading model: {args.model}")
    model = PhonikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    # Evaluate
    evaluate_model(model, tokenizer, eval_texts, args.device)


def main():
    args = EvalArgs().parse_args()

    if args.input:
        # Evaluate with input file
        eval_with_input_file(args)
    else:
        # Evaluate against training data
        eval_against_train_data(args)


if __name__ == "__main__":
    main()
