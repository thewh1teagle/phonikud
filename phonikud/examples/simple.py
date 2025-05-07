"""
uv run src/test.py --device cuda
"""

from phonikud.src.model import PhoNikudModel, NIKUD_HASER
from transformers import AutoTokenizer
from tap import Tap
from typing import Literal


class RunArgs(Tap):
    model_checkpoint: str = "./ckpt/last"
    """Path to the model checkpoint"""

    device: Literal["cuda", "cpu"] = "cuda"
    """Device to run on"""

    file: str = "./data/eval/dummy.txt"
    """Path to the input test file"""


def main():
    args = RunArgs().parse_args()
    model = PhoNikudModel.from_pretrained(args.model_checkpoint, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    model.to(args.device)
    model.eval()

    with open(args.file, "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            lines = model.predict([line], tokenizer, mark_matres_lectionis=NIKUD_HASER)
            for line in lines:
                print(line)


if __name__ == "__main__":
    main()
