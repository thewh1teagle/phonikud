# Mishkal

Grapheme to phoneme in Hebrew

Convert Hebrew text into IPA for TTS systems and learning.

## Features

- Expand dates into text with niqqud
- Expand numbers into text with niqqud
- Convert text with niqqud to modern spoken phonemes
- (WIP) Dictionaries with words, symbols, emojies, etc...
- (WIP) Mixed English in Hebrew
- (WIP) Very accurate lightweight niqqud model

## Install
```console
pip install mishkal-ivrit
```

## Examples
```python
from mishkal import phonemize
phonemes = phonemize('שָׁלוֹם עוֹלָם') 
print(phonemes) # ʃalom ?olam
```

See [examples](examples)
