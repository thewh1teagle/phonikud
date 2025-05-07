from phonikud.src.model import NIKUD_HASER


def evaluate_model(model, tokenizer, eval_lines):
    print("🧪 Evaluating...")
    for line in eval_lines:
        result = model.predict([line], tokenizer, mark_matres_lectionis=NIKUD_HASER)
        print(result)
