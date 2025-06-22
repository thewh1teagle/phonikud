from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import torch
import json
from src.model.phonikud_model import (
    PhoNikudModel,
    remove_enhanced_nikud,
)
from tqdm import tqdm


@dataclass
class TrainingLine:
    vocalized: str  # Vocalized text with diacritics (nikud)
    unvocalized: str  # Unvocalized text without diacritics


def print_model_size(model: PhoNikudModel):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"💾 Total Parameters: {total_params:,}")
    print(f"🔧 Trainable Parameters: {trainable_params:,}")


def save_train_metadata(eval_indices: List[int], eval_lines: List[TrainingLine], val_split: float, split_seed: int, max_lines: Optional[int], data_dir: str, ckpt_dir: str):
    """Save eval indices with verification"""
    sorted_indices = sorted(eval_indices)
    
    eval_data = {
        "eval_indices": eval_indices,
        "verification": {
            "first_index": sorted_indices[0],
            "last_index": sorted_indices[-1],
            "first_line": eval_lines[sorted_indices[0]].vocalized,
            "last_line": eval_lines[sorted_indices[-1]].vocalized
        },
        "params": {
            "val_split": val_split,
            "split_seed": split_seed,
            "max_lines": max_lines,
            "data_dir": str(data_dir)
        }
    }
    
    indices_file = Path(ckpt_dir) / "train_metadata.json"
    indices_file.parent.mkdir(parents=True, exist_ok=True)
    with open(indices_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(eval_indices)} eval indices")


def read_lines(
    data_dir: str,
    max_context_length: int = 2048,
    max_lines: Optional[int] = None,
) -> List[TrainingLine]:
    """Simple function to read lines from text files and return TrainingLine objects"""
    files = list(Path(data_dir).glob("**/*.txt"))
    total_bytes = sum(f.stat().st_size for f in files)

    lines = []
    with tqdm(
        total=total_bytes, desc="📚 Loading text files...", unit="B", unit_scale=True
    ) as pbar:
        for file in files:
            with open(file, "r", encoding="utf-8") as fp:
                for line in fp:
                    # Check if we've reached the maximum number of lines
                    if max_lines is not None and max_lines > 0 and len(lines) >= max_lines:
                        break
                        
                    pbar.update(len(line.encode("utf-8")))
                    # Split lines into chunks if they are too long
                    while len(line) > max_context_length:
                        vocalized = line[:max_context_length].strip()
                        unvocalized = remove_enhanced_nikud(vocalized)
                        lines.append(TrainingLine(vocalized, unvocalized))
                        line = line[max_context_length:]
                        
                        # Check limit after adding each chunk
                        if max_lines is not None and max_lines > 0 and len(lines) >= max_lines:
                            break

                    if line.strip() and (max_lines is None or max_lines <= 0 or len(lines) < max_lines):
                        vocalized = line.strip()
                        unvocalized = remove_enhanced_nikud(vocalized)
                        lines.append(TrainingLine(vocalized, unvocalized))
            
            # Break outer loop if we've reached the limit
            if max_lines is not None and max_lines > 0 and len(lines) >= max_lines:
                break

    return lines


def prepare_indices(
    lines: List[TrainingLine],
    val_split: float,
    split_seed: int,
) -> Tuple[List[int], List[int]]:
    """Prepare train and validation indices"""
    split_idx = int(len(lines) * (1 - val_split))
    torch.manual_seed(split_seed)
    idx = torch.randperm(len(lines))
    
    train_indices = idx[:split_idx].tolist()
    val_indices = idx[split_idx:].tolist()
    
    return train_indices, val_indices


def prepare_lines(
    data_dir: str,
    ckpt_dir: str,
    val_split: float,
    split_seed: int,
    max_lines: Optional[int] = None,
    max_context_length: int = 2048,
) -> Tuple[List[TrainingLine], List[TrainingLine]]:
    """Higher level function that reads lines, splits them, and saves metadata"""
    # Read all lines
    print("📖🔍 Reading lines from dataset...")
    lines = read_lines(data_dir, max_context_length, max_lines)
    
    # Prepare train/val split
    train_indices, val_indices = prepare_indices(lines, val_split, split_seed)
    
    # Create train and validation datasets
    train_lines = [lines[i] for i in train_indices]
    val_lines = [lines[i] for i in val_indices]
    
    # Save metadata
    save_train_metadata(val_indices, lines, val_split, split_seed, max_lines, data_dir, ckpt_dir)
    
    # Print samples
    print("🛤️ Train samples:")
    for i in train_lines[:3]:
        print(f"\t{i.vocalized} | {i.unvocalized}")

    print("🧪 Validation samples:")
    for i in val_lines[:3]:
        print(f"\t{i.vocalized} | {i.unvocalized}")
    
    print(f"✅ Loaded {len(train_lines)} training lines and {len(val_lines)} validation lines.")
    
    return train_lines, val_lines
