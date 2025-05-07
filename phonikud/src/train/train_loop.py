# train_loop.py
import torch
from torch import nn
from tqdm import tqdm, trange
from torch.utils.tensorboard import SummaryWriter

from data import COMPONENT_INDICES
from evaluate import evaluate_model


def train_model(
    model,
    tokenizer,
    train_dataloader,
    val_dataloader,
    args,
    components,
    writer: SummaryWriter,
):
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()
    step = args.pre_training_step
    for _ in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(train_dataloader, desc="Train iter")
        for inputs, targets in pbar:
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

            if args.checkpoint_interval > 0 and step % args.checkpoint_interval == 0:
                save_dir = f"{args.output_dir}/last"
                print(f"💾 Saving checkpoint at step {step} to: {save_dir}")
                model.save_pretrained(save_dir)
                tokenizer.save_pretrained(save_dir)

        # Evaluate each epoch
        evaluate_model(model, val_dataloader, args, components, writer, step)

    final_dir = f"{args.output_dir}/step_{step + 1}_loss_{loss.item():.4f}"
    print(f"🚀 Saving trained model to: {final_dir}")
    model.save_pretrained(final_dir)
    tokenizer.save_pretrained(final_dir)
