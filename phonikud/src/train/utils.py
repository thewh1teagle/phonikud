import humanize

def print_model_size(model):
    def count_params(module):
        return sum(p.numel() for p in module.parameters())

    def pretty(n):
        return humanize.intword(n)

    print("🔍 Model breakdown:")
    print(f"  ⚙️  MLP: {pretty(count_params(model.mlp))} parameters")
    print(f"  📘 Menaked: {pretty(count_params(model.menaked))} parameters")
    print(f"  🧠  BERT: {pretty(count_params(model.bert))} parameters")
