"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv sync
uv run python examples/simple.py
"""

from phonikud_onnx import Phonikud
from phonikud import lexicon


def main():
    phonikud = Phonikud("./phonikud-1.0.int8.onnx")
    sentence = "כמה אתה חושב שזה יעלה לי? אני מגיע לשם רק בערב.."
    with_diacritics = phonikud.add_diacritics(
        sentence, mark_matres_lectionis=lexicon.NIKUD_HASER_DIACRITIC
    )
    print(with_diacritics)


if __name__ == "__main__":
    main()
