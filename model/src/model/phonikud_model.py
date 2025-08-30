import torch
from torch import nn
from dataclasses import dataclass
from transformers.utils import ModelOutput
from transformers import BertTokenizerFast
import re
from typing import List


from .dicta_model import (
    BertForDiacritization,
    is_hebrew_letter,
    is_matres_letter,
)

HATAMA_CHAR = "\u05ab"  # "ole" symbol marks hatama
VOCAL_SHVA_CHAR = "\u05bd"  # "meteg" symbol marks vocal shva (e)
PREFIX_CHAR = "|"  # vertical bar
NIKUD_HASER = "\u05af"  # not in use but dicta has it

ENHANCED_NIKUD = HATAMA_CHAR + VOCAL_SHVA_CHAR + PREFIX_CHAR + NIKUD_HASER


def get_char_name(char: str) -> str:
    """Get clean character name without Unicode symbols"""
    names = {
        HATAMA_CHAR: "HATAMA",
        VOCAL_SHVA_CHAR: "VOCAL_SHVA",
        PREFIX_CHAR: "PREFIX",
    }
    return names.get(char, char)


def remove_enhanced_nikud(text: str):
    return remove_nikud(text, additional=ENHANCED_NIKUD)


def remove_nikud(text: str, additional=""):
    """
    Remove nikud except meteg as we use it for Vocal Shva
    """
    return re.sub(f"[\u05b0-\u05bc\u05be-\u05c7{additional}]", "", text)


@dataclass
class MenakedLogitsOutput(ModelOutput):
    nikud_logits: torch.FloatTensor = None
    shin_logits: torch.FloatTensor = None
    additional_logits: torch.FloatTensor = None  # For hatama, mobile shva, and prefix

    def detach(self):
        return MenakedLogitsOutput(
            self.nikud_logits.detach(),
            self.shin_logits.detach(),
            self.additional_logits.detach(),
        )


@dataclass
class ModelPredictions:
    """Container for all model predictions to avoid tuple unpacking."""

    nikud: List[List[int]]
    shin: List[List[int]]
    hatama: List[List[int]]
    vocal_shva: List[List[int]]
    prefix: List[List[int]]


class PhonikudModel(BertForDiacritization):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.mlp = nn.Sequential(
            nn.Linear(1024, 256), nn.ReLU(), nn.Linear(256, 3)
        )  # 3 for hatama, mobile shva, and prefix
        # ^ predicts hatama, mobile shva, and prefix; outputs are logits

    def freeze_base_model(self):
        self.bert.eval()
        self.menaked.eval()
        for param in self.bert.parameters():
            param.requires_grad = False

        for param in self.menaked.parameters():
            param.requires_grad = False

    def freeze_specific_chars(self, chars_to_train: List[str]):
        """Freeze entire MLP, then unfreeze only specific character outputs"""
        if len(chars_to_train) == 3:
            return  # Training all characters, no freezing needed

        # Step 1: Freeze entire MLP
        for param in self.mlp.parameters():
            param.requires_grad = False
        print("🧊 Frozen entire MLP")

        # Step 2: Unfreeze only specific output weights for training characters
        final_layer = self.mlp[-1]  # nn.Linear(256, 3)
        char_to_idx = {HATAMA_CHAR: 0, VOCAL_SHVA_CHAR: 1, PREFIX_CHAR: 2}

        for char in chars_to_train:
            if char in char_to_idx:
                idx = char_to_idx[char]
                final_layer.weight[idx].requires_grad = True
                final_layer.bias[idx].requires_grad = True
                from src.train.utils import get_char_name

                print(
                    f"🔓 Unfrozen parameters for {get_char_name(char)} (channel {idx})"
                )

    def forward(self, x):
        # based on: https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py
        bert_outputs = self.bert(**x)
        hidden_states = bert_outputs.last_hidden_state
        # ^ shape: (batch_size, n_chars_padded, 1024)
        hidden_states = self.dropout(hidden_states)

        _, nikud_logits = self.menaked(hidden_states)
        # ^ nikud_logits: MenakedLogitsOutput

        additional_logits = self.mlp(hidden_states)
        # ^ shape: (batch_size, n_chars_padded, 3) [hatama, mobile shva, and prefix]

        return MenakedLogitsOutput(
            nikud_logits.nikud_logits, nikud_logits.shin_logits, additional_logits
        )

    def encode(
        self, sentences: list[str], tokenizer: BertTokenizerFast, padding="longest"
    ):
        sentences = [remove_nikud(sentence) for sentence in sentences]

        # Assert the lengths are within the tokenizer's max limit
        assert all(
            len(sentence) + 2 <= tokenizer.model_max_length for sentence in sentences
        ), (
            f"All sentences must be <= {tokenizer.model_max_length}, please segment and try again"
        )

        # Tokenize the inputs and return the tensor format
        inputs = tokenizer(
            sentences,
            padding=padding,
            truncation=True,
            return_tensors="pt",
            return_offsets_mapping=True,
        )
        offset_mapping = inputs.pop("offset_mapping")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        return inputs, offset_mapping

    def decode(
        self,
        sentences,
        offset_mapping,
        nikud_predictions,
        shin_predictions,
        hatama_predictions,
        vocal_shva_predictions,
        prefix_predictions,
        mark_matres_lectionis: str = "",
    ):
        ret = []
        for sent_idx, (sentence, sent_offsets) in enumerate(
            zip(sentences, offset_mapping)
        ):
            output = []
            prev_index = 0
            for idx, offsets in enumerate(sent_offsets):
                # Add anything missed
                if offsets[0] > prev_index:
                    output.append(sentence[prev_index : offsets[0]])
                if offsets[1] - offsets[0] != 1:
                    continue

                # Get the next character
                char = sentence[offsets[0] : offsets[1]]
                prev_index = offsets[1]

                if not is_hebrew_letter(char):
                    output.append(char)
                    continue

                # Apply the predictions to the character
                nikud = self.config.nikud_classes[nikud_predictions[sent_idx][idx]]
                shin = (
                    ""
                    if char != "ש"
                    else self.config.shin_classes[shin_predictions[sent_idx][idx]]
                )

                # Check for matres lectionis
                if nikud == self.config.mat_lect_token:
                    if not is_matres_letter(char):
                        nikud = ""  # Don't allow matres on irrelevant letters
                    elif mark_matres_lectionis is not None:
                        nikud = mark_matres_lectionis
                    else:
                        nikud = ""  # No marking, but don't skip the character

                # Apply hatama, mobile shva, and prefix predictions
                hatama = HATAMA_CHAR if hatama_predictions[sent_idx][idx] == 1 else ""
                vocal_shva = (
                    VOCAL_SHVA_CHAR
                    if vocal_shva_predictions[sent_idx][idx] == 1
                    else ""
                )
                prefix = PREFIX_CHAR if prefix_predictions[sent_idx][idx] == 1 else ""

                output.append(char + shin + nikud + hatama + vocal_shva + prefix)

            output.append(sentence[prev_index:])
            ret.append("".join(output))

        return ret

    def get_predictions_from_output(self, output) -> ModelPredictions:
        """Extract predictions from an existing forward pass output to avoid running forward twice."""
        # Extract the logits from the model output
        nikud_logits = output.detach()
        additional_logits = output.additional_logits.detach()

        # Get predictions from logits
        nikud_predictions = nikud_logits.nikud_logits.argmax(dim=-1).tolist()
        shin_predictions = nikud_logits.shin_logits.argmax(dim=-1).tolist()

        hatama_predictions = (additional_logits[..., 0] > 0).int().tolist()
        vocal_shva_predictions = (additional_logits[..., 1] > 0).int().tolist()
        prefix_predictions = (additional_logits[..., 2] > 0).int().tolist()

        return ModelPredictions(
            nikud=nikud_predictions,
            shin=shin_predictions,
            hatama=hatama_predictions,
            vocal_shva=vocal_shva_predictions,
            prefix=prefix_predictions,
        )

    def create_predictions(self, inputs) -> ModelPredictions:
        output = self.forward(inputs)
        return self.get_predictions_from_output(output)

    @torch.no_grad()
    def predict(
        self,
        sentences,
        tokenizer: BertTokenizerFast,
        mark_matres_lectionis: str = None,
        padding="longest",
    ):
        # Step 1: Encoding (tokenizing sentences)
        inputs, offset_mapping = self.encode(sentences, tokenizer, padding)

        # Step 2: Making predictions
        predictions = self.create_predictions(inputs)

        # Step 3: Decoding (reconstructing the sentences with predictions)
        result = self.decode(
            sentences,
            offset_mapping,
            predictions.nikud,
            predictions.shin,
            predictions.hatama,
            predictions.vocal_shva,
            predictions.prefix,
            mark_matres_lectionis,
        )

        return result
