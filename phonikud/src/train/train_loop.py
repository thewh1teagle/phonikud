import torch
from torch import nn
from tqdm import tqdm, trange
import wandb

from torch.utils.data import DataLoader
from config import TrainArgs
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from evaluate import evaluate_model
from phonikud.src.model.phonikud_model import PhoNikudModel
from utils import align_logits_and_targets, calculate_wer

def train_model(
    model: PhoNikudModel,
    tokenizer: BertTokenizerFast,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    args: TrainArgs,
):
    # Initialize wandb
    wandb.init(project="phonikud", config=vars(args))
    
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
        total_wer = 0.0
        total_acc = 0.0
        batch_count = 0
        
        for index, batch in pbar:  # Change this line from (inputs, targets) to batch
            optimizer.zero_grad()

            # Log learning rate
            for param_group in optimizer.param_groups:
                lr = param_group["lr"]
                wandb.log({"LR": lr}, step=step)

            # If batch is a tuple (old format), unpack it
            if isinstance(batch, tuple):
                inputs, targets = batch
                attention_mask = None
            # If batch is a dict (new format), extract components
            else:
                inputs = {
                    "input_ids": batch["input_ids"],
                    "attention_mask": batch["attention_mask"],
                    "token_type_ids": batch["token_type_ids"] 
                }
                targets = batch["targets"]
                attention_mask = inputs["attention_mask"]

            inputs = inputs.to(args.device)
            targets = targets.to(args.device)
            if attention_mask is not None:
                attention_mask = attention_mask.to(args.device)
            
            # ^ shape: (batch_size, n_tokens_padded, n_active_components)
            output = model(inputs)
            # ^ shape: (batch_size, n_tokens_padded, 4)

            # Get only the logits for the components we're training on (classes 1-3)
            # Don't skip BOS/EOS here - handle alignment with targets instead
            active_logits = output.additional_logits
            # ^ shape: (batch_size, n_tokens_padded, 3)

            # Align sequence lengths
            active_logits, targets = align_logits_and_targets(active_logits, targets)

            loss = criterion(active_logits, targets.float())
            
            # Calculate WER for this batch
            if attention_mask is not None:
                # Align attention mask with logits
                attention_mask = attention_mask[:, :active_logits.size(1)]
            
            batch_wer, batch_accuracy = calculate_wer(active_logits, targets, attention_mask)
            total_wer += batch_wer
            total_acc += batch_accuracy.item()
            batch_count += 1

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            total_loss += loss.item() 

            pbar.set_description(f"Train iter (L={total_loss/ (index+1):.4f}, WER={total_wer/batch_count:.4f}, Acc={total_acc/batch_count:.4f})")
            step += 1

            # Log per-step metrics
            wandb.log({
                "Loss/train_step": loss.item(),
                "WER/train_step": batch_wer,
                "Accuracy/train_step": batch_accuracy.item(),
            }, step=step)

            # Early validation check before checkpoint interval
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                # Log metrics before validation
                avg_train_loss = total_loss / (index + 1)
                avg_train_wer = total_wer / batch_count
                avg_train_acc = total_acc / batch_count
                
                wandb.log({
                    "Loss/train_avg": avg_train_loss,
                    "WER/train_avg": avg_train_wer,
                    "Accuracy/train_avg": avg_train_acc,
                }, step=step)

            # Always save "last"
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                last_dir = f"{args.output_dir}/last"
                print(f"💾 Saving last checkpoint at step {step} to: {last_dir}")
                model.save_pretrained(last_dir)
                tokenizer.save_pretrained(last_dir)

            # Val
            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                # Evaluate and maybe save "best"
                val_score = evaluate_model(model, val_dataloader, args, step)

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

    final_dir = f"{args.output_dir}/loss_{loss.item():.2f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
    
    # Finish the wandb run
    wandb.finish()
