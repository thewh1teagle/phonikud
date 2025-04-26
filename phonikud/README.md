# Phonikud

Phonikud is a Hebrew diacritizer based on [dictabert-large-char-menaked](https://huggingface.co/dicta-il/dictabert-large-char-menaked) with added phonetic symbols for Shva Na and Atma'a (Stress).

## Added Symbols

- Stress (Atma'a): `\u05ab` also called `ole`

- Mobile Shva (Shva Na): `\u05bd` also called `meteg`

## Train

Add text files with diacritics, including Atma'a and Shva Na, to `data/train`.

Example input: `סֵ֫לֵרִי בְּֽמַעְבַּד מָזוֹן`

```console
uv run src/train.py
```

## Inference

Run the model for testing:

```console
uv run src/test.py
```

TODO:
* Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
* Clean up flags in scripts
* Check that stress/shva targets are guaranteed to be aligned with tokenized characters (use `return_offsets_mapping=True`? cf. dictabert code)