# Phonikud

Phonikud is a Hebrew diacritizer based on [dictabert-large-char-menaked](https://huggingface.co/dicta-il/dictabert-large-char-menaked) with added phonetic symbols for Shva Na and Hat'ama (Stress).

## Added Symbols

- Stress (Hat'ama): `\u05ab` also called `ole`

- Mobile Shva (Shva Na): `\u05bd` also called `meteg`

## Setup

```console
uv sync
```

#  Prepare data

Add text files with diacritics, including Hat'ama and Shva Na, to `data/train`.

Example input: `סֵ֫לֵרִי בְּֽמַעְבַּד מָזוֹן`

```console
wget https://github.com/thewh1teagle/mishkal/releases/download/model-files-v1.0/phonikud_data_v1.7z
7z x phonikud_data_v1.7z
mv phonikud_data_v1/* data/train/
```

## Train

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