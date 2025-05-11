# phonikud-onnx

Add diacritics to Hebrew text along with phonetic marks

Enhanced model of [Dicta model](https://huggingface.co/dicta-il/dictabert-large-char-menaked) 🤗

## Features

- Phonetics: adds phonetics diacritics
- Fast: 0.1s per sentnece (macOS M1) 🚀
- Batching: Supports multiple sentences at once 📚
- User friendly: Add diacritics with just 2 lines of code ✨
- Lightweight: Runs with onnx without heavy dependencies 🛠️
- Dual mode: Output nikud male (fully marked) and nikud haser 💡

## Setup

```console
pip install phonikud-onnx
```

## Usage

```python
from phonikud_onnx import Phonikud
phonikud = Phonikud("./phonikud-1.0.int8.onnx")
with_diacritics = phonikud.add_diacritics("מתכת יקרה")
print(with_diacritics)
```

## Examples

See [examples](examples)
