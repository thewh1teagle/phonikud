from argparse import ArgumentParser
from transformers import AutoModel, AutoTokenizer
from glob import glob
import os
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, trange
import torch
from torch import nn
from torch.nn.utils.rnn import pad_sequence


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
    STRESS_CHAR = chr(1451) # "ole" symbol marks stress
    MOBILE_SHVA_CHAR = chr(1469) # "meteg" symbol marks shva na (mobile shva)

    def __init__(self, raw_text):
        self.text = "" # will contain plain hebrew text
        stress = [] # will contain 0/1 for each character (1=stressed)
        mobile_shva = [] # will contain 0/1 for each caracter (1=mobile shva)
        for char in raw_text:
            if char == self.STRESS_CHAR:
                stress[-1] = 1
            elif char == self.MOBILE_SHVA_CHAR:
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

        _, nikkud_logits = self.base_model.menaked(hidden_states)
        # ^ nikkud_logits: MenakedLogitsOutput

        additional_logits = self.mlp(hidden_states)
        # ^ shape: (batch_size, n_chars_padded, 2) [2 for stress & mobile shva]

        return nikkud_logits, additional_logits


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
        for inputs, targets in tqdm(dl, desc="Train iteration"):
            inputs = inputs.to(args.device)
            targets = targets.to(args.device)
            # ^ shape: (batch_size, n_chars_padded, 2)
            _, additional_logits = model(inputs)
            # ^ shape: (batch_size, n_chars_padded, 2)

            loss = criterion(additional_logits, targets)
            # ^ NOTE: loss is only on new labels (stress, mobile shva)
            # rest of network is frozen so nikkud predictions should not change
            import pdb; pdb.set_trace()
    
    save_dir = args.output_dir
    print("Saving trained model to:", save_dir)
    model.save_model(save_dir)

    print("Testing...")

    model.eval()

    test_fn = os.path.join(args.data_dir, "test.txt")
    with open(test_fn, "r") as f:
        test_text = f.read().strip()

    for line in test_text.splitlines():
        ...

    # import pdb; pdb.set_trace()

    # print("Testing...")

    # model.eval()
    # sentence = 'בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים'
    # print(model.predict([sentence], tokenizer))

    # print("Done")


if __name__ == "__main__":
    main()
