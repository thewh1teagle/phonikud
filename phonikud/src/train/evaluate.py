# evaluate.py
import os
from phonikud.src.model import remove_nikud, NIKUD_HASER
from data import get_diac_to_remove


def evaluate_model(model, tokenizer, args, components):
    print("⚙️ Testing...")
    model.eval()
    test_fn = os.path.join(args.data_dir, "eval/dummy.txt")
    with open(test_fn, "r", encoding="utf-8") as f:
        test_text = f.read().strip()
    for line in test_text.splitlines():
        if not line.strip():
            continue
        line = remove_nikud(line, additional=get_diac_to_remove(components))
        print(line)
        prediction = "".join(
            model.predict([line], tokenizer, mark_matres_lectionis=NIKUD_HASER)
        )
        print(prediction + "\n")
