"""
pip install transformers torch mishkal
uv run with_dicta.py
"""

from transformers import AutoModel, AutoTokenizer
from mishkal import phonemize

tokenizer = AutoTokenizer.from_pretrained("dicta-il/dictabert-large-char-menaked")
model = AutoModel.from_pretrained(
    "dicta-il/dictabert-large-char-menaked", trust_remote_code=True
)

model.eval()

sentence = "בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים"
nikud = model.predict([sentence], tokenizer)
phonemes = phonemize(nikud)
print(nikud)
print(phonemes)
