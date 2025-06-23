"""
uv venv -p3.11
uv pip install -U phonikud-onnx "flask>=3.1.1"

wget https://huggingface.co/thewh1teagle/phonikud/resolve/main/phonikud-1.0.int8.onnx
uv run main.py
"""

from flask import Flask, request, jsonify
from phonikud_onnx import Phonikud
from pathlib import Path

app = Flask(__name__)

phonikud = None
model_path = Path("./phonikud-1.0.int8.onnx")
if model_path.exists():
    phonikud = Phonikud(str(model_path))


@app.route("/")
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.route("/add_diacritics", methods=["POST"])
def add_diacritics():
    data = request.get_json()
    text = data.get("text", "")

    if not phonikud:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        with_diacritics = phonikud.add_diacritics(text)
        return jsonify({"text": with_diacritics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
