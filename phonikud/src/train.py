from argparse import ArgumentParser
from transformers import AutoModel, AutoTokenizer
from glob import glob
import os
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, trange
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence

ALEF_ORD = ord('א')
TAF_ORD = ord('ת')
def is_hebrew_letter(char):
   return ALEF_ORD <= ord(char) <= TAF_ORD

MATRES_LETTERS = list('אוי')
def is_matres_letter(char):
    return char in MATRES_LETTERS

import re
nikud_pattern = re.compile(r'[\u05B0-\u05BD\u05C1\u05C2\u05C7]')
def remove_nikkud(text):
    return nikud_pattern.sub('', text)

STRESS_CHAR = chr(1451) # "ole" symbol marks stress
MOBILE_SHVA_CHAR = chr(1469) # "meteg" symbol marks shva na (mobile shva)


def get_opts():
    parser = ArgumentParser()
    parser.add_argument('-m', '--model_checkpoint',
                        default='dicta-il/dictabert-large-char-menaked', type=str)
    parser.add_argument('-d', '--device',
                        default='cuda', type=str)
    parser.add_argument('-dd', '--data_dir',
                        default='data/', type=str)
    parser.add_argument('-o', '--output_dir',
                        default='output/phonikud_ckpt', type=str)
    parser.add_argument('--batch_size', default=4, type=int)
    parser.add_argument('--epochs', default=10, type=int)
    parser.add_argument('--learning_rate', default=1e-3, type=float)
    parser.add_argument('--num_workers', default=0, type=int)

    return parser.parse_args()

class AnnotatedLine:
    
    def __init__(self, raw_text):
        self.text = "" # will contain plain hebrew text
        stress = [] # will contain 0/1 for each character (1=stressed)
        mobile_shva = [] # will contain 0/1 for each caracter (1=mobile shva)
        for char in raw_text:
            if char == STRESS_CHAR:
                stress[-1] = 1
            elif char == MOBILE_SHVA_CHAR:
                mobile_shva[-1] = 1
            else:
                self.text += char
                stress += [0]
                mobile_shva += [0]
        assert len(self.text) == len(stress) == len(mobile_shva)
        stress_tensor = torch.tensor(stress)
        mobile_shva_tensor = torch.tensor(mobile_shva)

        self.target = torch.stack((stress_tensor, mobile_shva_tensor))
        # ^ shape: (n_chars, 2)

class TrainData(Dataset):

    def __init__(self, args):
        fns = glob(os.path.join(args.data_dir, "train", "*.txt"))
        print(len(fns), "text files found; using them for training data...")

        raw_text = ""
        for fn in fns:
            with open(fn, "r") as f:
                raw_text += f.read() + "\n"
        raw_text = raw_text.strip()

        self.lines = raw_text.splitlines()
        # TODO: chunk into max length (2048) rather than assuming each line is shorter

    def __len__(self):
        return len(self.lines)
    
    def __getitem__(self, idx):
        text = self.lines[idx]
        return AnnotatedLine(text)


class PhoNikudModel(nn.Module):
    # TODO: make it a Transformers module, instead of wrapping existing module
    def __init__(self, args):
        super().__init__()
        self.device = args.device
        self.base_model = AutoModel.from_pretrained(
            args.model_checkpoint, trust_remote_code=True)

        self.mlp = nn.Sequential(
            nn.Linear(1024, 100),
            nn.ReLU(),
            nn.Linear(100, 2)
        )
        # ^ predicts stress and mobile shva; outputs are logits

        self.base_config = self.base_model.config

    def freeze_base_model(self):
        self.base_model.eval()
        for param in self.base_model.parameters():
            param.requires_grad = False
    
    def forward(self, x):
        # based on: https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py
        bert_outputs = self.base_model.bert(**x)
        hidden_states = bert_outputs.last_hidden_state
        # ^ shape: (batch_size, n_chars_padded, 1024)
        hidden_states = self.base_model.dropout(hidden_states)

        _, nikud_logits = self.base_model.menaked(hidden_states)
        # ^ nikud_logits: MenakedLogitsOutput

        additional_logits = self.mlp(hidden_states)
        # ^ shape: (batch_size, n_chars_padded, 2) [2 for stress & mobile shva]

        return nikud_logits, additional_logits

    @torch.no_grad()
    def predict(self, sentences, tokenizer, mark_matres_lectionis=None, padding='longest'):
        # based on: https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py

        sentences = [remove_nikkud(sentence) for sentence in sentences]
        # assert the lengths aren't out of range
        assert all(len(sentence) + 2 <= tokenizer.model_max_length for sentence in sentences), f'All sentences must be <= {tokenizer.model_max_length}, please segment and try again'
        
        # tokenize the inputs and convert them to relevant device
        inputs = tokenizer(sentences, padding=padding, truncation=True, return_tensors='pt', return_offsets_mapping=True)
        offset_mapping = inputs.pop('offset_mapping')
        inputs = {k:v.to(self.device) for k,v in inputs.items()}
        
        # calculate the predictions
        nikud_logits, additional_logits = self.forward(inputs)
        nikud_predictions = nikud_logits.nikud_logits.argmax(dim=-1).tolist()
        shin_predictions = nikud_logits.shin_logits.argmax(dim=-1).tolist()

        stress_predictions = (additional_logits[..., 0] > 0).int().tolist()
        mobile_shva_predictions = (additional_logits[..., 1] > 0).int().tolist()

        ret = []
        for sent_idx,(sentence,sent_offsets) in enumerate(zip(sentences, offset_mapping)):
            # assign the nikud to each letter!
            output = []
            prev_index = 0
            for idx,offsets in enumerate(sent_offsets):
                # add in anything we missed
                if offsets[0] > prev_index:
                    output.append(sentence[prev_index:offsets[0]])
                if offsets[1] - offsets[0] != 1: continue
                
                # get our next char
                char = sentence[offsets[0]:offsets[1]]
                prev_index = offsets[1]
                if not is_hebrew_letter(char):
                    output.append(char)
                    continue
                
                nikud = self.base_config.nikud_classes[nikud_predictions[sent_idx][idx]]
                shin = '' if char != 'ש' else self.base_config.shin_classes[shin_predictions[sent_idx][idx]] 

                # check for matres lectionis
                if nikud == self.base_config.mat_lect_token:
                    if not is_matres_letter(char): nikud = '' # don't allow matres on irrelevant letters
                    elif mark_matres_lectionis is not None: nikud = mark_matres_lectionis
                    else: continue
                
                stress = STRESS_CHAR if stress_predictions[sent_idx][idx] == 1 else ""
                mobile_shva = MOBILE_SHVA_CHAR if mobile_shva_predictions[sent_idx][idx] == 1 else ""

                output.append(char + shin + nikud + stress + mobile_shva)
            output.append(sentence[prev_index:])
            ret.append(''.join(output))
        
        return ret


class Collator:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def collate_fn(self, items):
        inputs = self.tokenizer(
            [x.text for x in items],
            padding=True,
            truncation=True,
            return_tensors='pt')
        targets = pad_sequence([x.target.T for x in items], batch_first=True)
        # ^ shape: (batch_size, n_chars_padded, 2)

        return inputs, targets


def main():
    args = get_opts()

    print("Loading model...")

    model = PhoNikudModel(args)
    model.to(args.device)
    model.freeze_base_model()
    # ^ we will only train extra layers

    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    collator = Collator(tokenizer)

    print("Loading data...")
    data = TrainData(args)

    print("Training...")

    dl = DataLoader(data,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collator.collate_fn,
        num_workers=args.num_workers
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    criterion = nn.BCEWithLogitsLoss()

    for _ in trange(args.epochs, desc="Epoch"):
        pbar = tqdm(dl, desc="Train iter")
        for inputs, targets in pbar:

            optimizer.zero_grad()

            inputs = inputs.to(args.device)
            targets = targets.to(args.device)
            # ^ shape: (batch_size, n_chars_padded, 2)
            _, additional_logits = model(inputs)
            # ^ shape: (batch_size, n_chars_padded, 2)

            loss = criterion(
                additional_logits[:, 1:-1], # skip BOS and EOS symbols
                targets.float())
            # ^ NOTE: loss is only on new labels (stress, mobile shva)
            # rest of network is frozen so nikkud predictions should not change

            loss.backward()
            optimizer.step()

            pbar.set_description(f"Train iter (L={loss.item():.4f})")
    
    # TODO: save checkpoint
    # save_dir = args.output_dir
    # print("Saving trained model to:", save_dir)
    # model.save_model(save_dir)

    print("Testing...")

    model.eval()

    test_fn = os.path.join(args.data_dir, "test.txt")
    with open(test_fn, "r") as f:
        test_text = f.read().strip()

    for line in test_text.splitlines():
        print(line)
        print(model.predict([line], tokenizer, mark_matres_lectionis='*'))
        print()


if __name__ == "__main__":
    main()
