# Architecture

## Pipeline

```
text → normalize → expand (numbers/dates/times) → phonemize → post-clean → phonemes
```

## Structure

- `phonikud/` — core library: phonemizer, FST rules, lexicon, utilities, text expander
- `phonikud_onnx/` — ONNX runtime wrapper for the nikud prediction model
- `model/` — nikud prediction model (adds diacritics to plain text)
- `tests/` — test tables (CSV) and test scripts
- `examples/` — usage examples

## How it works

1. **Normalize** — Unicode NFD, sort diacritics, deduplicate punctuation
2. **Expand** — numbers/dates/times to Hebrew words
3. **Phonemize** each Hebrew word:
   - Parse into Letter objects (char + diacritics)
   - Predict vocal shva if enabled
   - Add stress mark (milra by default) if not present
   - Run FST rules letter by letter (left to right, with prev/next context)
   - Post-normalize (trim final glottal stop/h, etc.)
4. **Fallback** — optional callback for non-Hebrew (Latin) text
5. **Schema** — convert plain IPA to modern Hebrew phonemes if requested
6. **Hyper-phonemes** — `[word](/phonemes/)` syntax bypasses the pipeline

## Model

Character-level BERT (based on dictabert-large-char-menaked) with the base model frozen and small adapter heads on top. The base model already predicts nikud and shin/sin dot; the adapters add hatama, vocal shva, and prefix prediction. Predicts 5 things per character:

1. **Nikud** (vowel marks) — 29 classes
2. **Shin/Sin dot** — 2 classes
3. **Hatama** (stress) — binary
4. **Vocal shva** — binary
5. **Prefix marker** — binary

Exported to ONNX for fast inference without PyTorch. The model adds diacritics; the FST rules then convert diacritics to phonemes.

## FST rules

Each letter is processed with prev/next context. Priority order:
1. Nikud haser (skip letter)
2. Geresh (consonant override)
3. Dagesh beged-kefet (consonant override)
4. Vav (vowel/consonant — most complex, ~12 variants)
5. Shin/Sin (dot determines s vs sh)
6. Patah gnuva (final guttural + patah)
7. Kamatz before hataf-kamatz (produces 'o')
8. Em kriah (silent alef mid-word)
9. Yud kriah (silent yud mid-word)
10. Default: consonant table + nikud vowel table
