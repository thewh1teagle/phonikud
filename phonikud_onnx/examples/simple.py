"""
wget https://huggingface.co/thewh1teagle/phonikud/resolve/main/phonikud-1.0.int8.onnx
uv sync
uv run python examples/simple.py
"""

from phonikud_onnx import Phonikud


def main():
    phonikud = Phonikud("./phonikud-1.0.int8.onnx")
    sentence = "בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים"
    with_diacritics = phonikud.add_diacritics(sentence)
    print(with_diacritics)


if __name__ == "__main__":
    main()
