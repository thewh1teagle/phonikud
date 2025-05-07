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
uv run src/train/main.py
```

## Run

Run the model with:

```console
uv run examples/simple.py
```

## Upload to HuggingFace

```console
uv pip install huggingface_hub
git config --global credential.helper store # Allow clone private repo from HF
huggingface-cli login --token "token" --add-to-git-credential # https://huggingface.co/settings/tokens 
uv run huggingface-cli upload --repo-type model phonikud ./ckpt/last.ckpt ./ckpt/last.ckpt

# Fetch the model by
git lfs install
git clone https://huggingface.co/user/phonikud

# Fetch file by
huggingface-cli download --repo-type dataset user/some-dataset some_file.7z --local-dir .
sudo apt install p7zip-full
7z x some_file.7z
```



## Export onnx

See [onnx_lib](onnx_lib)

## Gotchas

1. Hebrew not printed in terminal when using SSH

Run

```console
sudo locale-gen en_US.UTF-8
sudo update-locale LANG=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

Then, close the terminal and reconnect.

TODO:
* Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
* Clean up flags in scripts
* Check that stress/shva targets are guaranteed to be aligned with tokenized characters (use `return_offsets_mapping=True`? cf. dictabert code)