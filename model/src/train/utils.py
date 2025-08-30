from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import torch
import json
from src.model.phonikud_model import (
    PhonikudModel,
    remove_enhanced_nikud,
    NIKUD_HASER,
    remove_nikud,
    ENHANCED_NIKUD,
)
from tqdm import tqdm
import wandb
import jiwer
import random
from torch.utils.tensorboard import SummaryWriter
from transformers import BertTokenizerFast
from model.src.model.phonikud_model import ModelPredictions, MenakedLogitsOutput
from src.train.data import Batch
import shutil
from src.model.phonikud_model import HATAMA_CHAR, VOCAL_SHVA_CHAR, PREFIX_CHAR


@dataclass
class TrainingLine:
    vocalized: str  # Vocalized text with diacritics (nikud)
    unvocalized: str  # Unvocalized text without diacritics


@dataclass
class MetricsResult:
    """Result of WER/CER calculation"""

    wer: float
    cer: float
    wer_accuracy: float
    cer_accuracy: float
    val_loss: float


def print_model_size(model: PhonikudModel):
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"💾 Total Parameters: {total_params:,}")
    print(f"🔧 Trainable Parameters: {trainable_params:,}")


def save_train_metadata(
    eval_indices: List[int],
    eval_lines: List[TrainingLine],
    val_split: float,
    split_seed: int,
    max_lines: Optional[int],
    data_dir: str,
    ckpt_dir: str,
):
    """Save eval indices with verification"""
    sorted_indices = sorted(eval_indices)

    eval_data = {
        "eval_indices": eval_indices,
        "verification": {
            "first_index": sorted_indices[0],
            "last_index": sorted_indices[-1],
            "first_line": eval_lines[sorted_indices[0]].vocalized,
            "last_line": eval_lines[sorted_indices[-1]].vocalized,
        },
        "params": {
            "val_split": val_split,
            "split_seed": split_seed,
            "max_lines": max_lines,
            "data_dir": str(data_dir),
        },
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
                    if (
                        max_lines is not None
                        and max_lines > 0
                        and len(lines) >= max_lines
                    ):
                        break

                    pbar.update(len(line.encode("utf-8")))
                    # Split lines into chunks if they are too long
                    while len(line) > max_context_length:
                        vocalized = line[:max_context_length].strip()
                        unvocalized = remove_enhanced_nikud(vocalized)
                        lines.append(TrainingLine(vocalized, unvocalized))
                        line = line[max_context_length:]

                        # Check limit after adding each chunk
                        if (
                            max_lines is not None
                            and max_lines > 0
                            and len(lines) >= max_lines
                        ):
                            break

                    if line.strip() and (
                        max_lines is None or max_lines <= 0 or len(lines) < max_lines
                    ):
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
    save_train_metadata(
        val_indices, lines, val_split, split_seed, max_lines, data_dir, ckpt_dir
    )

    # Print samples
    print("🛤️ Train samples:")
    for i in train_lines[:3]:
        print(f"\t{i.vocalized} | {i.unvocalized}")

    print("🧪 Validation samples:")
    for i in val_lines[:3]:
        print(f"\t{i.vocalized} | {i.unvocalized}")

    print(
        f"✅ Loaded {len(train_lines)} training lines and {len(val_lines)} validation lines."
    )

    return train_lines, val_lines


def calculate_wer_cer_metrics(
    predictions: List[str], ground_truth: List[str], val_loss: float = 0.0
) -> MetricsResult:
    """
    Calculate WER and CER metrics from predictions and ground truth.

    Args:
        predictions: List of predicted text strings
        ground_truth: List of ground truth text strings
        val_loss: Validation loss (optional, defaults to 0.0)

    Returns:
        MetricsResult containing WER, CER, and accuracy metrics
    """
    # Calculate WER and CER using jiwer
    wer = jiwer.wer(ground_truth, predictions)
    cer = jiwer.cer(ground_truth, predictions)

    # Handle the case where jiwer returns a dict instead of float
    if isinstance(wer, dict):
        wer = float(wer.get("wer", 0.0))
    if isinstance(cer, dict):
        cer = float(cer.get("cer", 0.0))

    # Calculate accuracies as percentages (1 - error_rate) * 100
    wer_accuracy = (1 - wer) * 100
    cer_accuracy = (1 - cer) * 100

    return MetricsResult(
        wer=wer,
        cer=cer,
        wer_accuracy=wer_accuracy,
        cer_accuracy=cer_accuracy,
        val_loss=val_loss,
    )


def log_metrics_to_tensorboard_and_wandb(
    metrics: MetricsResult,
    predictions: List[str],
    ground_truth: List[str],
    step: int,
    writer: SummaryWriter,
    phase: str = "val",
) -> None:
    """
    Log metrics and examples to TensorBoard and wandb.

    Args:
        metrics: MetricsResult containing the calculated metrics
        predictions: List of predicted text strings
        ground_truth: List of ground truth text strings
        step: Training step number
        writer: TensorBoard SummaryWriter
        phase: Phase identifier ("train" or "val")
    """
    # Log metrics to TensorBoard
    writer.add_scalar(f"Loss/{phase}", metrics.val_loss, step)
    writer.add_scalar(f"Metrics/WER_{phase}", metrics.wer, step)
    writer.add_scalar(f"Metrics/CER_{phase}", metrics.cer, step)
    writer.add_scalar(f"Metrics/WER_Accuracy_{phase}", metrics.wer_accuracy, step)
    writer.add_scalar(f"Metrics/CER_Accuracy_{phase}", metrics.cer_accuracy, step)

    # Log random text examples to TensorBoard and wandb
    num_examples = min(3, len(ground_truth))
    if num_examples > 0:
        random_indices = random.sample(range(len(ground_truth)), num_examples)

        # For TensorBoard (text format)
        examples_text = ""
        for i, idx in enumerate(random_indices):
            examples_text += f"**Example {i + 1}:**\n"
            examples_text += f"Source:    {ground_truth[idx]}\n"
            examples_text += f"Predicted: {predictions[idx]}\n\n"

        writer.add_text(f"Examples_{phase}", examples_text, step)

        # For wandb (table format) - create data list first
        table_data = []
        for idx in random_indices:
            table_data.append([ground_truth[idx], predictions[idx]])

        examples_table = wandb.Table(columns=["Source", "Prediction"], data=table_data)
        wandb.log({f"Examples_Table_{phase}": examples_table}, step=step)


def print_metrics_with_examples(
    metrics: MetricsResult,
    predictions: List[str],
    ground_truth: List[str],
    step: int,
    phase: str = "validation",
) -> None:
    """
    Print metrics and examples in a nice format.

    Args:
        metrics: MetricsResult containing the calculated metrics
        predictions: List of predicted text strings
        ground_truth: List of ground truth text strings
        step: Training step number
        phase: Phase identifier ("validation" or "training")
    """
    # Print examples with nice emojis
    num_examples = min(3, len(ground_truth))
    if num_examples > 0:
        random_indices = random.sample(range(len(ground_truth)), num_examples)
        print(f"🔤 Examples from {phase}:")
        for i in random_indices:
            print(f"   {ground_truth[i]}")
            print(f"   🔤 {predictions[i]}")
            print()

    # Print metrics summary
    emoji = "✅" if phase == "validation" else "🏃"
    phase_title = phase.capitalize()
    print(f"{emoji} {phase_title} Results after step {step}:")
    if metrics.val_loss > 0:
        print(f"   Loss: {metrics.val_loss:.4f} 📉")
    print(f"   WER:  {metrics.wer:.4f} | Accuracy: {metrics.wer_accuracy:.2f}% 🔤")
    print(f"   CER:  {metrics.cer:.4f} | Accuracy: {metrics.cer_accuracy:.2f}% 📝")


def calculate_train_batch_metrics(
    model: PhonikudModel,
    batch: Batch,
    tokenizer: BertTokenizerFast,
    output: MenakedLogitsOutput,
    loss: float,
) -> MetricsResult:
    """
    Calculate WER/CER metrics for a training batch.

    Args:
        model: The PhonikudModel instance
        batch: Training batch containing vocalized text and inputs
        tokenizer: BERT tokenizer for offset mapping
        output: Model output from forward pass
        loss: Training loss for this batch

    Returns:
        MetricsResult containing WER, CER, and accuracy metrics
    """
    # Get predictions for this batch
    predictions: ModelPredictions = model.get_predictions_from_output(output)

    batch_predictions: List[str] = []
    batch_ground_truth: List[str] = []

    # Process each sample in the batch
    for batch_idx, src_text in enumerate(batch.vocalized):
        text_without_nikud: str = remove_nikud(src_text, additional=ENHANCED_NIKUD)

        # Get offset mapping for this specific text
        tokenized_for_offsets = tokenizer(
            [text_without_nikud],
            return_offsets_mapping=True,
            return_tensors="pt",
        )
        offset_mapping = tokenized_for_offsets.offset_mapping[0]

        # Decode prediction for this sample
        predicted_texts = model.decode(
            [text_without_nikud],
            [offset_mapping],
            [predictions.nikud[batch_idx]],
            [predictions.shin[batch_idx]],
            [predictions.hatama[batch_idx]],
            [predictions.vocal_shva[batch_idx]],
            [predictions.prefix[batch_idx]],
            mark_matres_lectionis=NIKUD_HASER,
        )

        # Remove nikud from both predicted and ground truth
        predicted_texts[0] = remove_nikud(predicted_texts[0])
        src_text_clean = remove_nikud(src_text)

        batch_predictions.append(predicted_texts[0])
        batch_ground_truth.append(src_text_clean)

    # Calculate metrics using the main utility function
    return calculate_wer_cer_metrics(batch_predictions, batch_ground_truth, loss)


def save_model(model: PhonikudModel, tokenizer: BertTokenizerFast, dst_path: str):
    dst_path = Path(dst_path)
    model_dir = Path(__file__).parent / "../model"
    model_dir = model_dir.resolve()
    phonikud_modal_file = model_dir / "phonikud_model.py"
    dicta_modal_file = model_dir / "dicta_model.py"
    model_config_file = dst_path / "config.json"

    model.save_pretrained(dst_path)
    tokenizer.save_pretrained(dst_path)

    # Copy models to the new model for transformers to use
    shutil.copy(phonikud_modal_file, dst_path)
    shutil.copy(dicta_modal_file, dst_path)

    # Add auto_map to the config for transformers to use
    with open(model_config_file, "r") as f:
        config = json.load(f)

    config["auto_map"] = {"AutoModel": "phonikud_model.PhonikudModel"}

    with open(model_config_file, "w") as f:
        json.dump(config, f, indent=4)


def get_char_mask(chars_to_train: List[str]) -> torch.Tensor:
    """Returns boolean mask for [hatama, vocal_shva, prefix] channels"""
    if not chars_to_train:  # Empty list = train all
        return torch.ones(3, dtype=torch.bool)

    # Map characters to channel indices
    mask = torch.zeros(3, dtype=torch.bool)
    if HATAMA_CHAR in chars_to_train:
        mask[0] = True  # hatama
    if VOCAL_SHVA_CHAR in chars_to_train:
        mask[1] = True  # vocal_shva
    if PREFIX_CHAR in chars_to_train:
        mask[2] = True  # prefix

    return mask


def get_train_char_name(char: str) -> str:
    """Get readable name for a single character"""
    names = {
        HATAMA_CHAR: "hatama(֫)",
        VOCAL_SHVA_CHAR: "vocal_shva(ֽ)",
        PREFIX_CHAR: "prefix(|)",
    }
    return names.get(char, char)
