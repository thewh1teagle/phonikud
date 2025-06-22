## Upload to HuggingFace

```console
uv pip install huggingface_hub
git config --global credential.helper store # Allow clone private repo from HF
huggingface-cli login --token "token" --add-to-git-credential # https://huggingface.co/settings/tokens
uv run export.py
uv run huggingface-cli upload --repo-type model phonikud-onnx phonikud-1.0.int8.onnx phonikud-1.0.onnx
```