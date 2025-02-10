# Mishkal

Grapheme to phoneme in Hebrew

Convert Hebrew text into IPA for TTS systems and learning.

## Features

- Expand dates into text with niqqud
- Expand numbers into text with niqqud
- Convert text with niqqud to modern spoken phonemes
- Dictionaries with words, symbols, emojies
- (WIP) Mixed English in Hebrew
- (WIP) Very accurate lightweight niqqud model

## Install
```console
pip install mishkal-hebrew
```

## Play

See [Phonemize with Hebrew Space](https://huggingface.co/spaces/thewh1teagle/phonemize-in-hebrew)

## Examples
```python
from mishkal import phonemize
phonemes = phonemize('שָׁלוֹם עוֹלָם') 
print(phonemes) # ʃalom ?olam
```

See [examples](examples)
