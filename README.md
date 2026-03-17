<p align="center">
  <a target="_blank" href="https://phonikud.github.io">
    <img
        width="110px"
        alt="Phonikud logo"
        src="./design/logo.svg"
    />
  </a>
</p>

<h1 align="center">Phonikud – Hebrew Grapheme-to-Phoneme</h1>

<p align="center">
  <em>Convert Hebrew text into IPA for TTS, speech technology, and language learning</em>
</p>

<p align="center">
  <a target="_blank" href="https://phonikud.github.io">
    🌐 Project Page
  </a>
  &nbsp; | &nbsp; 
  <a target="_blank" href="https://arxiv.org/abs/2506.12311">
    📄 Research Paper
  </a>
</p>

<hr />

## Features

- Nikud model with phonetic marks 🧠
- Convert nikud text to modern spoken phonemes 🗣️
- Expand dates, numbers, etc 📚
- Handle mixed English/Hebrew with fallback 🌍
- Real time onnx model support 💫
- Lightweight TTS library: [phonikud-tts](https://github.com/thewh1teagle/phonikud-tts) 🎤

## Setup

1. Install with pip

```console
pip install phonikud phonikud-onnx
```

2. Download [phonikud-1.0.int8.onnx](https://huggingface.co/thewh1teagle/phonikud-onnx/resolve/main/phonikud-1.0.int8.onnx)

3. Use with

```python
from phonikud_onnx import Phonikud
from phonikud import phonemize

model = Phonikud("./phonikud-1.0.int8.onnx")
text = "שלום עולם"
vocalized = model.add_diacritics(text)
phonemes = phonemize(vocalized)
print(phonemes) # ʃalˈom olˈam
```

## Examples

See [examples](examples)

## Play 🕹️

See [TTS with Hebrew Space](https://huggingface.co/spaces/thewh1teagle/phonikud-tts)

See [Phonemize with Hebrew Space](https://huggingface.co/spaces/thewh1teagle/phonemize-in-hebrew)

## Community

[![Discord](https://img.shields.io/badge/chat-discord-7289da.svg)](https://discord.gg/trfCMfhhum)

Come chat about Hebrew TTS!

## Docs 📚

- It is recommend to add nikud with [phonikud-onnx](phonikud_onnx) model
- Hebrew nikud is normalized
- Most Hebrew rules are handled in phonemize.py - a fast rule-based [FST](https://en.wikipedia.org/wiki/Finite-state_transducer) for converting text to phonemes.
- It is highly recommend to normalize Hebrew using `phonikud.normalize('שָׁלוֹם')` when training models

### Nikud set and symbols

- Chars from `\u05b0` to `\u05ea` (Letters and diacritics)
- `'"` (Gershaim),
- `\u05ab` (Hat'ama eg. `טח֫ינה` != `טחינ֫ה` `tahini` != `grinding`)
- `\u05bd` (Vocal Shva eg. `תְֽפרְסם` notice Meteg in `ת`)
- `|` (Prefix letters eg. `ב|ירושלים`)

`\u05ab` and `\u05bd` are not standard - we invented them to mark `Hat'ama` and `Vocal Shva` clearly.

See [Hebrew UTF-8](https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table)

### Hebrew phonemes 🔠

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
- `ɡ` - Gimel, visually looks like `g`, but it's actually `\u0261`
- `ʁ` - Resh `\u0281`
- `ʃ` - Shin `\u0283`
- `ʒ` - Zain with Geresh (`בֵּז׳`) `\u0292`
- `dʒ` - Gimel with Geresh (`גִּ׳ירָפָה`)

Character set:

`abdefhijklmnopstuvwzɡʁʃʒʔˈχ`

### Mixed English 🌎

You can mix the phonemization of English by providing a fallback function that accepts an English string and returns phonemes.
Note: if you use this with TTS, it is recommended to train the model on phonemized English. Otherwise, the model may not recognize the phonemes correctly.
Cool fact: modern Hebrew phonemes mostly exist in English except `ʔ` (Alef/Ayin), Resh `ʁ` and `χ` (Het).

## How It Works 🔧

To train TTS models, it’s essential to represent speech accurately. Plain Hebrew text is ambiguous without diacritics, and even with them, Vocal Shva and Hat'ama can cause confusion. For example, "אני אוהב אורז" (I like rice) and "אני אורז מזוודה" (I pack a suitcase) share the same diacritics for "אורז" but have different Hat'ama.

The workflow is as follows:

1. Add diacritics using a standard Nakdan.

2. Enhance the diacritics with an enhanced Nakdan that adds invented diacritics for Hat'ama and Vocal Shva. See [phonikud](phonikud)

3. Convert the text with diacritics to phonemes (alphabet characters that represent sounds) using this library, based on coding rules.

4. Train the TTS model on phonemes, and at runtime, feed the model phonemes to generate speech.

This ensures accurate and clear speech synthesis. Since the output phonemes are similar to English, we can fine tune an English model with as little as one hour of Hebrew data.

## ℹ️ Limitations

- Some of the _nikud_ may sound a bit formal - similar to other models
- Some words get the same _nikud_ but different _hat'ama_ - not always accurate
- Does not currently support user choice between multiple possibilities, or _nikud_ hints in input
- Basic support for non-words (gibberish, typos) - not always handled
- Names and non-Hebrew words are sometimes predicted incorrectly

💡 You can always pass your own phonemes using markdown-like syntax:  
`[...title](/ʔentsiklopˈedja/)`

## 🧠 Future Ideas

- _Multilingual LLM Expander_

  Expand numbers, emojis, dates, times, and more using a lightweight multilingual LLM or transformer.  
  The idea is to train a small model on pairs of raw text → expanded text, making it easier to generate speech-friendly inputs.

- _Punctuation model_

  Train model to restore missing punctuation for better intonations

- _Transformer/LLM G2P_

  Skip coding rules - make a dataset with current G2P, then train a end-to-end model on text to phonemes.

## Datasets

- [ILSpeech](https://huggingface.co/datasets/thewh1teagle/ILSpeech) (speech, non commercial)
- [Saspeech](https://huggingface.co/datasets/thewh1teagle/saspeech) (speech, non commercial)
- [phonikud-data](https://huggingface.co/datasets/thewh1teagle/phonikud-data) (nikud and phonetics, cc-4.0)
- [phonikud-phonemes-data](https://huggingface.co/datasets/thewh1teagle/phonikud-phonemes-data) (enhanced nikud alongside IPA phonemes, cc-4.0)

## License

Phonikud G2P (the code in this repository) is licensed under CC BY 4.0 (open use).
Note: The datasets included or referenced in this repository have their own separate licenses.
Please make sure to read both the Phonikud license (see LICENSE) and the individual dataset licenses carefully before use.

### Notes

- The default schema is `modern`. you can use `plain` schema for simplicify (eg. `x` instead of `χ`). use `phonemize(..., schema='plain')`
- There's no secondary stress (only `Milel` and `Milra`)
- The `ʔ`/`h` phonemes trimmed from the suffix
- Stress placed usually on the last syllable - `Milra`, sometimes on one before - `Milel` and rarely one before `Milel`
- Stress should be placed in the syllable always **before vowel** and _NOT_ in the first character of the syllable
- See [Unicode Hebrew table](https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table)
- See [Modern Hebrew phonology](https://en.m.wikipedia.org/wiki/Modern_Hebrew_phonology)
- Initially we called Vocal Shva as Shva Na, but we learned that in modern Hebrew spoken Shva is different from written Shva Na, catchy name for it: `שווא נשמע`. See [Shva#Pronunciation_in_Modern_Hebrew](https://en.wikipedia.org/wiki/Shva#Pronunciation_in_Modern_Hebrew)
- To type Hebrew diacritics, use `Right ALT` (`Windows`), `Left Option` (`macOS`), or `Long Press` on the corresponding letter (`Google Keyboard`) based on the diacritic's name. eg. for `Katmaz` use `Alt` + `ק`. for `Hatama` use `Alt` + `^`. for Vocal Shva use `Alt` + `&`

### Testing 🧪

Run `uv run pytest`

## Citation

If you find this code or our data helpful in your research or work, please cite the following paper.

```bibtex
@misc{kolani2025phonikud,
  title={Phonikud: Hebrew Grapheme-to-Phoneme Conversion for Real-Time Text-to-Speech},
  author={Yakov Kolani and Maxim Melichov and Cobi Calev and Morris Alper},
  year={2025},
  eprint={2506.12311},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2506.12311},
}
```

## Credits

Special thanks ❤️ to [dicta-il](https://huggingface.co/dicta-il/dictabert-large-char-menaked) for their amazing Hebrew diacritics model ✨ and the dataset that made this possible!  

Huge thanks to [Oron Kam](https://www.linkedin.com/in/oronkam/) for helping with training the best Hebrew Whisper IPA so far! 🙌

