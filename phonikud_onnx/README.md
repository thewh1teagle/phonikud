# phonikud-onnx

TODO: change this

Add diacritics to Hebrew text using [Dicta model](https://huggingface.co/dicta-il/dictabert-large-char-menaked)

See [model card](https://huggingface.co/dicta-il/dictabert-large-char-menaked) on HuggingFace 🤗

## Features

- Fast: 0.1s per sentnece (macOS M1) 🚀
- Batching: Supports multiple sentences at once 📚
- User friendly: Add diacritics with just 2 lines of code ✨
- Lightweight: Runs with onnx without heavy dependencies 🛠️
- Dual mode: Output niqqud male (fully marked) and niqqud haser 💡

## Install

```console
pip install -U dicta-onnx
```

## Usage

1. Install the library
2. Download model from [model-files-v1.0](https://github.com/thewh1teagle/dicta-onnx/releases/model-files-v1.0) and put in the directory
3. Run one of the examples from [examples](examples) folder

## Play

You can play with dicta-onnx in this [HuggingFace Space](https://huggingface.co/spaces/thewh1teagle/add-diacritics-in-hebrew)

## Credits

Special thanks ❤️ to [dicta-il](https://huggingface.co/dicta-il/dictabert-large-char-menaked) for their amazing Hebrew diacritics model! ✨
