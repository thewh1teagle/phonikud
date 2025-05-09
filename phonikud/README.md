# Phonikud

Phonikud is a Hebrew diacritizer based on [dictabert-large-char-menaked](https://huggingface.co/dicta-il/dictabert-large-char-menaked) with added phonetic symbols for Shva Na and Hat'ama (Stress).

## Added Symbols

- Hat'ama (Stress): `\u05ab` also called `ole`
- Mobile Shva (Shva Na): `\u05bd` also called `meteg`
- Prefix: vertical bar `|`

Example: `סֵ֫לֵרִי בְּֽ|מַעְבַּד מָזוֹן`

## Setup

```console
pip install uv
uv sync
```

# Prepare data

Add text files with diacritics, including Hat'ama and Shva Na, to `data/train`.

Example input: `סֵ֫לֵרִי בְּֽ|מַעְבַּד מָזוֹן`

```console
wget https://huggingface.co/datasets/thewh1teagle/phonikud-data/resolve/main/knesset_nikud_v4.txt.7z
sudo apt install p7zip-full -y
7z x knesset_nikud_v4.txt.7z
mv knesset_nikud_v4.txt data/train/
```

## Train

```console
uv run src/train/main.py
```

## Monitor loss

```console
uv run tensorboard  --logdir ./ckpt
```

## Monitor GPU

```console
uv pip install nvitop
uv run nvitop
```

## Run

Run the model with:

```console
uv run src/run/main.py -m path/to/checkpoint/
```

## Export onnx

See [onnx_lib](onnx_lib)

## Upload to HuggingFace

```console
uv pip install huggingface_hub
git config --global credential.helper store # Allow clone private repo from HF
huggingface-cli login --token "token" --add-to-git-credential # https://huggingface.co/settings/tokens
uv run huggingface-cli upload --repo-type model phonikud ./ckpt/last ./ckpt/last

# Fetch the model by
git lfs install
git clone https://huggingface.co/user/phonikud

# Fetch file by
huggingface-cli download --repo-type dataset user/some-dataset some_file.7z --local-dir .
sudo apt install p7zip-full
7z x some_file.7z
```

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

- Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
- Check that hatama/shva targets are guaranteed to be aligned with tokenized characters (use `return_offsets_mapping=True`? cf. dictabert code)
