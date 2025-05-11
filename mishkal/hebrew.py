"""
Hebrew Phonemizer

Rules implemented:
1. Consonant handling (including special cases)
2. Nikud (vowel) processing
3. Dagesh handling
4. Geresh handling
5. Shva Na prediction
6. Special letter combinations

Reference:
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
- https://he.wikipedia.org/wiki/הברה
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://hebrew-academy.org.il/2010/03/24/צהרים-נעמי-הגיית-קמץ-לפני-חט
- https://hebrew-academy.org.il/2022/03/03/מלעיל-ומלרע-על-ההטעמה-בעברית
"""

from typing import Literal
from mishkal.variants import Letter
from mishkal import lexicon
import re
from mishkal.utils import sort_stress

SHVA = "\u05b0"
SIN = "\u05c2"
PATAH = "\u05b7"
KAMATZ = "\u05b8"
HATAF_KAMATZ = "\u05b3"
DAGESH = "\u05bc"
HOLAM = "\u05b9"
HIRIK = "\u05b4"
PATAH_LIKE_PATTERN = "[\u05b7-\u05b8]"
KUBUTS = "\u05bb"
TSERE = "\u05b5"
HATAMA = "\u05ab"
VAV_HOLAM = "\u05ba"
DAGESH = "\u05bc"
SEGOL = "\u05b6"


def phonemize_hebrew(
    letters: list[Letter],
    stress_placement: Literal["syllable", "vowel"],
) -> list[str]:
    phonemes = []
    i = 0

    while i < len(letters):
        cur = letters[i]
        prev = letters[i - 1] if i > 0 else None
        next = letters[i + 1] if i < len(letters) - 1 else None
        next_phonemes, skip_offset = letter_to_phonemes(
            cur, prev, next, stress_placement=stress_placement
        )
        # TODO: split into syllables
        # next_letters = next_phonemes, letters[i:i+skip_offset+1]
        phonemes.extend(next_phonemes)
        i += skip_offset + 1

    return phonemes


def letter_to_phonemes(
    cur: Letter,
    prev: Letter | None,
    next: Letter | None,
    stress_placement: Literal["syllable", "vowel"],
) -> tuple[str, int]:
    cur_phonemes = []
    skip_diacritics = False
    skip_consonants = False
    skip_offset = 0

    if lexicon.NIKUD_HASER_DIACRITIC in cur.all_diac:
        skip_consonants = True
        skip_diacritics = True

    elif cur.char == "א" and not cur.diac and prev:
        if next and next.char != "ו":
            skip_consonants = True

    elif (
        cur.char == "י"
        and next
        # Yud without diacritics
        and not cur.diac
        # In middle
        and prev
        # Prev Hirik
        and prev.char + prev.diac != "אֵ"
        # Next Vav has meaning
        and not (next.char == "ו" and next.diac and "\u05b0" not in next.diac)
    ):
        skip_consonants = True

    elif cur.char == "ש" and SIN in cur.diac:
        if (
            next
            and next.char == "ש"
            and not next.diac
            and re.search("[\u05b7\u05b8]", cur.diac)
        ):
            # ^ יששכר
            cur_phonemes.append("sa")
            skip_consonants = True
            skip_diacritics = True
            skip_offset += 1
        else:
            cur_phonemes.append("s")
            skip_consonants = True

    # shin without nikud after sin = sin
    elif cur.char == "ש" and not cur.diac and prev and SIN in prev.diac:
        cur_phonemes.append("s")
        skip_consonants = True

    elif not next and cur.char == "ח" and PATAH in cur.diac:
        # Final Het gnuva
        cur_phonemes.append("ax")
        skip_diacritics = True
        skip_consonants = True

    elif not next and cur.char == "ה" and PATAH in cur.diac:
        # Final He gnuva
        cur_phonemes.append("ah")
        skip_diacritics = True
        skip_consonants = True

    elif not next and cur.char == "ע" and PATAH in cur.diac:
        # Final Ayin gnuva
        cur_phonemes.append("a")
        skip_diacritics = True
        skip_consonants = True

    if cur and "'" in cur.diac and cur.char in lexicon.GERESH_PHONEMES:
        if cur.char == "ת":
            cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
            skip_diacritics = True
            skip_consonants = True
        else:
            # Geresh
            cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
            skip_consonants = True

    elif DAGESH in cur.diac and cur.char + DAGESH in lexicon.LETTERS_PHONEMES:  # dagesh
        cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char + DAGESH, ""))
        skip_consonants = True
    elif cur.char == "ו" and lexicon.NIKUD_HASER_DIACRITIC not in cur.all_diac:
        skip_consonants = True

        if prev and "\u05b0" in prev.diac and re.findall("[\u05b9-\u05ba]", cur.diac):
            # ^ לִגְוֹעַ
            cur_phonemes.append("vo")
            skip_diacritics = True
            skip_consonants = True

        elif next and next.char == "ו":
            # One of them has holam

            holams = re.findall("[\u05b9-\u05ba]", cur.diac + next.diac)
            if len(holams) == 2:
                cur_phonemes.append("wo")
                skip_diacritics = True
                skip_offset += 1
            if len(holams) == 1:
                cur_phonemes.append("vo")
                skip_diacritics = True
                skip_offset += 1
            # patah and next.diac empty
            elif cur.diac == next.diac:
                # double Vav
                cur_phonemes.append("vu")
                skip_diacritics = True
                skip_offset += 1
            elif HIRIK in cur.diac:
                cur_phonemes.append("vi")
                skip_diacritics = True
            elif SHVA in cur.diac and not next.diac:
                cur_phonemes.append("v")
                skip_diacritics = True
            elif KAMATZ in cur.diac or PATAH in cur.diac:
                cur_phonemes.append("va")
                skip_diacritics = True
            else:
                # TODO ?
                # skip_consonants = False
                skip_diacritics = False
        else:
            # Single vav

            # Vav with Patah
            if re.search(PATAH_LIKE_PATTERN, cur.diac):
                cur_phonemes.append("va")

            # Tsere
            elif TSERE in cur.diac:
                cur_phonemes.append("ve")
            elif SEGOL in cur.diac:
                cur_phonemes.append("ve")
            # Holam haser
            elif HOLAM in cur.diac:
                cur_phonemes.append("o")
            # Shuruk / Kubutz
            elif KUBUTS in cur.diac or DAGESH in cur.diac:
                cur_phonemes.append("u")
            # Vav with Shva in start
            elif SHVA in cur.diac and not prev:
                cur_phonemes.append("ve")
            # Hirik
            elif HIRIK in cur.diac:
                cur_phonemes.append("vi")
            elif next and not cur.diac:
                # It is fine for now since we use Dicta
                skip_consonants = True
                skip_diacritics = True
            else:
                cur_phonemes.append("v")

            skip_diacritics = True

    if not skip_consonants:
        cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char, ""))

    if KAMATZ in cur.diac and next and HATAF_KAMATZ in next.diac:
        cur_phonemes.append("o")
        skip_diacritics = True

    nikud_phonemes = []
    if not skip_diacritics:
        nikud_phonemes = [
            lexicon.NIKUD_PHONEMES.get(nikud, "") for nikud in cur.all_diac
        ]
    elif skip_diacritics and lexicon.HATAMA_DIACRITIC in cur.all_diac:
        nikud_phonemes = [lexicon.STRESS_PHONEME]
    cur_phonemes.extend(nikud_phonemes)
    # Ensure the stress is at the beginning of the syllable
    cur_phonemes = sort_stress(cur_phonemes, stress_placement)
    cur_phonemes = [
        p for p in cur_phonemes if all(i in lexicon.SET_PHONEMES for i in p)
    ]
    # Remove empty phonemes
    cur_phonemes = [p for p in cur_phonemes if p]
    return cur_phonemes, skip_offset
