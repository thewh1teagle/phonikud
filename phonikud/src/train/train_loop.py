import torch
from torch import nn
from tqdm import tqdm, trange
from torch.utils.tensorboard import SummaryWriter

from torch.utils.data import DataLoader
from config import TrainArgs
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from evaluate import evaluate_model
from phonikud.src.model.phonikud_model import PhoNikudModel


def train_model(
    model: PhoNikudModel,
    tokenizer: BertTokenizerFast,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    args: TrainArgs,
    writer: SummaryWriter,
):
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.ConstantLR(optimizer, total_iters=args.epochs)
    # Boosted on GPU
    scaler = torch.amp.GradScaler(args.device, enabled="cuda" in args.device)

    step = args.pre_training_step
    best_val_score = float("inf")
    early_stop_counter = 0

    for epoch in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(
            enumerate(train_dataloader), desc="Train iter", total=len(train_dataloader)
        )
        for _, (inputs, targets) in pbar:
            optimizer.zero_grad()

            # Log learning rate
            for param_group in optimizer.param_groups:
                lr = param_group["lr"]
                writer.add_scalar("LR", lr, step)

            inputs = inputs.to(args.device)
            targets = targets.to(args.device)
            # ^ shape: (batch_size, n_chars_padded, n_active_components)
            output = model(inputs)
            # ^ shape: (batch_size, n_chars_padded, 4)

            # Get only the logits for the components we're training on
            active_logits = output.additional_logits[
                :, 1:-1
            ]  # skip BOS and EOS symbols
            # active_logits = active_logits.permute(0, 2, 1)
            # targets = targets.permute(0, 2, 1)

            loss = criterion(active_logits, targets.float())

            scaler.scale(loss).backward()
            # Unscale gradients before clipping
            scaler.unscale_(optimizer)

            # Clip gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            pbar.set_description(f"Train iter (L={loss.item():.4f})")
            step += 1

            # Log total loss
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
                val_score = evaluate_model(model, val_dataloader, args, writer, step)

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
                    print(
                        f"🚨 Early stopping at epoch {epoch}, step {step}. No improvement in validation score for {args.early_stopping_patience} steps."
                    )
                    break

        # Break batch loop
        if (
            args.early_stopping_patience
            and early_stop_counter >= args.early_stopping_patience
        ):
            break

        # Evaluate each epoch
        # evaluate_model(model, val_dataloader, args, writer, step)

    final_dir = f"{args.output_dir}/loss_{loss.item():.2f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
