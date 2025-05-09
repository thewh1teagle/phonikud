"""
uv run src/test.py --device cuda
"""

from src.model.phonikud_model import PhoNikudModel, NIKUD_HASER, remove_nikud
from src.train.config import BASE_PATH
from transformers import AutoTokenizer
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from tap import Tap


class RunArgs(Tap):
    model: str = BASE_PATH / "./ckpt/best"  # --model, -m
    device = "cuda"
    file: str = BASE_PATH / "./data/eval/dummy.txt"

    def configure(self):
        self.add_argument("--model", "-m", help="Path to the model checkpoint")
        return super().configure()


def main():
    args = RunArgs().parse_args()
    model = PhoNikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer: BertTokenizerFast = AutoTokenizer.from_pretrained(args.model)
    model.to(args.device)
    model.eval()

    with open(args.file, "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            line = remove_nikud(line)
            if not line:
                continue
            lines = model.predict([line], tokenizer, mark_matres_lectionis=NIKUD_HASER)
            for line in lines:
                print(line)


if __name__ == "__main__":
    main()
