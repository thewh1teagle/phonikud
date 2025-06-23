from torch import nn
import torch
from src.train.config import TrainArgs
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
from src.model.phonikud_model import NIKUD_HASER, remove_nikud, ENHANCED_NIKUD
from src.train.data import Batch
from model.src.model.phonikud_model import (
    MenakedLogitsOutput,
    PhoNikudModel,
    ModelPredictions,
)
from typing import List
from transformers import BertTokenizerFast
from src.train.utils import (
    calculate_wer_cer_metrics,
    log_metrics_to_tensorboard_and_wandb,
    print_metrics_with_examples,
)


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
            inputs = batch.input
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
                    [predictions.vocal_shva[batch_idx]],
                    [predictions.prefix[batch_idx]],
                    mark_matres_lectionis=NIKUD_HASER,
                )

                # Remove nikud from both predicted and ground truth (Keep enhanced nikud)
                predicted_texts[0] = remove_nikud(predicted_texts[0])
                src_text = remove_nikud(src_text)

                # Collect for WER/CER calculation
                all_predictions.append(predicted_texts[0])
                all_ground_truth.append(src_text)

            progress_bar.set_postfix(
                {
                    "val_loss": val_loss / (index + 1),
                }
            )

    val_loss /= len(val_dataloader)  # Average over all validation batches

    # Calculate WER/CER metrics using utility function
    metrics = calculate_wer_cer_metrics(all_predictions, all_ground_truth, val_loss)

    # Log metrics to TensorBoard and wandb using utility function
    log_metrics_to_tensorboard_and_wandb(
        metrics, all_predictions, all_ground_truth, step, writer, "val"
    )

    # Print metrics and examples using utility function
    print_metrics_with_examples(
        metrics, all_predictions, all_ground_truth, step, "validation"
    )

    return val_loss, metrics.wer
