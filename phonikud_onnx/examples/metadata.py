"""
wget https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx
uv sync
uv run python examples/simple.py
"""

from phonikud_onnx import Phonikud
from phonikud import lexicon


def main():
    phonikud = Phonikud("./phonikud-1.0.int8.onnx")
    metadata = phonikud.get_metadata()
    commit = metadata["commit"]
    print(f'Phonikud commit: {commit}')


if __name__ == "__main__":
    main()
