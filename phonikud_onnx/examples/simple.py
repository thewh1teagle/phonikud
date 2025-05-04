"""
uv sync
uv run python examples/simple.py
"""

from phonikud_onnx import Phonikud


def main():
    dicta = Phonikud("./dicta-1.0.int8.onnx")
    sentence = "בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים"
    with_diacritics = dicta.add_diacritics(sentence)
    print(with_diacritics)


if __name__ == "__main__":
    main()
