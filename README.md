# Mishkal
grapheme to phoneme in Hebrew
Convert Hebrew text into IPA, this useful for TTS systems and learning.

## Install
```console
pip install mishkal-ivrit
```

## Examples
```python
from mishkal import phonemize
phonemes = phonemize('שָׁלוֹם עוֹלָם') # ʃalom ?olam
print(phonemes) # 
```

See [examples](examples)
