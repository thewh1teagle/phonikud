"""
wget https://huggingface.co/thewh1teagle/phonikud/resolve/main/phonikud-1.0.int8.onnx
uv sync
uv run python examples/file.py <some file>
"""

from phonikud_onnx import Phonikud
from phonikud import lexicon
import sys


def main():
    phonikud = Phonikud("./phonikud-1.0.int8.onnx")
    file = sys.argv[1]
    with open(file) as fp:
        for line in fp:
            with_diacritics = phonikud.add_diacritics(
                line, mark_matres_lectionis=lexicon.NIKUD_HASER_DIACRITIC
            )
            print(with_diacritics.strip())


if __name__ == "__main__":
    main()
