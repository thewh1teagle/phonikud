import argparse
import torch
from model import Seq2Seq
import json


def predict(model, text, char_to_idx, phoneme_to_idx, idx_to_phoneme, max_len=50):
    model.eval()

    text_ids = (
        [char_to_idx["<sos>"]]
        + [char_to_idx.get(c, char_to_idx["<unk>"]) for c in text]
        + [char_to_idx["<eos>"]]
    )
    src = torch.tensor(text_ids).unsqueeze(0)

    encoder_outputs, hidden, cell = model.encoder(src)
    hidden = hidden.view(1, 1, -1)
    cell = cell.view(1, 1, -1)

    outputs = [phoneme_to_idx["<sos>"]]

    for _ in range(max_len):
        input_token = torch.tensor([outputs[-1]])
        output, hidden, cell = model.decoder(input_token, hidden, cell, encoder_outputs)
        predicted = output.argmax(1).item()

        if predicted == phoneme_to_idx["<eos>"]:
            break

        outputs.append(predicted)

    phonemes = "".join([idx_to_phoneme.get(idx, "") for idx in outputs[1:]])
    return phonemes


def infer(args):
    with open(args.vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    char_to_idx = vocab["char_to_idx"]
    phoneme_to_idx = vocab["phoneme_to_idx"]
    idx_to_phoneme = vocab["idx_to_phoneme"]

    model = Seq2Seq(len(char_to_idx), len(phoneme_to_idx))
    model.load_state_dict(torch.load(args.model_path))

    if args.text:
        result = predict(model, args.text, char_to_idx, phoneme_to_idx, idx_to_phoneme)
        print(f"{args.text} -> {result}")
    elif args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if text:
                    result = predict(
                        model, text, char_to_idx, phoneme_to_idx, idx_to_phoneme
                    )
                    print(f"{text} -> {result}")
    else:
        while True:
            text = input("Enter Hebrew text (or 'quit' to exit): ")
            if text.lower() == "quit":
                break
            result = predict(model, text, char_to_idx, phoneme_to_idx, idx_to_phoneme)
            print(f"{text} -> {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", default="model.pt")
    parser.add_argument("--vocab_path", default="vocab.json")
    parser.add_argument("--text", help="Single text to convert")
    parser.add_argument("--input_file", help="File with texts to convert")

    args = parser.parse_args()
    infer(args)
