"""
Copied from: https://huggingface.co/dicta-il/dictabert-large-char-menaked/blob/main/BertForDiacritization.py
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import torch
from torch import nn
from transformers.utils import ModelOutput
from transformers import BertPreTrainedModel, BertModel, BertTokenizerFast

# MAT_LECT => Matres Lectionis, known in Hebrew as Em Kriaa.
MAT_LECT_TOKEN = "<MAT_LECT>"
NIKUD_CLASSES = [
    "",
    MAT_LECT_TOKEN,
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


@dataclass
class MenakedLogitsOutput(ModelOutput):
    nikud_logits: torch.FloatTensor = None
    shin_logits: torch.FloatTensor = None

    def detach(self):
        return MenakedLogitsOutput(
            self.nikud_logits.detach(), self.shin_logits.detach()
        )


@dataclass
class MenakedOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[MenakedLogitsOutput] = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None


@dataclass
class MenakedLabels(ModelOutput):
    nikud_labels: Optional[torch.FloatTensor] = None
    shin_labels: Optional[torch.FloatTensor] = None

    def detach(self):
        return MenakedLabels(self.nikud_labels.detach(), self.shin_labels.detach())

    def to(self, device):
        return MenakedLabels(self.nikud_labels.to(device), self.shin_labels.to(device))


class BertMenakedHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        if not hasattr(config, "nikud_classes"):
            config.nikud_classes = NIKUD_CLASSES
            config.shin_classes = SHIN_CLASSES
            config.mat_lect_token = MAT_LECT_TOKEN

        self.num_nikud_classes = len(config.nikud_classes)
        self.num_shin_classes = len(config.shin_classes)

        # create our classifiers
        self.nikud_cls = nn.Linear(config.hidden_size, self.num_nikud_classes)
        self.shin_cls = nn.Linear(config.hidden_size, self.num_shin_classes)

    def forward(
        self, hidden_states: torch.Tensor, labels: Optional[MenakedLabels] = None
    ):
        # run each of the classifiers on the transformed output
        nikud_logits = self.nikud_cls(hidden_states)
        shin_logits = self.shin_cls(hidden_states)

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(
                nikud_logits.view(-1, self.num_nikud_classes),
                labels.nikud_labels.view(-1),
            )
            loss += loss_fct(
                shin_logits.view(-1, self.num_shin_classes), labels.shin_labels.view(-1)
            )

        return loss, MenakedLogitsOutput(nikud_logits, shin_logits)


class BertForDiacritization(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.bert = BertModel(config, add_pooling_layer=False)

        classifier_dropout = (
            config.classifier_dropout
            if config.classifier_dropout is not None
            else config.hidden_dropout_prob
        )
        self.dropout = nn.Dropout(classifier_dropout)

        self.menaked = BertMenakedHead(config)

        # Initialize weights and apply final processing
        self.post_init()

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple[torch.Tensor], MenakedOutput]:
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )

        bert_outputs = self.bert(
            input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        hidden_states = bert_outputs[0]
        hidden_states = self.dropout(hidden_states)

        loss, logits = self.menaked(hidden_states, labels)

        if not return_dict:
            return (loss, logits) + bert_outputs[2:]

        return MenakedOutput(
            loss=loss,
            logits=logits,
            hidden_states=bert_outputs.hidden_states,
            attentions=bert_outputs.attentions,
        )

    def predict(
        self,
        sentences: List[str],
        tokenizer: BertTokenizerFast,
        mark_matres_lectionis: str = None,
        padding="longest",
    ):
        sentences = [remove_nikkud(sentence) for sentence in sentences]
        # assert the lengths aren't out of range
        assert all(
            len(sentence) + 2 <= tokenizer.model_max_length for sentence in sentences
        ), (
            f"All sentences must be <= {tokenizer.model_max_length}, please segment and try again"
        )

        # tokenize the inputs and convert them to relevant device
        inputs = tokenizer(
            sentences,
            padding=padding,
            truncation=True,
            return_tensors="pt",
            return_offsets_mapping=True,
        )
        offset_mapping = inputs.pop("offset_mapping")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # calculate the predictions
        logits = self.forward(**inputs, return_dict=True).logits
        nikud_predictions = logits.nikud_logits.argmax(dim=-1).tolist()
        shin_predictions = logits.shin_logits.argmax(dim=-1).tolist()

        ret = []
        for sent_idx, (sentence, sent_offsets) in enumerate(
            zip(sentences, offset_mapping)
        ):
            # assign the nikud to each letter!
            output = []
            prev_index = 0
            for idx, offsets in enumerate(sent_offsets):
                # add in anything we missed
                if offsets[0] > prev_index:
                    output.append(sentence[prev_index : offsets[0]])
                if offsets[1] - offsets[0] != 1:
                    continue

                # get our next char
                char = sentence[offsets[0] : offsets[1]]
                prev_index = offsets[1]
                if not is_hebrew_letter(char):
                    output.append(char)
                    continue

                nikud = self.config.nikud_classes[nikud_predictions[sent_idx][idx]]
                shin = (
                    ""
                    if char != "ש"
                    else self.config.shin_classes[shin_predictions[sent_idx][idx]]
                )

                # check for matres lectionis
                if nikud == self.config.mat_lect_token:
                    if not is_matres_letter(char):
                        nikud = ""  # don't allow matres on irrelevant letters
                    elif mark_matres_lectionis is not None:
                        nikud = mark_matres_lectionis
                    else:
                        continue

                output.append(char + shin + nikud)
            output.append(sentence[prev_index:])
            ret.append("".join(output))

        return ret


ALEF_ORD = ord("א")
TAF_ORD = ord("ת")


def is_hebrew_letter(char):
    return ALEF_ORD <= ord(char) <= TAF_ORD


MATRES_LETTERS = list("אוי")


def is_matres_letter(char):
    return char in MATRES_LETTERS


import re

nikud_pattern = re.compile(r"[\u05B0-\u05BD\u05C1\u05C2\u05C7]")


def remove_nikkud(text):
    return nikud_pattern.sub("", text)
