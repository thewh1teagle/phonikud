"""
See https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py
"""

import onnxruntime as ort
import numpy as np
from tokenizers import Tokenizer
import re
import json

# Constants
NIKUD_CLASSES = [
    "",
    "<MAT_LECT>",
    "\u05bc",
    "\u05b0",
    "\u05b1",
    "\u05b2",
    "\u05b3",
    "\u05b4",
    "\u05b5",
    "\u05b6",
    "\u05b7",
    "\u05b8",
    "\u05b9",
    "\u05ba",
    "\u05bb",
    "\u05bc\u05b0",
    "\u05bc\u05b1",
    "\u05bc\u05b2",
    "\u05bc\u05b3",
    "\u05bc\u05b4",
    "\u05bc\u05b5",
    "\u05bc\u05b6",
    "\u05bc\u05b7",
    "\u05bc\u05b8",
    "\u05bc\u05b9",
    "\u05bc\u05ba",
    "\u05bc\u05bb",
    "\u05c7",
    "\u05bc\u05c7",
]
SHIN_CLASSES = ["\u05c1", "\u05c2"]  # shin, sin
MAT_LECT_TOKEN = "<MAT_LECT>"
MATRES_LETTERS = list("אוי")
ALEF_ORD = ord("א")
TAF_ORD = ord("ת")
STRESS_CHAR = "\u05ab"  # "ole" symbol marks stress
MOBILE_SHVA_CHAR = "\u05bd"  # "meteg" symbol marks Vocal Shva (mobile shva)
PREFIX_CHAR = "|"


def is_hebrew_letter(char):
    return ALEF_ORD <= ord(char) <= TAF_ORD


def is_matres_letter(char):
    return char in MATRES_LETTERS


nikud_pattern = re.compile(r"[\u0590-\u05C7|]")


def remove_nikkud(text):
    return nikud_pattern.sub("", text)


class OnnxModel:
    def __init__(
        self,
        model_path,
        tokenizer_name="dicta-il/dictabert-large-char-menaked",
        session: ort.InferenceSession = None,
    ):
        # Load the tokenizer
        self.tokenizer = Tokenizer.from_pretrained(tokenizer_name)

        # Create ONNX Runtime session
        self.session = session or ort.InferenceSession(model_path)
        self.input_names = [input.name for input in self.session.get_inputs()]
        self.output_names = [output.name for output in self.session.get_outputs()]

    def get_metadata(self):
        try:
            metadata = self.session.get_modelmeta().custom_metadata_map
            if "config" in metadata:
                return json.loads(metadata["config"])
            return {}
        except (json.JSONDecodeError, KeyError):
            return {}

    def _create_inputs(self, sentences: list[str], padding: str):
        # Tokenize inputs using tokenizers library
        encodings = []
        for sentence in sentences:
            encoding = self.tokenizer.encode(sentence)
            encodings.append(encoding)

        # Get the max length for padding
        max_len = max(len(enc.ids) for enc in encodings) if padding == "longest" else 0

        # Prepare batch inputs
        input_ids = []
        attention_mask = []
        offset_mapping = []

        for encoding in encodings:
            ids = encoding.ids
            masks = [1] * len(ids)
            offsets = encoding.offsets

            # Pad if needed
            if padding == "longest" and len(ids) < max_len:
                padding_length = max_len - len(ids)
                ids = ids + [self.tokenizer.token_to_id("[PAD]")] * padding_length
                masks = masks + [0] * padding_length
                offsets = offsets + [(0, 0)] * padding_length

            input_ids.append(ids)
            attention_mask.append(masks)
            offset_mapping.append(offsets)

        # Convert to numpy arrays for ONNX Runtime
        return {
            "input_ids": np.array(input_ids, dtype=np.int64),
            "attention_mask": np.array(attention_mask, dtype=np.int64),
            # Token type IDs might be needed depending on your model
            "token_type_ids": np.zeros_like(np.array(input_ids, dtype=np.int64)),
        }, offset_mapping

    def predict(self, sentences, mark_matres_lectionis=None, padding="longest"):
        sentences = [remove_nikkud(sentence) for sentence in sentences]
        inputs, offset_mapping = self._create_inputs(sentences, padding)

        # Run inference
        outputs = self.session.run(self.output_names, inputs)

        # Process outputs based on output names
        nikud_idx = self.output_names.index("nikud_logits")
        shin_idx = self.output_names.index("shin_logits")
        nikud_logits = outputs[nikud_idx]
        shin_logits = outputs[shin_idx]

        additional_idx = self.output_names.index("additional_logits")
        additional_logits = outputs[additional_idx]

        # Get predictions
        nikud_predictions = np.argmax(nikud_logits, axis=-1)
        shin_predictions = np.argmax(shin_logits, axis=-1)

        # Since additional_logits shape is (batch, seq, 3), each index is a separate binary classifier
        stress_predictions = (additional_logits[..., 0] > 0).astype(np.int32)
        mobile_shva_predictions = (additional_logits[..., 1] > 0).astype(np.int32)
        prefix_predictions = (additional_logits[..., 2] > 0).astype(np.int32)

        ret = []
        for sent_idx, (sentence, sent_offsets) in enumerate(
            zip(sentences, offset_mapping)
        ):
            # Assign the nikud to each letter
            output = []
            prev_index = 0
            for idx, offsets in enumerate(sent_offsets):
                # Add anything we missed
                if offsets[0] > prev_index:
                    output.append(sentence[prev_index : offsets[0]])
                if offsets[1] - offsets[0] != 1:
                    continue

                # Get next char
                char = sentence[offsets[0] : offsets[1]]
                prev_index = offsets[1]
                if not is_hebrew_letter(char):
                    output.append(char)
                    continue

                nikud = NIKUD_CLASSES[nikud_predictions[sent_idx][idx]]
                shin = (
                    "" if char != "ש" else SHIN_CLASSES[shin_predictions[sent_idx][idx]]
                )

                # Check for matres lectionis
                if nikud == MAT_LECT_TOKEN:
                    if not is_matres_letter(char):
                        nikud = ""  # Don't allow matres on irrelevant letters
                    elif mark_matres_lectionis is not None:
                        nikud = mark_matres_lectionis
                    else:
                        output.append(char)
                        continue

                stress = (
                    STRESS_CHAR
                    if stress_predictions is not None
                    and stress_predictions[sent_idx][idx] == 1
                    else ""
                )
                mobile_shva = (
                    MOBILE_SHVA_CHAR
                    if mobile_shva_predictions is not None
                    and mobile_shva_predictions[sent_idx][idx] == 1
                    else ""
                )

                prefix = (
                    PREFIX_CHAR
                    if prefix_predictions is not None
                    and prefix_predictions[sent_idx][idx] == 1
                    else ""
                )

                output.append(char + shin + nikud + stress + mobile_shva + prefix)
            output.append(sentence[prev_index:])
            ret.append("".join(output))

        return ret
