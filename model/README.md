# Phonikud

Phonikud is a Hebrew diacritizer based on [dictabert-large-char-menaked](https://huggingface.co/dicta-il/dictabert-large-char-menaked) with added enhanced diacritics for Vocal Shva and Hat'ama (Stress).

## Added Symbols

- Hat'ama (Stress): `\u05ab` also called `ole`
- Vocal Shva (e): `\u05bd` also called `meteg`
- Prefix: vertical bar `|`

Example: `סֵ֫לֵרִי בְּֽ|מַעְבַּד מָזוֹן`

## Why

Hebrew is usually written without nikud (vowels), so the pronunciation is unclear.  
To convert Hebrew to phonemes, we need more than just plain text:

- **Nikud** must be added — it's missing from the text.
- **Shva** can be vocal (e) or silent — usually silent.
- **Hat'ama** (word stress) isn’t marked — usually on the last syllable.
- **Prefix letters** (e.g., ו־ / ב־) make words harder to analyze.

Phonetic details like these are essential for accurate pronunciation.

## Model card

See [model card](https://huggingface.co/thewh1teagle/phonikud) on HuggingSpace 🤗

## Setup

```console
pip install uv
uv sync
```

# Prepare data

Add text files with diacritics, including Hat'ama and vocal Shva, to `data/`.

Example input: `סֵ֫לֵרִי בְּֽ|מַעְבַּד מָזוֹן`

```console
wget https://huggingface.co/datasets/thewh1teagle/phonikud-data/resolve/main/knesset_nikud_v6.txt.7z
sudo apt install p7zip-full -y
7z x knesset_nikud_v6.txt.7z
cp knesset_nikud_v6.txt data/
```

## Train

```console
uv run src/train/main.py \
    --device cuda \
    --checkpoint_interval 1758 \
    --wandb_mode online \
    --val_split 0.05 \
    --early_stopping_patience 0 \
    --num_workers 16 \
    --learning_rate 5e-3 \
    --epochs 999999 \
    --batch_size 128 \
    --wandb_mode online \
    --max_lines 1000000
```

## Monitor loss

```console
uv run tensorboard  --logdir ./ckpt
```

You can also enable cloud wandb with

```console
uv run src/train/main.py --wandb_mode online
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

See [phonikud-onnx](../phonikud_onnx)

## Upload to HuggingFace

```console
uv pip install huggingface_hub
git config --global credential.helper store # Allow clone private repo from HF
huggingface-cli login --token "token" --add-to-git-credential # https://huggingface.co/settings/tokens
uv run huggingface-cli upload --repo-type model phonikud ./ckpt/path # upload contents of the folder

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

2. Cuda version issues

Run

```console
uv pip install --refresh -U torch
```

TODO:

- Organize train/val/test splits -- track val performance over time, log to tensorboard/wandb, ...
- Check that hatama/shva targets are guaranteed to be aligned with tokenized characters (use `return_offsets_mapping=True`? cf. dictabert code)
