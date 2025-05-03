# Mishkal

Grapheme to phoneme in Hebrew

Convert Hebrew text into IPA for TTS systems and learning.

## Features

- Lightweight nikud model
- (WIP) Enhanced nikud model with phonetic features (stress, shva na, ...) see [phonikud](phonikud)
- Run onnx models with realtime support
- Convert text with nikud to modern spoken phonemes
- Expand dates into text with nikud
- Expand numbers into text with nikud
- Mixed English in Hebrew with fallback
- Dictionaries with words, symbols, emojis

## Limitiation

- The library depends on text with nikud
- the following hard to predict even from text with nikud
  - `Milel` - 
      position of `Hat'ama` / `Stress`. 
      most of the time it's `Milra`
  - `Shva Na`. most of the time it's regular `Shva`


We cover these using predictions, and enhanced nakdan is planned.

## Install

Due to ongoing development, it's recommend to install from git directly.

```console
pip install git+https://github.com/thewh1teagle/mishkal
```

You can find the package as well in `pypi.org/project/mishkal-hebrew`

## Play

See [Phonemize with Hebrew Space](https://huggingface.co/spaces/thewh1teagle/phonemize-in-hebrew)

## Usage

```python
from mishkal import phonemize
phonemes = phonemize('שָׁלוֹם עוֹלָם')
print(phonemes) # ʃalˈom olˈam
```

Please use [dicta-onnx](https://github.com/thewh1teagle/dicta-onnx) for adding diacritics.

## Examples

See [examples](examples)

## Docs

- It's recommend to add nikud with [dicta-onnx](https://github.com/thewh1teagle/dicta-onnx) model
- Hebrew nikud is normalized
- Most of the Hebrew rules happen in `phonemize.py`
- It's highly recommend to normalize Hebrew using `mishkal.normalize('שָׁלוֹם')` when training models

### Enhance vocabulary

One of the best ways to improve this library is to ~add words with phonemes to the dictionary~ create tagged sentences with shva na and hat'ama. you can listen to it with [phoneme-synthesis](https://itinerarium.github.io/phoneme-synthesis/)

### Deduplication

- Hebrew Geresh -> `'` (single quote)

### Nikud set and symbols

- Chars from `\u05b0` to `\u05ea` (Letters and nikud)
- `'"` (Gershaim),
- `\u05ab` (Hat'ama)
- `\u05bd` (Shva Na)

`\u05ab` and `\u05bd` are not standard - we invented them to mark `Hat'ama` and `Shva Na` clearly.


See [Hebrew UTF-8](https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table)


### Hebrew phonemes

Stress marks (1)

- `ˈ` - stress, visually looks like single quote, but it's `\u02c8`

Vowels (5)

- `a` - Shamar
- `e` - Shemer
- `i` - Shimer
- `o` - Shomer
- `u` - Shumar

Consonants (24)

- `b` - Bet
- `v` - Vet, Vav
- `d` - Daled
- `h` - Hey
- `z` - Zain
- `χ` - Het, Haf
- `t` - Taf, Tet
- `j` - Yud
- `k` - Kuf, Kaf
- `l` - Lamed
- `m` - Mem
- `n` - Nun
- `s` - Sin, Samekh
- `f` - Fey
- `p` - Pey
- `ts` - Tsadik
- `tʃ` - Tsadik with Geresh (`צִ'יפְּס`)
- `w` - Example: `וָואלָה`
- `ʔ` - Alef/Ayin, visually looks like `?`, but it's `\u0294`
- `ɡ` - Gimel, visually looks like `g`, but its actually `\u0261`
- `ʁ` - Resh `\u0281`
- `ʃ` - Shin `\u0283`
- `ʒ` - Zain with Geresh (`בֵּז׳`) `\u0292`
- `dʒ` - Gimel with Geresh (`גִּ׳ירָפָה`)

### Mixed English

You can mix the phonemization of English by providing a fallback function that accepts an English string and returns phonemes.
See [examples/with_fallback.py](examples/with_fallback.py) for reference.
Note that if you use this with TTS, it is recommended to train the model on phonemized English. Otherwise, the model may not recognize the phonemes correctly.
Cool fact: modern Hebrew phonemes mostly exist in English except `ʔ` (Alef/Ayin), Resh `ʁ` and `χ` (Het).

## How It Works

To train TTS models, it’s essential to represent speech accurately. Plain Hebrew text is ambiguous without diacritics, and even with them, Shva Na and Hat'ama can cause confusion. For example, "אני אוהב אורז" (I like rice) and "אני אורז מזוודה" (I pack a suitcase) share the same diacritics for "אורז" but have different Hat'ama.

The workflow is as follows:

1. Add diacritics using a standard Nakdan.


2. Enhance the diacritics with an enhanced Nakdan that adds invented diacritics for Hat'ama and Shva Na.


3. Convert the text with diacritics to phonemes (alphabet characters that represent sounds) using this library, based on coding rules.


4. Train the TTS model on phonemes, and at runtime, feed the model phonemes to generate speech.



This ensures accurate and clear speech synthesis.

## Datasets for TTS

- [ILSpeech](https://huggingface.co/datasets/thewh1teagle/ILSpeech) (mit)
- [Saspeech](https://www.openslr.org/134) (Non commercial)

### Notes

- The default schema is `modern`. you can use `plain` schema for simplicify (eg. `x` instead of `χ`). use `phonemize(..., schema='plain')`
- There's no secondary stress (only `Milel` and `Milra`)
- The `ʔ`/`h` phonemes trimmed from the suffix
- Stress placed usually on the last syllable - `Milra`, sometimes on one before - `Milel` and rarely one before `Milel`
- Stress should be placed in the syllable always **before vowel** and _NOT_ in the first character of the syllable
- See [Unicode Hebrew table](https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table)
- See [Modern Hebrew phonology](https://en.m.wikipedia.org/wiki/Modern_Hebrew_phonology)
