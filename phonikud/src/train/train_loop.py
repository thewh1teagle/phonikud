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
    step = args.pre_training_step
    best_val_score = float("inf")
    no_improvement_counter = 0

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
            loss.backward()

            optimizer.step()
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
                print(f"💾 Saving last checkpoint at step {step} to: {last_dir}")
                model.save_pretrained(last_dir)
                tokenizer.save_pretrained(last_dir)

                # Evaluate and maybe save "best"
                val_score = evaluate_model(
                    model, val_dataloader, args, components, writer, step
                )

                if val_score < best_val_score:
                    best_val_score = val_score
                    best_dir = f"{args.output_dir}/best"
                    print(
                        f"🏆 New best model at step {step} (val_score={val_score:.4f}), saving to: {best_dir}"
                    )
                    model.save_pretrained(best_dir)
                    tokenizer.save_pretrained(best_dir)
                    no_improvement_counter = 0
                else:
                    no_improvement_counter += 1

                if (
                    args.early_stopping_patience
                    and no_improvement_counter >= args.early_stopping_patience
                ):
                    print(
                        f"🚨 Early stopping at epoch {epoch}, step {step}. No improvement in validation score for {args.early_stopping_patience} steps."
                    )
                    break

        # Break batch loop
        if (
            args.early_stopping_patience
            and no_improvement_counter >= args.early_stopping_patience
        ):
            break

        # Evaluate each epoch
        evaluate_model(model, val_dataloader, args, components, writer, step)

    final_dir = f"{args.output_dir}/loss_{loss.item():.2f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
