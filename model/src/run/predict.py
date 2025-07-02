"""
Simple prediction script
"""

from tap import Tap
from src.model.phonikud_model import (
    PhonikudModel,
    NIKUD_HASER,
    remove_nikud,
    ENHANCED_NIKUD,
)
from transformers import AutoTokenizer
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from phonikud.utils import normalize


class PredictArgs(Tap):
    model: str = "ckpt/best_wer"
    "Path or name of the pretrained model"

    text: str = "כמה אתה חושב שזה יעלה לי? אני מגיע לשם רק בערב.."
    "Hebrew text to add nikud to"

    device: str = "cuda"
    "Device to run inference on"


def main():
    args = PredictArgs().parse_args()

    # Load model and tokenizer
    model = PhonikudModel.from_pretrained(args.model, trust_remote_code=True)
    tokenizer: BertTokenizerFast = AutoTokenizer.from_pretrained(args.model)
    model.to(args.device)  # type: ignore
    model.eval()

    # Process the text
    text = normalize(args.text.strip())
    without_nikud = remove_nikud(text, additional=ENHANCED_NIKUD)

    if without_nikud:
        predicted = model.predict(
            [without_nikud], tokenizer, mark_matres_lectionis=NIKUD_HASER
        )[0]
        predicted = normalize(predicted)
        print(predicted)


if __name__ == "__main__":
    main()
