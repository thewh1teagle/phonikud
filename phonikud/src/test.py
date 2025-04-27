"""
uv run src/test.py --device cpu --file data/test.txt
"""

from model import PhoNikudModel
from argparse import ArgumentParser
from transformers import AutoTokenizer

def get_opts():
    parser = ArgumentParser()
    parser.add_argument('-m', '--model_checkpoint',
                        default='./output/phonikud_ckpt', type=str)
    parser.add_argument('-d', '--device',
                        default='cuda', type=str)
    # test file path
    parser.add_argument('-t', '--file',
                        default='./data/test.txt', type=str)
    return parser

def main():
    parser = get_opts()
    args = parser.parse_args()
    model = PhoNikudModel.from_pretrained(args.model_checkpoint, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    model.to(args.device)
    model.eval()

    with open(args.file, 'r', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            print(model.predict([line], tokenizer, mark_matres_lectionis='*'))


if __name__ == "__main__":
    main()
