"""
uv sync --extra onnx

From filesystem:
    uv run export.py --model ../phonikud/ckpt/last

From HuggingFace:
    uv run .\export.py --model thewh1teagle/phonikud
"""

import torch
import onnx
import json
from pathlib import Path
from onnxruntime.quantization import quantize_dynamic, QuantType
from argparse import ArgumentParser
import sys

sys.path.append(str(Path(__file__).parent / "../model/src"))
from model.phonikud_model import (
    PhonikudModel,
)  # TODO: add it as package for autocomplete

# Global metadata to add to ONNX models
metadata = {
    "commit": "aef4b26",  # https://huggingface.co/thewh1teagle/phonikud/tree/main
}


def add_meta_data_onnx(filename, key, value):
    """Add metadata to ONNX model."""
    model = onnx.load(filename)
    meta = model.metadata_props.add()
    meta.key = key
    meta.value = value
    onnx.save(model, filename)


def parse_args():
    parser = ArgumentParser(description="Export and quantize model")
    parser.add_argument(
        "--model",
        type=str,
        default="../model/ckpt/best_wer",  # dicta-il/dictabert-large-char-menaked # ../model/ckpt/best_wer # thewh1teagle/phonikud
        help="Name of the model to export and quantize.",
    )
    return parser.parse_args()


args = parse_args()

# Config
dynamic_axes = True
dynamic_axes_dict = None
batch_size = 1
sequence_length = 128

int8_model_path = "phonikud-1.0.int8.onnx"
fp32_model_path = "phonikud-1.0.onnx"


# Define a model wrapper class for ONNX export
class ModelForONNX(torch.nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, input_ids, attention_mask, token_type_ids):
        # Create a dictionary of inputs as expected by the model's forward method
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        }

        # Call the model with the inputs dictionary
        outputs = self.model(inputs)

        # Extract the three outputs we want to export
        return (outputs.nikud_logits, outputs.shin_logits, outputs.additional_logits)


def main():
    # Load your custom model
    print(f"Loading model from: {args.model}")

    # Option 1: If your model can be loaded directly from checkpoint
    model = PhonikudModel.from_pretrained(args.model)  # force_download=True

    # Option 2: If you need to load from a saved state dict
    # model = PhonikudModel(config)
    # state_dict = torch.load(os.path.join(args.model, "pytorch_model.bin"))
    # model.load_state_dict(state_dict)

    model.eval()

    # Wrap the model for ONNX export
    wrapped_model = ModelForONNX(model)

    # Create dummy inputs
    dummy_input_ids = torch.ones((batch_size, sequence_length), dtype=torch.long)
    dummy_attention_mask = torch.ones((batch_size, sequence_length), dtype=torch.long)
    dummy_token_type_ids = torch.zeros((batch_size, sequence_length), dtype=torch.long)

    # Define dynamic axes if requested
    if dynamic_axes:
        dynamic_axes_dict = {
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "token_type_ids": {0: "batch_size", 1: "sequence_length"},
            "nikud_logits": {0: "batch_size", 1: "sequence_length"},
            "shin_logits": {0: "batch_size", 1: "sequence_length"},
            "additional_logits": {0: "batch_size", 1: "sequence_length"},
        }

    # Create model folder
    Path(fp32_model_path).parent.mkdir(exist_ok=True)

    print(f"Exporting onnx model to: {fp32_model_path}...")
    # Export with the wrapped model
    torch.onnx.export(
        wrapped_model,
        args=(dummy_input_ids, dummy_attention_mask, dummy_token_type_ids),
        f=fp32_model_path,
        input_names=["input_ids", "attention_mask", "token_type_ids"],
        output_names=["nikud_logits", "shin_logits", "additional_logits"],
        dynamic_axes=dynamic_axes_dict,
        opset_version=14,
        do_constant_folding=True,
        export_params=True,
        verbose=False,
    )
    print("✅ ONNX model export completed!")

    # Add metadata to the model as JSON config
    config = {**metadata, "source_model": args.model}
    print(f"Adding metadata: {config}")
    add_meta_data_onnx(fp32_model_path, "config", json.dumps(config))

    # Verify the exported model
    print("Verifying ONNX model integrity...")
    onnx_model = onnx.load(fp32_model_path)
    onnx.checker.check_model(onnx_model)
    print("🎉 ONNX model verification successful! Ready to use.")

    # Perform dynamic quantization (INT8)
    print(f"Quantizing model to INT8: {int8_model_path}...")
    quantize_dynamic(
        model_input=fp32_model_path,
        model_output=int8_model_path,
        weight_type=QuantType.QInt8,  # Use QuantType.QUInt8 for unsigned weights if needed
    )
    print("✅ INT8 quantized model export completed!")

    # Add metadata to quantized model too
    config_int8 = {**config, "quantization": "int8"}
    add_meta_data_onnx(int8_model_path, "config", json.dumps(config_int8))


if __name__ == "__main__":
    main()
