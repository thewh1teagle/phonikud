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
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://hebrew-academy.org.il/2010/03/24/צהרים-נעמי-הגיית-קמץ-לפני-חט/
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
- https://he.wikipedia.org/wiki/הברה
"""

from mishkal.variants import Letter
from mishkal import lexicon
import re
from mishkal.utils import sort_stress

SHVA = "\u05b0"
SIN = "\u05c2"
PATAH = '\u05b7'
KAMATZ = '\u05b8'
HATAF_KAMATZ = '\u05b3'
DAGESH = "\u05bc"
HOLAM = "\u05b9"
HIRIK = "\u05b4"
PATAH_LIKE_PATTERN = "[\u05b7-\u05b8]"
KUBUTS = "\u05bb"
TSERE = "\u05b5"

def phonemize_hebrew(letters: list[Letter], predict_shva_na: bool) -> list[str]:
    phonemes = []
    i = 0

    while i < len(letters):
        cur = letters[i]
        prev = letters[i - 1] if i > 0 else None
        next = letters[i + 1] if i < len(letters) - 1 else None

        next_phonemes, skip_offset = letter_to_phonemes(cur, prev, next, predict_shva_na)
        phonemes.extend(next_phonemes)
        i += skip_offset + 1

    return phonemes


def letter_to_phonemes(cur: Letter, prev: Letter | None, next: Letter | None, predict_shva_na: bool):
    cur_phonemes = []
    skip_diacritics = False
    skip_constants = False
    skip_offset = 0
    # revised rules

    # יַאלְלָה
    if cur.char == "ל" and cur.diac == SHVA and next and next.char == "ל":
        skip_diacritics = True
        skip_constants = True

    if (
        cur.char == "ו"
        and not prev
        and next
        and not next.diac
        and cur.char + cur.diac == "וַא"
    ):
        skip_offset += 1
        cur_phonemes.append("wa")

    if cur.char == "א" and not cur.diac and prev:
        if next and next.char != 'ו':
            skip_constants = True

    # TODO ?
    if cur.char == "י" and next and not cur.diac and prev and prev.char + prev.diac != 'אֵ':
        skip_constants = True

    if cur.char == "ש" and SIN in cur.diac:
        cur_phonemes.append("s")
        skip_constants = True

    # shin without nikud after sin = sin
    if cur.char == "ש" and not cur.diac and prev and SIN in prev.diac:
        cur_phonemes.append("s")
        skip_constants = True

    if not next and cur.char == "ח" and PATAH in cur.diac:
        # Final Het gnuva
        cur_phonemes.append("ax")
        skip_diacritics = True
        skip_constants = True

    if cur and "'" in cur.diac and cur.char in lexicon.GERESH_PHONEMES:
        if cur.char == "ת":
            cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
            skip_diacritics = True
            skip_constants = True
        else:
            # Geresh
            cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
            skip_constants = True

    elif (
        DAGESH in cur.diac and cur.char + DAGESH in lexicon.LETTERS_PHONEMES
    ):  # dagesh
        cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char + DAGESH, ""))
        skip_constants = True
    elif cur.char == "ו":
        skip_constants = True
        if next and next.char == "ו" and next.diac == cur.diac:
            # patah and next.diac empty
            if re.search(PATAH_LIKE_PATTERN, cur.diac) and not next.diac:
                cur_phonemes.append("w")
                skip_diacritics = True
                skip_offset += 1
            elif cur.diac == next.diac:
                # double vav
                cur_phonemes.append("wo")
                skip_diacritics = True
                skip_offset += 1
            else:
                # TODO ?
                # skip_consonants = False
                skip_diacritics = False
        else:
            # Single vav

            # Vav with Patah
            if re.search(PATAH_LIKE_PATTERN, cur.diac):
                cur_phonemes.append("va")

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
            # Tsere
            elif TSERE in cur.diac:
                cur_phonemes.append("ve")
            
            else:
                cur_phonemes.append("v")
            skip_diacritics = True

    if not skip_constants:
        cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char, ""))
    
    if lexicon.SHVA_NA_DIACRITIC not in cur.diac and predict_shva_na and SHVA in cur.diac and not skip_diacritics:
        # Shva Na prediction
        if not prev:
            # Lamanrey
            if cur.char in 'למנרי':
                cur_phonemes.append("e")
                skip_diacritics = True 
            # Itsurim groniyim in next one
            elif next.char in 'אהע':
                cur_phonemes.append("e")
                skip_diacritics = True 
            # Otiot ashimush
            elif cur.char in 'ול':
                # TODO: Kaf and Bet?
                cur_phonemes.append("e")
                skip_diacritics = True 
            # TODO: txiliyot "yatan"?

        else:
            if next and next.char == cur.char:
                cur_phonemes.append("e")
                skip_diacritics = True
            elif prev and SHVA in prev.diac and cur_phonemes[-1] != 'e':
                cur_phonemes.append("e")
                skip_diacritics = True

    if KAMATZ in cur.diac and next and HATAF_KAMATZ in next.diac:
        cur_phonemes.append('o')
        skip_diacritics = True


    
    nikud_phonemes = (
        [lexicon.NIKUD_PHONEMES.get(nikud, "") for nikud in cur.diac]
        if not skip_diacritics
        else []
    )            
    cur_phonemes.extend(nikud_phonemes)
    # Ensure the stress is at the beginning of the syllable
    cur_phonemes = sort_stress(cur_phonemes)
    cur_phonemes = [p for p in cur_phonemes if all(i in lexicon.SET_PHONEMES for i in p)]
    return cur_phonemes, skip_offset