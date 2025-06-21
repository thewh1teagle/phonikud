from torch import nn
import torch
from src.train.config import TrainArgs
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import jiwer
import random
from src.model.phonikud_model import remove_nikud, ENHANCED_NIKUD
from src.train.data import Batch
from model.src.model.phonikud_model import (
    MenakedLogitsOutput,
    PhoNikudModel,
    ModelPredictions,
)
from typing import List, Dict
from transformers import BertTokenizerFast


def evaluate_model(
    model: PhoNikudModel,
    val_dataloader: DataLoader,
    args: TrainArgs,
    tokenizer: BertTokenizerFast,
    step: int,
    writer: SummaryWriter,
):
    model.eval()  # Set the model to evaluation mode
    val_loss: float = 0
    criterion = nn.BCEWithLogitsLoss()

    # Collect all predictions and ground truth for WER/CER calculation
    all_predictions: List[str] = []
    all_ground_truth: List[str] = []

    with torch.no_grad():  # No gradients needed during evaluation
        progress_bar = tqdm(
            enumerate(val_dataloader), desc="Eval iter", total=len(val_dataloader)
        )
        for index, batch in progress_bar:
            # Handle the new Batch class format
            batch: Batch = batch
            src_texts: List[str] = (
                batch.vocalized
            )  # Vocalized text with diacritics for comparison
            inputs: Dict[str, torch.Tensor] = batch.input
            targets: torch.Tensor = batch.outputs

            inputs = {k: v.to(args.device) for k, v in inputs.items()}
            targets = targets.to(args.device)

            # Get model predictions
            output: MenakedLogitsOutput = model.forward(inputs)
            active_logits: torch.Tensor = output.additional_logits

            loss: torch.Tensor = criterion(active_logits, targets.float())
            val_loss += loss.item()

            # Get predictions for all samples in this batch for WER/CER calculation
            predictions: ModelPredictions = model.get_predictions_from_output(output)

            # Process each sample in the batch
            for batch_idx, src_text in enumerate(src_texts):
                text_without_nikud: str = remove_nikud(
                    src_text, additional=ENHANCED_NIKUD
                )

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
                    [predictions.mobile_shva[batch_idx]],
                    [predictions.prefix[batch_idx]],
                )

                # Collect for WER/CER calculation
                all_predictions.append(predicted_texts[0])
                all_ground_truth.append(src_text)

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                }
            )

    val_loss /= len(val_dataloader)  # Average over all validation batches

    # Calculate WER and CER using jiwer
    wer = jiwer.wer(all_ground_truth, all_predictions)
    cer = jiwer.cer(all_ground_truth, all_predictions)

    # Calculate accuracies as percentages (1 - error_rate) * 100
    wer_accuracy = (1 - wer) * 100
    cer_accuracy = (1 - cer) * 100

    # Log metrics to TensorBoard
    writer.add_scalar("Loss/val", val_loss, step)
    writer.add_scalar("Metrics/WER", wer, step)
    writer.add_scalar("Metrics/CER", cer, step)
    writer.add_scalar("Metrics/WER_Accuracy", wer_accuracy, step)
    writer.add_scalar("Metrics/CER_Accuracy", cer_accuracy, step)

    # Log random text examples to TensorBoard
    num_examples = min(3, len(all_ground_truth))
    random_indices = random.sample(range(len(all_ground_truth)), num_examples)

    examples_text = ""
    for i, idx in enumerate(random_indices):
        examples_text += f"**Example {i+1}:**\n"
        examples_text += f"Source:    {all_ground_truth[idx]}\n"
        examples_text += f"Predicted: {all_predictions[idx]}\n\n"

    writer.add_text("Examples", examples_text, step)

    print(f"✅ Validation Results after step {step}:")
    print(f"   Loss: {val_loss:.4f} 📉")
    print(f"   WER:  {wer:.4f} ({wer*100:.2f}%) | Accuracy: {wer_accuracy:.2f}% 🔤")
    print(f"   CER:  {cer:.4f} ({cer*100:.2f}%) | Accuracy: {cer_accuracy:.2f}% 📝")

    return val_loss
