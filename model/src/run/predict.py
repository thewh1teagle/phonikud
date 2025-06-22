"""
Simple prediction script
"""

from src.model.phonikud_model import (
    PhoNikudModel,
    NIKUD_HASER,
    remove_nikud,
    ENHANCED_NIKUD,
)
from transformers import AutoTokenizer
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
from phonikud.utils import normalize


def main():
    # Hardcoded text
    text = "שלום עולם"
    
    # Load model and tokenizer
    model_path = "thewh1teagle/phonikud"
    model = PhoNikudModel.from_pretrained(model_path, trust_remote_code=True)
    tokenizer: BertTokenizerFast = AutoTokenizer.from_pretrained(model_path)
    model.to("cuda")  # type: ignore
    model.eval()

    # Process the text
    text = normalize(text.strip())
    without_nikud = remove_nikud(text, additional=ENHANCED_NIKUD)
    
    if without_nikud:
        predicted = model.predict(
            [without_nikud], tokenizer, mark_matres_lectionis=NIKUD_HASER
        )[0]
        predicted = normalize(predicted)
        print(predicted)


if __name__ == "__main__":
    main()
