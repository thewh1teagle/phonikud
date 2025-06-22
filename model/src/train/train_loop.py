from src.train.data import Batch
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm, trange
from torch.utils.data import DataLoader
from src.train.config import TrainArgs
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from src.train.evaluate import evaluate_model
from model.src.model.phonikud_model import PhoNikudModel, MenakedLogitsOutput
from typing import Dict
from datetime import datetime
from pathlib import Path
import wandb


def train_model(
    model: PhoNikudModel,
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
    wandb.tensorboard.patch(root_logdir=str(log_dir))
    wandb.init(
        project=args.wandb_project,
        entity=args.wandb_entity,
        config=vars(args),
        mode=args.wandb_mode,
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
    scaler = torch.amp.GradScaler(args.device, enabled="cuda" in args.device)

    step = args.pre_training_step
    best_val_score = float("inf")
    early_stop_counter = 0

    for epoch in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(
            enumerate(train_dataloader), desc="Train iter", total=len(train_dataloader)
        )
        total_loss = 0.0

        batch: Batch
        for index, batch in pbar:
            optimizer.zero_grad()

            # Log learning rate
            for param_group in optimizer.param_groups:
                lr = param_group["lr"]
                writer.add_scalar("LR", lr, step)

            inputs: Dict[str, torch.Tensor] = batch.input
            targets: torch.Tensor = batch.outputs
            inputs = {k: v.to(args.device) for k, v in inputs.items()}
            targets = targets.to(args.device)

            output: MenakedLogitsOutput = model(inputs)
            active_logits: torch.Tensor = output.additional_logits

            loss = criterion(active_logits, targets.float())

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
                model.save_pretrained(last_dir)
                tokenizer.save_pretrained(last_dir)

            # Val
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                # Evaluate and maybe save "best"
                val_score = evaluate_model(
                    model, val_dataloader, args, tokenizer, step, writer
                )

                if val_score < best_val_score:
                    best_val_score = val_score
                    best_dir = f"{args.output_dir}/best"
                    print(
                        f"🏆 New best model at step {step} (val_score={val_score:.4f}), saving to: {best_dir}"
                    )
                    model.save_pretrained(best_dir)
                    tokenizer.save_pretrained(best_dir)
                    early_stop_counter = 0
                else:
                    print(
                        f"📉 No improvement at step {step} (no_improvement_counter={early_stop_counter})"
                    )
                    early_stop_counter += 1

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
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
