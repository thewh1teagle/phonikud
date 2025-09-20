#!/usr/bin/env python3
"""
Create evaluation report comparing ground truth vs predictions
"""

import json
from pathlib import Path
import pandas as pd
from typing import List
from tqdm import tqdm
from transformers import AutoTokenizer
from src.model.phonikud_model import (
    PhonikudModel,
    NIKUD_HASER,
    remove_nikud,
    ENHANCED_NIKUD,
    HATAMA_CHAR,
    VOCAL_SHVA_CHAR,
    PREFIX_CHAR,
)
from src.train.utils import read_lines, prepare_indices, filter_to_trained_chars
from src.train.config import BASE_PATH
from phonikud.utils import normalize
from tap import Tap


class EvalReportArgs(Tap):
    base_model: str = "thewh1teagle/phonikud"
    "Base model path or name"

    finetuned_model: str = str(BASE_PATH / "ckpt/best_wer")
    "Fine-tuned model path"

    device: str = "cuda"
    "Device for inference"

    output_file: str = "model_comparison"
    "Output filename (without extension)"

    train_chars: List[str] = [
        HATAMA_CHAR
    ]  # [HATAMA_CHAR, VOCAL_SHVA_CHAR, PREFIX_CHAR]
    "Characters that were trained on. Will only evaluate on these chars (others removed from comparison)"


def main():
    args = EvalReportArgs().parse_args()
    
    print("📊 Creating Evaluation Report...")
    
    # Load training metadata to get the same validation split
    metadata_file = BASE_PATH / "ckpt/train_metadata.json"
    
    if not metadata_file.exists():
        print(f"❌ No train_metadata.json found at {metadata_file}")
        print("   Run training first to generate metadata")
        return
    
    print(f"📖 Loading training metadata from: {metadata_file}")
    with open(metadata_file, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
    
    params = eval_data["params"]
    print(f"   Data params: val_split={params['val_split']}, seed={params['split_seed']}, max_lines={params['max_lines']}")
    
    # Read all data using same params as training
    print("📚 Reading training data...")
    lines = read_lines(
        data_dir=params["data_dir"],
        max_context_length=2048,
        max_lines=params["max_lines"],
    )
    
    # Get the same validation indices used during training
    _train_indices, val_indices = prepare_indices(
        lines, 
        val_split=params["val_split"], 
        split_seed=params["split_seed"]
    )
    
    # Create validation lines
    val_lines = [lines[i] for i in val_indices]
    print(f"📝 Using {len(val_lines)} validation lines (same as training)")
    
    # Load both models
    print(f"🧠 Loading base model: {args.base_model}")
    base_model = PhonikudModel.from_pretrained(args.base_model, trust_remote_code=True)
    base_tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    base_model.to(args.device)
    base_model.eval()

    print(f"🧠 Loading fine-tuned model: {args.finetuned_model}")
    finetuned_model = PhonikudModel.from_pretrained(args.finetuned_model, trust_remote_code=True)
    finetuned_tokenizer = AutoTokenizer.from_pretrained(args.finetuned_model)
    finetuned_model.to(args.device)
    finetuned_model.eval()
    
    # Print evaluation mode info
    if len(args.train_chars) == 3:
        print("🔬 Evaluating on all characters...")
    else:
        from src.train.utils import get_train_char_name
        char_names = [get_train_char_name(char) for char in args.train_chars]
        print(f"🎯 Evaluating only on: {', '.join(char_names)}")
    
    # Run predictions
    print("🔮 Running predictions...")
    results = []
    
    for i, line in enumerate(tqdm(val_lines, desc="Processing")):
        # Original vocalized text (ground truth)
        gt_original = line.vocalized
        
        # Remove enhanced nikud to get input text  
        input_text = remove_nikud(gt_original, additional=ENHANCED_NIKUD)
        
        if not input_text.strip():
            continue
            
        # Get predictions from both models
        try:
            base_prediction = base_model.predict([input_text], base_tokenizer, mark_matres_lectionis=NIKUD_HASER)[0]
            base_prediction = normalize(base_prediction)
        except Exception as e:
            print(f"⚠️ Error predicting line {i} with base model: {e}")
            base_prediction = input_text  # Fallback to input

        try:
            finetuned_prediction = finetuned_model.predict([input_text], finetuned_tokenizer, mark_matres_lectionis=NIKUD_HASER)[0]
            finetuned_prediction = normalize(finetuned_prediction)
        except Exception as e:
            print(f"⚠️ Error predicting line {i} with fine-tuned model: {e}")
            finetuned_prediction = input_text  # Fallback to input
        
        # Process for comparison (remove standard nikud, keep enhanced)
        gt_processed = remove_nikud(gt_original)
        base_processed = remove_nikud(base_prediction)
        finetuned_processed = remove_nikud(finetuned_prediction)
        
        # Apply character filtering if training on specific chars
        if len(args.train_chars) < 3:
            gt_processed = filter_to_trained_chars(gt_processed, args.train_chars)
            base_processed = filter_to_trained_chars(base_processed, args.train_chars)
            finetuned_processed = filter_to_trained_chars(finetuned_processed, args.train_chars)
        
        # Check if correct
        base_correct = 1 if gt_processed.strip() == base_processed.strip() else 0
        finetuned_correct = 1 if gt_processed.strip() == finetuned_processed.strip() else 0
        
        results.append({
            'gt': gt_processed.strip(), 
            'base': base_processed.strip(),
            'finetuned': finetuned_processed.strip(),
            'base_correct': base_correct,
            'finetuned_correct': finetuned_correct
        })
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Save CSV
    csv_file = f"{args.output_file}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"💾 Saved CSV: {csv_file}")
    
    # Calculate metrics for both models
    total_lines = len(results)
    base_correct_lines = df['base_correct'].sum()
    finetuned_correct_lines = df['finetuned_correct'].sum()
    base_accuracy = (base_correct_lines / total_lines * 100) if total_lines > 0 else 0
    finetuned_accuracy = (finetuned_correct_lines / total_lines * 100) if total_lines > 0 else 0
    improvement = finetuned_accuracy - base_accuracy
    
    # Write summary
    summary = f"""
📊 MODEL COMPARISON SUMMARY
===========================

Dataset Information:
- Total validation lines: {total_lines}
- Base model: {args.base_model}
- Fine-tuned model: {args.finetuned_model}
- Characters evaluated: {', '.join([get_train_char_name(char) for char in args.train_chars]) if len(args.train_chars) < 3 else 'All characters'}

Base Model Results:
- Correct predictions: {base_correct_lines}
- Incorrect predictions: {total_lines - base_correct_lines}
- Line accuracy: {base_accuracy:.2f}%

Fine-tuned Model Results:
- Correct predictions: {finetuned_correct_lines}
- Incorrect predictions: {total_lines - finetuned_correct_lines}
- Line accuracy: {finetuned_accuracy:.2f}%

Improvement:
- Accuracy improvement: {improvement:+.2f}% ({finetuned_correct_lines - base_correct_lines:+d} lines)

Files created:
- {csv_file} (CSV format)

Note: This is line-by-line accuracy (exact match).
For word-level or character-level error rates, use WER/CER metrics.
"""

    print(summary)
    
    # Save summary to file
    summary_file = f"{args.output_file}_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"📄 Saved summary: {summary_file}")


if __name__ == "__main__":
    main()
