# Mishkal

grapheme to phoneme in Hebrew

Convert Hebrew text into IPA, this useful for TTS systems and learning.

## Install

```console
pip install mishkal-ivrit
```

## Examples

```python
from mishkal import text_to_ipa

phonemes = text_to_ipa('שָׁלוֹם עוֹלָם') # ʃalom ?olam
print(phonemes) # 
```

See [examples](examples)

## How it works

1. Dates are expanded into diacritized words (eg. 20/01/2025 into spoken words)
2. Numbers are expanded into diacritized words (eg. 2000 into single word)
3. Characters iterated and diacritics collected for each
4. Early phonemes returns based on surround context (cur, cur_d, prev, prev_d, next, next_d) eg. Vav is sometimes V and sometimes Just O with Holam Haser
5. If early phonemes not returned the base sound of the character added
6. Diacritics added as sounds that affect the letter