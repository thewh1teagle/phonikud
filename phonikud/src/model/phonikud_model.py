import torch
from torch import nn
from dataclasses import dataclass
from transformers.utils import ModelOutput
from transformers import BertTokenizerFast
import re


from .dicta_model import (
    BertForDiacritization,
    is_hebrew_letter,
    is_matres_letter,
)


def remove_nikud(text: str, additional=""):
    """
    Remove nikud except meteg as we use it for Shva Na
    """
    return re.sub(f"[\u05b0-\u05bc\u05be-\u05c7{additional}]", "", text)


HATAMA_CHAR = "\u05ab"  # "ole" symbol marks hatama
MOBILE_SHVA_CHAR = "\u05bd"  # "meteg" symbol marks shva na (mobile shva)
PREFIX_CHAR = "|"  # vertical bar
NIKUD_HASER = "\u05af"  # not in use but dicta has it

PHONETIC_NIKUD = HATAMA_CHAR + MOBILE_SHVA_CHAR + PREFIX_CHAR + NIKUD_HASER


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


class PhoNikudModel(BertForDiacritization):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.mlp = nn.Sequential(nn.Linear(1024, 100), nn.ReLU(), nn.Linear(100, 3))
        # ^ predicts hatama, mobile shva, and prefix; outputs are logits

    def freeze_base_model(self):
        self.bert.eval()
        self.menaked.eval()
        for param in self.bert.parameters():
            param.requires_grad = False

        for param in self.menaked.parameters():
            param.requires_grad = False

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
        ), f"All sentences must be <= {tokenizer.model_max_length}, please segment and try again"

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
        mobile_shva_predictions,
        prefix_predictions,
        mark_matres_lectionis: str = None,
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
                        continue

                # Apply hatama, mobile shva, and prefix predictions
                hatama = HATAMA_CHAR if hatama_predictions[sent_idx][idx] == 1 else ""
                mobile_shva = (
                    MOBILE_SHVA_CHAR
                    if mobile_shva_predictions[sent_idx][idx] == 1
                    else ""
                )
                prefix = PREFIX_CHAR if prefix_predictions[sent_idx][idx] == 1 else ""

                output.append(char + shin + nikud + hatama + mobile_shva + prefix)

            output.append(sentence[prev_index:])
            ret.append("".join(output))

        return ret

    def create_predictions(self, inputs):
        output = self.forward(inputs)

        # Extract the logits from the model output
        nikud_logits = output.detach()
        additional_logits = output.additional_logits.detach()

        # Get predictions from logits
        nikud_predictions = nikud_logits.nikud_logits.argmax(dim=-1).tolist()
        shin_predictions = nikud_logits.shin_logits.argmax(dim=-1).tolist()

        hatama_predictions = (additional_logits[..., 0] > 0).int().tolist()
        mobile_shva_predictions = (additional_logits[..., 1] > 0).int().tolist()
        prefix_predictions = (additional_logits[..., 2] > 0).int().tolist()

        return (
            nikud_predictions,
            shin_predictions,
            hatama_predictions,
            mobile_shva_predictions,
            prefix_predictions,
        )

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
        (
            nikud_predictions,
            shin_predictions,
            hatama_predictions,
            mobile_shva_predictions,
            prefix_predictions,
        ) = self.create_predictions(inputs)

        # Step 3: Decoding (reconstructing the sentences with predictions)
        result = self.decode(
            sentences,
            offset_mapping,
            nikud_predictions,
            shin_predictions,
            hatama_predictions,
            mobile_shva_predictions,
            prefix_predictions,
            mark_matres_lectionis,
        )

        return result
