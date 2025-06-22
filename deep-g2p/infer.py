import torch
from tap import Tap
from model import Seq2Seq
import json
import os
import time
import re


class InferenceConfig(Tap):
    model_path: str = "./ckpt/last"  # Path to model checkpoint
    vocab_path: str = "vocab.json"  # Path to vocabulary file


def predict_single(
    model, text, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len=50
):
    """Predict phonemes for a single word"""
    model.eval()

    text_ids = (
        [char_to_idx["<sos>"]]
        + [char_to_idx.get(c, char_to_idx["<unk>"]) for c in text]
        + [char_to_idx["<eos>"]]
    )
    src = torch.tensor(text_ids).unsqueeze(0)

    with torch.no_grad():
        encoder_outputs, hidden, cell = model.encoder(src)

        # Handle bidirectional LSTM states - same as in training
        # hidden/cell: [2, batch_size, hidden_size] (2 for bidirectional)
        # Combine forward and backward states
        hidden = torch.cat(
            [hidden[0], hidden[1]], dim=1
        )  # [batch_size, hidden_size * 2]
        cell = torch.cat([cell[0], cell[1]], dim=1)  # [batch_size, hidden_size * 2]

        # Project to decoder hidden size using the model's projection layers
        hidden = model.hidden_projection(hidden).unsqueeze(
            0
        )  # [1, batch_size, hidden_size]
        cell = model.cell_projection(cell).unsqueeze(0)  # [1, batch_size, hidden_size]

        outputs = [phoneme_to_idx["<sos>"]]

        for step in range(max_len):
            input_token = torch.tensor([outputs[-1]])
            output, hidden, cell = model.decoder(
                input_token, hidden, cell, encoder_outputs
            )
            predicted = output.argmax(1).item()

            if predicted == phoneme_to_idx["<eos>"]:
                break

            outputs.append(predicted)

    # Convert indices to phonemes
    phonemes = ""
    for idx in outputs[1:]:
        phoneme = idx_to_phoneme.get(str(idx), idx_to_phoneme.get(idx, f"UNK({idx})"))
        phonemes += phoneme

    return phonemes


def predict_batch(
    model, texts, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len=50
):
    """Predict phonemes for a batch of words"""
    model.eval()

    # Convert texts to tensor sequences
    batch_inputs = []
    for text in texts:
        text_ids = (
            [char_to_idx["<sos>"]]
            + [char_to_idx.get(c, char_to_idx["<unk>"]) for c in text]
            + [char_to_idx["<eos>"]]
        )
        batch_inputs.append(torch.tensor(text_ids))

    # Use collate function to pad the batch
    src_batch = torch.nn.utils.rnn.pad_sequence(
        batch_inputs, batch_first=True, padding_value=0
    )
    batch_size = src_batch.size(0)

    with torch.no_grad():
        encoder_outputs, hidden, cell = model.encoder(src_batch)

        # Handle bidirectional LSTM states
        hidden = torch.cat(
            [hidden[0], hidden[1]], dim=1
        )  # [batch_size, hidden_size * 2]
        cell = torch.cat([cell[0], cell[1]], dim=1)  # [batch_size, hidden_size * 2]

        # Project to decoder hidden size
        hidden = model.hidden_projection(hidden).unsqueeze(
            0
        )  # [1, batch_size, hidden_size]
        cell = model.cell_projection(cell).unsqueeze(0)  # [1, batch_size, hidden_size]

        # Initialize outputs for each item in batch
        batch_outputs = [[phoneme_to_idx["<sos>"]] for _ in range(batch_size)]
        finished = [False] * batch_size

        for step in range(max_len):
            if all(finished):
                break

            # Get current input tokens for all items in batch
            input_tokens = torch.tensor([outputs[-1] for outputs in batch_outputs])

            output, hidden, cell = model.decoder(
                input_tokens, hidden, cell, encoder_outputs
            )
            predictions = output.argmax(1)  # [batch_size]

            # Update outputs for each item in batch
            for i in range(batch_size):
                if not finished[i]:
                    predicted = predictions[i].item()
                    if predicted == phoneme_to_idx["<eos>"]:
                        finished[i] = True
                    else:
                        batch_outputs[i].append(predicted)

    # Convert indices to phonemes for each item
    results = []
    for outputs in batch_outputs:
        phonemes = ""
        for idx in outputs[1:]:  # Skip <sos>
            phoneme = idx_to_phoneme.get(
                str(idx), idx_to_phoneme.get(idx, f"UNK({idx})")
            )
            phonemes += phoneme
        results.append(phonemes)

    return results


def predict(
    model, text_or_texts, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len=50
):
    """Predict phonemes for single word or batch of words"""
    if isinstance(text_or_texts, str):
        # Single word
        return predict_single(
            model, text_or_texts, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len
        )
    else:
        # Batch of words
        return predict_batch(
            model, text_or_texts, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len
        )


def load_checkpoint(checkpoint_path):
    """Load model from checkpoint file"""
    if os.path.isfile(checkpoint_path):
        checkpoint = torch.load(checkpoint_path, map_location="cpu")
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            # Full checkpoint format
            return (
                checkpoint["model_state_dict"],
                checkpoint.get("char_to_idx"),
                checkpoint.get("phoneme_to_idx"),
            )
        else:
            # Legacy format (just state dict)
            return checkpoint, None, None
    else:
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")


def infer(config):
    # Load vocabulary
    with open(config.vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    char_to_idx = vocab["char_to_idx"]
    phoneme_to_idx = vocab["phoneme_to_idx"]
    idx_to_phoneme = vocab["idx_to_phoneme"]

    # Load model
    model = Seq2Seq(len(char_to_idx), len(phoneme_to_idx))
    model_state_dict, checkpoint_char_to_idx, checkpoint_phoneme_to_idx = (
        load_checkpoint(config.model_path)
    )
    model.load_state_dict(model_state_dict)

    # Use checkpoint vocab if available (for consistency)
    if checkpoint_char_to_idx and checkpoint_phoneme_to_idx:
        char_to_idx = checkpoint_char_to_idx
        phoneme_to_idx = checkpoint_phoneme_to_idx
        idx_to_phoneme = {str(idx): phoneme for phoneme, idx in phoneme_to_idx.items()}
        print("Using vocabulary from checkpoint")
    else:
        print("Using vocabulary from vocab.json")

    print(
        f"Loaded model with {len(char_to_idx)} characters, {len(phoneme_to_idx)} phonemes"
    )
    print()

    # Hebrew text with diacritics
    text = "הַ|דַּיָּי֯ג נִצְמַד לְֽ|דֹ֫ו֯פֶן הַ|סִּירָה בִּ|זְמַן הַ|סְּֽעָרָה. הִסְבַּ֫רְתִּי לָהּ אֶת הַ|כֹּל, וְֽ|אָמַ֫רְתִּי בְּֽדִיּוּק מָה קָרָה. הַ|יְּֽלָדִים אָהֲבוּ בִּמְיֻו֯חָד אֶת הַ|סִּי֯פּוּרִים הַלָּ֫לוּ שֶׁהַ|מּוֹרָה הִקְרִיאָה."

    # Extract Hebrew words using regex
    hebrew_pattern = r"[\u0590-\u05ea|]+"
    hebrew_words = re.findall(hebrew_pattern, text)

    # Clean words by removing pipes and empty strings
    clean_words = [
        word.replace("|", "") for word in hebrew_words if word.replace("|", "").strip()
    ]

    print("G2P Hebrew Word Processing:")
    print("=" * 50)
    print(f"Found {len(clean_words)} Hebrew words")
    print()

    # Start timing
    start_time = time.time()

    # Process each word individually
    for i, word in enumerate(clean_words, 1):
        result = predict(model, word, char_to_idx, phoneme_to_idx, idx_to_phoneme)
        print(f"{i:2d}. {word} -> {result}")

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Statistics
    total_chars = sum(len(word) for word in clean_words)

    print()
    print("=" * 50)
    print(f"Processed {len(clean_words)} words, {total_chars} characters")
    print(f"Total time: {elapsed_time:.3f} seconds")
    print(f"Average time per word: {elapsed_time/len(clean_words):.4f} seconds")
    print(f"Average time per character: {elapsed_time/total_chars:.5f} seconds")


if __name__ == "__main__":
    config = InferenceConfig().parse_args()
    infer(config)
