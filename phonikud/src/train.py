from argparse import ArgumentParser
from transformers import AutoModel, AutoTokenizer


def get_opts():
    parser = ArgumentParser()
    parser.add_argument('-m', '--model_checkpoint',
                        default='dicta-il/dictabert-large-char-menaked', type=str)
    parser.add_argument('-d', '--device',
                        default='cuda', type=str)


def main():
    args = get_opts()

    print("Loading model...")

    tokenizer = AutoTokenizer.from_pretrained(args.model_checkpoint)
    model = AutoModel.from_pretrained(
        args.model_checkpoint, trust_remote_code=True)
    model.to(args.device)

    print("Testing...")

    model.eval()
    sentence = 'בשנת 1948 השלים אפרים קישון את לימודיו בפיסול מתכת ובתולדות האמנות והחל לפרסם מאמרים הומוריסטיים'
    print(model.predict([sentence], tokenizer))

    print("Done")


if __name__ == "__main__":
    main()
