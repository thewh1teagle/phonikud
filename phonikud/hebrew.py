"""
Hebrew Phonemizer

Fast rule-based FST that converts Hebrew text to phonemes.
See https://en.wikipedia.org/wiki/Finite-state_transducer

Rules implemented:
1. Nikud Haser
2. Em Kriah
3. Yud Kriah
4. Shin Sin
5. Patah Gnuva
6. Geresh
7. Dagesh (Beged Kefet & Vav)
8. Kamatz & Kamatz Katan
9. Consonants & Vowels
10. Hatama (Stress)

Reference:
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
- https://he.wikipedia.org/wiki/הברה
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://hebrew-academy.org.il/2010/03/24/צהרים-נעמי-הגיית-קמץ-לפני-חט
- https://hebrew-academy.org.il/2022/03/03/מלעיל-ומלרע-על-ההטעמה-בעברית
"""

import re
from phonikud import lexicon
from phonikud.utils import sort_stress
from phonikud.variants import Letter
from phonikud.lexicon import NIKUD, NIKUD_PATAH_LIKE_PATTERN

_D, _SH, _HO, _HI = NIKUD["DAGESH"], NIKUD["SHVA"], NIKUD["HOLAM"], NIKUD["HIRIK"]
_KA, _PA, _TS, _SE = NIKUD["KAMATZ"], NIKUD["PATAH"], NIKUD["TSERE"], NIKUD["SEGOL"]
_KU, _VS, _SI, _HK = (
    NIKUD["KUBUTS"],
    NIKUD["VOCAL_SHVA"],
    NIKUD["SIN"],
    NIKUD["HATAF_KAMATZ"],
)
_PAT_RE = re.compile(NIKUD_PATAH_LIKE_PATTERN)
_GNUVA = {"ח": "ax", "ה": "ah", "ע": "a"}
_LP = lexicon.LETTERS_PHONEMES


def _clean(out):
    return [p for p in out if p and all(c in lexicon.SET_PHONEMES for c in p)]


def _vowels(cur):
    return [lexicon.NIKUD_PHONEMES.get(n, "") for n in cur.all_diac]


def _stress(cur):
    return [lexicon.STRESS_PHONEME] if lexicon.HATAMA_DIACRITIC in cur.all_diac else []


def _out(cur, con, vow=None, skip=0):
    out = ([con] if con else []) + (vow if vow is not None else _vowels(cur))
    return _clean(sort_stress(out)), skip


def _vav_vowel(d):
    if _PAT_RE.search(d):
        return "va"
    if _TS in d or _SE in d or _VS in d:
        return "ve"
    if _HO in d:
        return "o"
    if _KU in d or _D in d:
        return "u"
    if _HI in d:
        return "vi"
    return None


def phonemize_word(letters: list[Letter]) -> list[str]:
    phonemes, i = [], 0
    while i < len(letters):
        prev = letters[i - 1] if i > 0 else None
        nxt = letters[i + 1] if i + 1 < len(letters) else None
        p, skip = _letter(letters[i], prev, nxt)
        phonemes.extend(p)
        i += skip + 1
    return phonemes


def _letter(cur: Letter, prev: Letter | None, nxt: Letter | None):
    d, ch, s = cur.diac, cur.char, _stress(cur)

    # Skip letter marked as nikud haser
    if lexicon.NIKUD_HASER_DIACRITIC in cur.all_diac:
        return [], 0

    # Geresh overrides consonant (tav-geresh also skips vowels)
    if "'" in d and ch in lexicon.GERESH_PHONEMES:
        return _out(cur, lexicon.GERESH_PHONEMES[ch], vow=[] if ch == "ת" else None)

    # Dagesh beged-kefet overrides consonant
    if _D in d and ch + _D in _LP:
        return _out(cur, _LP[ch + _D])

    # Vav — complex vowel/consonant
    if ch == "ו" and lexicon.NIKUD_HASER_DIACRITIC not in cur.all_diac:
        return _vav(cur, prev, nxt)

    # Shin/Sin
    if ch == "ש":
        return _shin(cur, prev, nxt)

    # Patah gnuva — final patah on guttural
    if not nxt and _PA in d and ch in _GNUVA:
        return _out(cur, _GNUVA[ch], vow=s)

    # Kamatz before hataf-kamatz → 'o'
    if _KA in d and nxt and _HK in nxt.diac:
        return _out(cur, _LP.get(ch, ""), vow=["o"] + s)

    # Em kriah — silent alef mid-word (not before vav)
    if ch == "א" and not d and prev and nxt and nxt.char != "ו":
        return _out(cur, "")

    # Yud kriah — silent yud mid-word
    if (
        ch == "י"
        and not d
        and prev
        and nxt
        and prev.char + prev.diac != "אֵ"
        and not (nxt.char == "ו" and nxt.diac and _SH not in nxt.diac)
    ):
        return _out(cur, "")

    # Default: consonant + vowels
    return _out(cur, _LP.get(ch, ""))


def _shin(cur, prev, nxt):
    if _SI in cur.diac:
        if nxt and nxt.char == "ש" and not nxt.diac and _PAT_RE.search(cur.diac):
            return _out(cur, "sa", vow=_stress(cur), skip=1)
        return _out(cur, "s")
    if not cur.diac and prev and _SI in prev.diac:
        return _out(cur, "s")
    return _out(cur, _LP.get("ש", ""))


def _vav(cur, prev, nxt):
    d, s = cur.diac, _stress(cur)
    if prev and _SH in prev.diac and _HO in d:
        return _out(cur, "vo", vow=s)
    if nxt and nxt.char == "ו":
        dd = d + nxt.diac
        if _HO in dd:
            return _out(cur, "vo", vow=s, skip=1)
        if d == nxt.diac:
            return _out(cur, "vu", vow=s, skip=1)
        v = _vav_vowel(d)
        if v:
            return _out(cur, v, vow=s)
        if _SH in d and not nxt.diac:
            return _out(cur, "v", vow=s)
        return _out(cur, "", vow=s)
    v = _vav_vowel(d)
    if v:
        return _out(cur, v, vow=s)
    if _SH in d and not prev:
        return _out(cur, "ve", vow=s)
    if nxt and not d:
        return _out(cur, "", vow=s)
    return _out(cur, "v", vow=s)
