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

from phonikud import lexicon
import re
from phonikud.utils import sort_stress
from phonikud.variants import Letter
from phonikud.lexicon import NIKUD, NIKUD_PATAH_LIKE_PATTERN

FINAL_PATACH_MAP = {
    "ח": "ax",  # Het gnuva
    "ה": "ah",  # He gnuva
    "ע": "a",  # Ayin gnuva
}


def handle_shin(cur, prev, next):
    if NIKUD["SIN"] in cur.diac:
        if (
            next
            and next.char == "ש"
            and not next.diac
            and re.search(NIKUD_PATAH_LIKE_PATTERN, cur.diac)
        ):
            return make_result("sa", offset=1)  # special case יששכר
        return make_result("s", skip_diacritics=False)
    if not cur.diac and prev and NIKUD["SIN"] in prev.diac:
        return make_result("s", skip_diacritics=False)
    return make_result("", skip_diacritics=False, skip_consonants=False)


def clean_phonemes(phonemes):
    return [p for p in phonemes if p and all(ch in lexicon.SET_PHONEMES for ch in p)]


def handle_geresh(cur):
    phoneme = lexicon.GERESH_PHONEMES.get(cur.char, "")
    if cur.char == "ת":
        return make_result(phoneme)
    return make_result(phoneme, skip_diacritics=False)


def get_nikud_phonemes(cur, skip_diacritics):
    if not skip_diacritics:
        return [lexicon.NIKUD_PHONEMES.get(n, "") for n in cur.all_diac]
    if lexicon.HATAMA_DIACRITIC in cur.all_diac:
        return [lexicon.STRESS_PHONEME]
    return []


def phonemize_word(letters: list[Letter]) -> list[str]:
    phonemes = []
    i = 0
    while i < len(letters):
        prev = letters[i - 1] if i > 0 else None
        next = letters[i + 1] if i + 1 < len(letters) else None
        next_phonemes, skip_offset = letter_to_phonemes(letters[i], prev, next)
        phonemes.extend(next_phonemes)
        i += skip_offset + 1
    return phonemes


def should_skip_yud(cur: Letter, prev: Letter | None, next: Letter | None) -> bool:
    """Returns True if Yud should skip consonants"""
    return (
        next
        # Yud without diacritics
        and not cur.diac
        # In middle
        and prev
        # Prev Hirik
        and prev.char + prev.diac != "אֵ"
        # Next Vav has meaning
        and not (next.char == "ו" and next.diac and NIKUD["SHVA"] not in next.diac)
    )


def make_result(
    phoneme: str,
    offset: int = 0,
    skip_consonants: bool = True,
    skip_diacritics: bool = True,
):
    return [phoneme], skip_consonants, skip_diacritics, offset


def handle_vav(cur: Letter, prev: Letter | None, next: Letter | None):
    """
    Return phonemes, skip_consonants, skip_diacritics, skip_offset
    """
    if prev and NIKUD["SHVA"] in prev.diac and NIKUD["HOLAM"] in cur.diac:
        return make_result("vo")

    if next and next.char == "ו":
        diac = cur.diac + next.diac
        if NIKUD["HOLAM"] in diac:
            return make_result("vo", offset=1)
        if cur.diac == next.diac:
            return make_result("vu", offset=1)
        if NIKUD["HIRIK"] in cur.diac:
            return make_result("vi")
        if NIKUD["SHVA"] in cur.diac and not next.diac:
            return make_result("v")
        if NIKUD["KAMATZ"] in cur.diac or NIKUD["PATAH"] in cur.diac:
            return make_result("va")
        if NIKUD["TSERE"] in cur.diac or NIKUD["SEGOL"] in cur.diac:
            return make_result("ve")
        return make_result("", skip_consonants=True, skip_diacritics=True)

    # Single ו
    if re.search(NIKUD_PATAH_LIKE_PATTERN, cur.diac):
        return make_result("va")
    if NIKUD["TSERE"] in cur.diac or NIKUD["SEGOL"] in cur.diac:
        return make_result("ve")
    if NIKUD["HOLAM"] in cur.diac:
        return make_result("o")
    if NIKUD["KUBUTS"] in cur.diac or NIKUD["DAGESH"] in cur.diac:
        return make_result("u")
    if NIKUD["SHVA"] in cur.diac and not prev:
        return make_result("ve")
    if NIKUD["HIRIK"] in cur.diac:
        return make_result("vi")
    if next and not cur.diac:
        return [], True, True, 0

    return make_result("v")


def letter_to_phonemes(
    cur: Letter,
    prev: Letter | None,
    next: Letter | None,
) -> tuple[str, int]:
    cur_phonemes = []
    skip_diacritics = False
    skip_consonants = False
    skip_offset = 0

    # Nikud haser
    if lexicon.NIKUD_HASER_DIACRITIC in cur.all_diac:
        return [], 0

    # Em Kriah
    elif cur.char == "א" and not cur.diac and prev:
        if next and next.char != "ו":
            skip_consonants = True

    # Yud Kriah
    elif cur.char == "י" and should_skip_yud(cur, prev, next):
        skip_consonants = True

    # Shin Sin
    elif cur.char == "ש":
        sh_phonemes, skip_consonants, skip_diacritics, extra_skip = handle_shin(
            cur, prev, next
        )
        cur_phonemes.extend(sh_phonemes)
        skip_offset += extra_skip

    # Patah Gnuva
    elif not next and NIKUD["PATAH"] in cur.diac and cur.char in FINAL_PATACH_MAP:
        f_phonemes, skip_consonants, skip_diacritics, extra_skip = make_result(
            FINAL_PATACH_MAP[cur.char]
        )
        cur_phonemes.extend(f_phonemes)
        skip_offset += extra_skip

    # Geresh
    if cur and "'" in cur.diac and cur.char in lexicon.GERESH_PHONEMES:
        g_phonemes, skip_consonants, skip_diacritics, extra_skip = handle_geresh(cur)
        cur_phonemes.extend(g_phonemes)
        skip_offset += extra_skip

    # Dagesh (Beged Kefet & Vav)
    elif (
        NIKUD["DAGESH"] in cur.diac
        and cur.char + NIKUD["DAGESH"] in lexicon.LETTERS_PHONEMES
    ):
        cur_phonemes.append(
            lexicon.LETTERS_PHONEMES.get(cur.char + NIKUD["DAGESH"], "")
        )
        skip_consonants = True
    elif cur.char == "ו" and lexicon.NIKUD_HASER_DIACRITIC not in cur.all_diac:
        vav_phonemes, vav_skip_consonants, vav_skip_diacritics, vav_skip_offset = (
            handle_vav(cur, prev, next)
        )
        cur_phonemes.extend(vav_phonemes)
        skip_consonants = vav_skip_consonants
        skip_diacritics = vav_skip_diacritics
        skip_offset += vav_skip_offset

    # Consonant
    if not skip_consonants:
        cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char, ""))

    if NIKUD["KAMATZ"] in cur.diac and next and NIKUD["HATAF_KAMATZ"] in next.diac:
        cur_phonemes.append("o")
        skip_diacritics = True

    cur_phonemes.extend(get_nikud_phonemes(cur, skip_diacritics))
    # Ensure stress placed before the syllable's vowel
    cur_phonemes = sort_stress(cur_phonemes)
    # Clean unknown characters
    cur_phonemes = clean_phonemes(cur_phonemes)
    return cur_phonemes, skip_offset
