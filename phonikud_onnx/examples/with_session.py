"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv sync
uv run python examples/simple.py
"""

from phonikud_onnx import Phonikud
from phonikud import lexicon
import onnxruntime as ort

def main():
    sess = ort.InferenceSession('./phonikud-1.0.int8.onnx')
    phonikud = Phonikud.from_session(session=sess)
    sentence = "הילדים אהבו במיוחד את הסיפורים הללו שהמורה הקריאה."
    with_diacritics = phonikud.add_diacritics(
        sentence, mark_matres_lectionis=lexicon.NIKUD_HASER_DIACRITIC
    )
    print(with_diacritics)


if __name__ == "__main__":
    main()
