# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "mishkal-hebrew",
#     "nakdimon-onnx",
# ]
#
# [tool.uv.sources]
# mishkal-hebrew = { path = "../" }
# ///
"""
wget https://github.com/thewh1teagle/nakdimon-onnx/releases/download/v0.1.0/nakdimon.onnx
uv run examples/with_nakdimon.py
"""

from nakdimon_onnx import Nakdimon
from mishkal import phonemize

nakdimon = Nakdimon("nakdimon.onnx")
text = "שלום עולם!"
dotted_text = nakdimon.compute(text)

print('Undotted: ', phonemize(text))
print('Dotted: ', phonemize(dotted_text))