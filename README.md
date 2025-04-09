# Mishkal

Grapheme to phoneme in Hebrew

Convert Hebrew text into IPA for TTS systems and learning.

## Features

- Accurate lightweight niqqud model
- Convert text with niqqud to modern spoken phonemes
- Expand dates into text with niqqud
- Expand numbers into text with niqqud
- Mixed English in Hebrew with fallback
- Dictionaries with words, symbols, emojis

## Limitiation

The following hard to predict even from text with niqqud.

- Requires diacritized text
- `Shva na` and `Shva nah`
- `Stress` (`Atmaha` / `Milre` / `Milra`)
- `Kamatz Katan` (rarely used)

We cover these using dictionaries, and neural network is planned.

## Install

Due to ongoing development, it's recommend to install from git directly.

```console
pip install git+https://github.com/thewh1teagle/mishkal
```

You can find the package as well in `pypi.org/project/mishkal-hebrew`

## Play

See [Phonemize with Hebrew Space](https://huggingface.co/spaces/thewh1teagle/phonemize-in-hebrew)

## Examples

```python
from mishkal import phonemize
phonemes = phonemize('שָׁלוֹם עוֹלָם')
print(phonemes) # ʃaˈlom oˈlam
```

See [examples](examples)

## Docs

- Dictionaries prioritized based on `gold`, `silver`, `bronze`.
- It's recommend to add niqqud with [dicta-onnx](https://github.com/thewh1teagle/dicta-onnx) model
- Hebrew niqqud is normalized and deduplicated phonetically (simplified)
- Most of the Hebrew rules happen in `phonemize.py`
- Input chars: `!"'(),-.:` and `0x5B0` to `0x5E0` (normalized later)
- Output chars: `!"'(),-.:?abdefghijklmnoprsttstʃuvxzʃʒˈˌ`
- It's highly recommend to normalize Hebrew using `mishkal.normalize('שָׁלוֹם')` when training models

### Enhance vocabulary

One of the best ways to improve this library is to ~add words with phonemes to the dictionary~ create tagged sentences with shva na and atmaha. you can listen to it with [phoneme-synthesis](https://itinerarium.github.io/phoneme-synthesis/)

### Niqqud deduplication

- `Hataf segol` -> `Tsere`
- `Segol` -> `Tsere`
- `Hataf patah` -> `Patah`
- `Hataf qamatz` -> `Patah`
- `Qamats` -> `Patah`
- `Qamats katan` -> `Holam`
- `Hebrew Geresh` -> Regular `'` (`apostrophe`)

### Niqqud set and symbols

- `Shva`, `Tsere`, `Patah`, `Holam`, `Hirik`, `Qubuts`, `Dagesh` (`בכפךףו`),
- `Shin dot` (`ש`), `Sin dot` (`ש`), `'` (`ג'`), `Vav Holam` (`ו`)

### Hebrew phonemes

Constants

- `b` - Bet
- `v` - Vet, Vav
- `g` - Gimel
- `d` - Dalet
- `h` - He
- `z` - Zain
- `x` - Het, Haf
- `t` - Taf, Tet
- `j` - Yod
- `k` - Kuf, Kaf
- `l` - Lamed
- `m` - Mem
- `n` - Nun
- `s` - Sin, Samekh
- `f` - Fei
- `p` - Pei dgusha
- `r` - Resh
- `ts` - tsadik
- `ʃ` - Shin
- `tʃ` - Tsadik with geresh
- `dʒ` - Gimel with geresh (גִּ׳ירָפָה)
- `ʒ` - Zain with geresh (בֵּז׳)
- `ʔ` - Alef/Ayin
- `w` - Example: `walla`

Vowels

- `a` - Shamar
- `e` - Shemer
- `i` - Shimer
- `o` - Shomer
- `u` - Shumar

Symbols

- `ˈ` - stress (0x2C8) visually looks like apostrophe

### Mixed English

You can mix the phonemization of English by providing a fallback function that accepts an English string and returns phonemes.
See [examples/with_fallback.py](examples/with_fallback.py) for reference.
Note that if you use this with TTS, it is recommended to train the model on phonemized English. Otherwise, the model may not recognize the phonemes correctly.

### Notes

- There's no secondary stress (only Milel and Milra)
- The glottal stop/h sometimes omited
- Stress placed usually on the last syllable (milra), sometimes on one before milra (milhel) and rarely one before milhel
- See [Unicode Hebrew table](https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table)
- See [Modern Hebrew phonology](https://en.m.wikipedia.org/wiki/Modern_Hebrew_phonology)
