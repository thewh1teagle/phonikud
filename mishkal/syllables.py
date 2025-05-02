"""
https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

TODO: add to mishkal?
"""

import regex as re
from mishkal.utils import get_letters

VOWEL_DIACS = [chr(i) for i in range(0x05B1, 0x05BC)]
VOWEL_DIACS_WITHOUT_HOLAM = [chr(d) for d in [0x05B9, 0x05BA]] + VOWEL_DIACS

STRESS = "\u05ab"
SHVA = "\u05b0"
DAGESH = "\u05bc"


def sort_diacritics(word: str):
    def sort_diacritics_callback(match):
        letter = match.group(1)
        diacritics = "".join(sorted(match.group(2)))  # Sort diacritics
        return letter + diacritics

    return re.sub(r"(\p{L})(\p{M}+)", sort_diacritics_callback, word)


def has_vowel_diacs(s: str):
    return any(i in s for i in VOWEL_DIACS)


def get_syllables(word: str) -> list[str]:
    letters = get_letters(word)
    syllables, cur = [], []
    found_vowel = False

    i = 0
    while i < len(letters):
        letter = letters[i]
        cur.append(letter)
        has_vowel = has_vowel_diacs(letter.diac) or (i == 0 and SHVA in letter.diac)

        if has_vowel:
            if found_vowel:
                syllables.append("".join(c.char + c.diac for c in cur[:-1]))
                cur = [cur[-1]]
            else:
                found_vowel = True

        # Two-ahead vav logic
        if (
            i + 2 < len(letters)
            and letters[i + 2].char == "ו"
            and not letters[i + 1].diac
        ):
            syllables.append("".join(c.char + c.diac for c in cur))
            cur, found_vowel = [], False

        # Next letter is plain vav
        elif (
            i + 1 < len(letters)
            and letters[i + 1].char == "ו"
            and not any(d in letters[i + 1].diac for d in VOWEL_DIACS_WITHOUT_HOLAM)
        ):
            cur.append(letters[i + 1])
            i += 1
            syllables.append("".join(c.char + c.diac for c in cur))
            cur, found_vowel = [], False

        i += 1

    if cur:
        syllables.append("".join(x.char + x.diac for x in cur))

    if not has_vowel_diacs(syllables[-1]) and not syllables[-1].endswith("ו"):
        syllables[-2] += syllables[-1]
        syllables.pop()

    return syllables


def add_stress_to_syllable(s: str):
    letters = get_letters(s)
    letters[0].diac = STRESS + letters[0].diac
    return "".join(letter.char + letter.diac for letter in letters)


def add_stress(word: str, syllable_position: int):
    syllables: list[str] = get_syllables(word)
    stressed_syllable = syllables[syllable_position]
    stressed_syllable = add_stress_to_syllable(stressed_syllable)
    syllables[syllable_position] = stressed_syllable
    return "".join(syllables)
