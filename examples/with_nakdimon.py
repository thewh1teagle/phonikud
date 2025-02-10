# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "mishkal-ivrit",
#     "nakdimon-onnx",
# ]
#
# [tool.uv.sources]
# mishkal-ivrit = { path = "../" }
# ///
"""
wget https://github.com/thewh1teagle/nakdimon-onnx/releases/download/v0.1.0/nakdimon.onnx
uv run examples/with_nakdimon.py
"""

from nakdimon_onnx import Nakdimon
from mishkal import text_to_ipa

nakdimon = Nakdimon("nakdimon.onnx")
text = "שלום עולם!"
dotted_text = nakdimon.compute(text)

print('Undotted: ', text_to_ipa(text))
print('Dotted: ', text_to_ipa(dotted_text))