from argparse import ArgumentParser
from transformers import AutoModel, AutoTokenizer
from glob import glob
import os
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, trange
import torch


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
        self.stress = [] # will contain 0/1 for each character (1=stressed)
        self.mobile_shva = [] # will contain 0/1 for each caracter (1=mobile shva)
        for char in raw_text:
            if char == self.STRESS_CHAR:
                self.stress[-1] = 1
            elif char == self.MOBILE_SHVA_CHAR:
                self.mobile_shva[-1] = 1
            else:
                self.text += char
                self.stress += [0]
                self.mobile_shva += [0]
        assert len(self.text) == len(self.stress) == len(self.mobile_shva)

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


def main():
    args = get_opts()

    print("Loading model...")

    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    model = AutoModel.from_pretrained(
        args.model_checkpoint, trust_remote_code=True)
    model.to(args.device)

    print("Loading data...")
    data = TrainData(args)

    import pdb; pdb.set_trace()

    print("Training...")

    dl = DataLoader(data,
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=lambda x: x,
        num_workers=args.num_workers
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)

    for _ in trange(args.epochs, desc="Epoch"):
        for B in tqdm(dl, desc="Train iteration"):
            ...
    
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
