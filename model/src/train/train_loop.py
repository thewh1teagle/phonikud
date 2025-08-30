from src.train.data import Batch
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm, trange
from torch.utils.data import DataLoader
from src.train.config import TrainArgs
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from src.train.evaluate import evaluate_model
from model.src.model.phonikud_model import PhonikudModel, MenakedLogitsOutput
from datetime import datetime
from pathlib import Path
import wandb
from src.train.utils import (
    calculate_train_batch_metrics,
    save_model,
    get_char_mask,
    get_train_char_name,
)


def train_model(
    model: PhonikudModel,
    tokenizer: BertTokenizerFast,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    args: TrainArgs,
):
    # Create run name with timestamp
    run_name = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize wandb with TensorBoard sync
    log_dir = Path(args.log_dir) / run_name
    log_dir.mkdir(parents=True, exist_ok=True)
    wandb.tensorboard.patch(root_logdir=str(log_dir))  # type: ignore
    wandb.init(
        project=args.wandb_project,
        entity=args.wandb_entity,
        config=vars(args),
        mode=args.wandb_mode,  # type: ignore
        name=run_name,
        sync_tensorboard=True,
    )
    print(f"🔗 Wandb syncing from TensorBoard (mode: {args.wandb_mode})")

    # Initialize TensorBoard (convert Path to string for wandb compatibility)
    writer = SummaryWriter(str(log_dir))
    print(f"📊 TensorBoard logging to: {log_dir}")
    print(f"    View with: tensorboard --logdir {args.log_dir}")

    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.StepLR(
        optimizer,
        step_size=9000,
        gamma=0.1,
    )
    # Boosted on GPU
    scaler = torch.amp.GradScaler(args.device, enabled="cuda" in args.device)  # type: ignore

    step = args.pre_training_step
    best_val_score = float("inf")
    best_wer = float("inf")  # Track best WER
    early_stop_counter = 0

    # Setup character-specific training
    char_mask = get_char_mask(args.train_chars).to(args.device)

    if len(args.train_chars) == 3:
        print("🎯 Training on all characters")
    else:
        names = [get_train_char_name(char) for char in args.train_chars]
        print(f"🎯 Training only on: {', '.join(names)}")

    for epoch in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(
            enumerate(train_dataloader), desc="Train iter", total=len(train_dataloader)
        )
        total_loss = 0.0

        batch: Batch
        for _index, batch in pbar:
            optimizer.zero_grad()

            # Log learning rate
            for param_group in optimizer.param_groups:
                lr = param_group["lr"]
                writer.add_scalar("LR", lr, step)

            inputs = batch.input
            targets: torch.Tensor = batch.outputs
            inputs = {k: v.to(args.device) for k, v in inputs.items()}
            targets = targets.to(args.device)

            output: MenakedLogitsOutput = model(inputs)
            logits: torch.Tensor = output.additional_logits

            # Apply selective training mask
            if len(args.train_chars) < 3:  # Only mask if not training all chars
                logits = logits * char_mask.float()
                targets = targets * char_mask.float()

            loss = criterion(logits, targets.float())

            scaler.scale(loss).backward()
            # Unscale gradients before clipping
            scaler.unscale_(optimizer)

            # Clip gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            total_loss += loss.item()

            pbar.set_description(f"Train iter (L={loss.item():.4f})")
            step += 1

            # Log training loss
            writer.add_scalar("Loss/train", loss.item(), step)

            # Always save "last"
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                last_dir = f"{args.output_dir}/last"
                print(f"💾 Saving last checkpoint at step {step} to: {last_dir}")
                save_model(model, tokenizer, last_dir)

            # Val
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                # Calculate training metrics before evaluation
                try:
                    train_metrics = calculate_train_batch_metrics(
                        model, batch, tokenizer, output, loss.item()
                    )

                    # Log training metrics to TensorBoard
                    writer.add_scalar("Metrics/WER_train", train_metrics.wer, step)
                    writer.add_scalar("Metrics/CER_train", train_metrics.cer, step)
                    writer.add_scalar(
                        "Metrics/WER_Accuracy_train", train_metrics.wer_accuracy, step
                    )
                    writer.add_scalar(
                        "Metrics/CER_Accuracy_train", train_metrics.cer_accuracy, step
                    )

                    print(
                        f"🏃 Training WER at step {step}: {train_metrics.wer:.4f} ({train_metrics.wer_accuracy:.2f}% accuracy)"
                    )

                except Exception as e:
                    print(f"⚠️ Could not calculate training WER/CER at step {step}: {e}")

                # Evaluate and maybe save "best"
                val_score, wer = evaluate_model(
                    model, val_dataloader, args, tokenizer, step, writer
                )

                # Track best validation loss
                if val_score < best_val_score:
                    best_val_score = val_score
                    best_dir = f"{args.output_dir}/best"
                    print(
                        f"🏆 New best model (loss) at step {step} (val_score={val_score:.4f}), saving to: {best_dir}"
                    )
                    save_model(model, tokenizer, best_dir)
                    early_stop_counter = 0
                else:
                    print(
                        f"📉 No improvement in loss at step {step} (no_improvement_counter={early_stop_counter})"
                    )
                    early_stop_counter += 1

                # Track best WER separately
                if wer < best_wer:
                    best_wer = wer
                    best_wer_dir = f"{args.output_dir}/best_wer"
                    print(
                        f"🎯 New best WER at step {step} (WER={wer:.4f}), saving to: {best_wer_dir}"
                    )
                    save_model(model, tokenizer, best_wer_dir)

                    # Save WER info to a text file in the checkpoint directory
                    wer_info_path = Path(best_wer_dir) / "wer_info.txt"
                    with open(wer_info_path, "w") as f:
                        f.write(f"Best WER: {wer:.6f}\n")
                        f.write(f"Step: {step}\n")
                        f.write(f"Validation Loss: {val_score:.6f}\n")
                        f.write(f"WER Accuracy: {(1 - wer) * 100:.2f}%\n")
                else:
                    print(
                        f"📊 No WER improvement at step {step} (current WER={wer:.4f}, best WER={best_wer:.4f})"
                    )

                if (
                    args.early_stopping_patience
                    and early_stop_counter > args.early_stopping_patience
                ):
                    break

        # Break batch loop
        if (
            args.early_stopping_patience
            and early_stop_counter >= args.early_stopping_patience
        ):
            print(
                f"🚨 Early stopping at epoch {epoch}, step {step}. No improvement in validation score for {args.early_stopping_patience} steps."
            )
            break

    # Close loggers
    writer.close()
    wandb.finish()
    print("📊 TensorBoard logging closed")
    print("🔗 Wandb sync finished")

    final_dir = f"{args.output_dir}/loss_{loss.item():.2f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    save_model(model, tokenizer, final_dir)

    # Print final summary
    print("\n🏁 Training Summary:")
    print(f"   Best Validation Loss: {best_val_score:.4f}")
    print(f"   Best WER: {best_wer:.4f} ({(1 - best_wer) * 100:.2f}% accuracy)")
