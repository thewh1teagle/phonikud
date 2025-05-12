import torch
from torch import nn
from tqdm import tqdm, trange
from torch.utils.tensorboard import SummaryWriter

from torch.utils.data import DataLoader
from data import COMPONENT_INDICES
from config import TrainArgs
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from evaluate import evaluate_model
from transformers import BertPreTrainedModel
from utils import load_model_checkpoint


def train_model(
    model: BertPreTrainedModel,
    tokenizer: BertTokenizerFast,
    train_dataloader: DataLoader,
    val_dataloader: DataLoader,
    args: TrainArgs,
    components,
    writer: SummaryWriter,
):
    
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    scheduler = torch.optim.lr_scheduler.ConstantLR(optimizer, total_iters=args.epochs)
    scaler = torch.amp.GradScaler(args.device)
    # Load model from checkpoint if specified
    if args.load_model:
        model, tokenizer, training_metadata = load_model_checkpoint(
            model,
            tokenizer,
            args.load_model,
            optimizer=optimizer,
            scheduler=scheduler,
            device=args.device,
        )
        # Update training metadata
        optimizer.param_groups[0]["lr"] = training_metadata["learning_rate"]
        scheduler.last_epoch = training_metadata["scheduler_last_epoch"]
        step = training_metadata["train_steps"]
        epoch = training_metadata["last_epoch"]
        best_val_score = training_metadata["last_validation_score"]
        best_val_loss = training_metadata["last_validation_loss"]
    else:
        # Initialize training metadata
        step = 0
        epoch = 0
        best_val_loss = float("inf")
        best_val_score = float("inf")


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
            # ^ shape: (batch_size, n_chars_padded, 3)

            # Get only the logits for the components we're training on
            active_indices = [COMPONENT_INDICES[comp] for comp in components]
            active_logits = output.additional_logits[
                :, 1:-1, active_indices
            ]  # # skip BOS and EOS symbols

            loss = criterion(active_logits, targets.float())

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
            # Loss per component
            for i, comp in enumerate(components):
                comp_loss = criterion(
                    active_logits[:, :, i], targets[:, :, i].float()
                ).item()
                writer.add_scalar(f"Loss/{comp}", comp_loss, step)

            if args.checkpoint_interval and step % args.checkpoint_interval == 0:
                # Always save "last"
                last_dir = f"{args.output_dir}/last"
                print(f"""💾 Saving last checkpoint at step {step} to: {last_dir}
                      (val_score={best_val_loss:.4f}),
                      (val_accuracy={best_val_score:.4f})""")
                model.save_pretrained(last_dir)
                tokenizer.save_pretrained(last_dir)

                # Evaluate and maybe save "best"
                val_loss, val_accuracy = evaluate_model(
                    model, val_dataloader, args, components, writer, step
                )

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    best_dir = f"{args.output_dir}/best"
                    print(
                        f"""🏆 New best model at step {step} (val_score={val_loss:.4f}),
                          (val_accuracy={val_accuracy:.4f}), saving to: {best_dir}"""
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
        evaluate_model(model, val_dataloader, args, components, writer, step)

    # Get final validation loss
    final_val_loss = evaluate_model(model, val_dataloader, args, components, writer, step)
    
    # Prepare metadata to save with the model
    training_metadata = {
        "learning_rate": optimizer.param_groups[0]["lr"],
        "train_steps": step,
        "last_train_loss": loss.item(),
        "last_epoch": epoch,
        "last_validation_score": best_val_score,
        "last_validation_loss": final_val_loss,
        "optimizer_step": optimizer.state_dict().get("step", 0),
        "scheduler_last_epoch": scheduler.last_epoch
    }
    
    # Update model config with training metadata
    for key, value in training_metadata.items():
        setattr(model.config, key, value)
    
    final_dir = f"{args.output_dir}/loss_{loss.item():.2f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    print(f"📊 Saved metadata: {training_metadata}")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
