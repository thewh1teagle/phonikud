"""
pip install -U phonikud-onnx mishkal

wget https://huggingface.co/thewh1teagle/phonikud/resolve/main/phonikud-1.0.int8.onnx
uv run examples/with_phonikud_onnx.py
"""

from phonikud_onnx import Phonikud
from mishkal import phonemize

phonikud = Phonikud("./phonikud-1.0.int8.onnx")
sentence = "בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים על כל מה שרצה"
with_diacritics = phonikud.add_diacritics(sentence)
phonemes = phonemize(with_diacritics)
print("Sentence: ", with_diacritics)
print("Phonemes: ", phonemes)
