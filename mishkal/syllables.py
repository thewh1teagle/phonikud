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
    syllables = []
    letters = get_letters(word)
    i = 0
    cur = ""
    found_vowel = False

    while i < len(letters):
        letter = letters[i]

        cur += letter.char + letter.diac

        # Check if the letter has a vowel diacritic or shvain first letter (prediction)
        if has_vowel_diacs(letter.diac) or (SHVA in letters[i].diac and i == 0):
            if found_vowel:
                # Found a second vowel diacritic, break the syllable here
                syllables.append(
                    cur[: -len(letter.char + letter.diac)]
                )  # Remove the last added letter
                cur = (
                    letter.char + letter.diac
                )  # Start new syllable with the current letter
            else:
                found_vowel = True

        # With diacritics -> Vav -> Mark end
        if (
            i + 2 < len(letters)
            and letters[i + 2].char == "ו"
            and not letters[i + 1].diac
        ):
            syllables.append(cur)
            cur = ""
            found_vowel = False

        # Next is Vav -> Mark end

        elif (
            i + 1 < len(letters)
            and letters[i + 1].char == "ו"
            and not any(d in letters[i + 1].diac for d in VOWEL_DIACS_WITHOUT_HOLAM)
        ):
            cur += letters[i + 1].char + letters[i + 1].diac
            i += 1
            syllables.append(cur)
            cur = ""
            found_vowel = False  # Reset vowel flag

        i += 1

    if cur:  # Append the last syllable
        syllables.append(cur)

    if not has_vowel_diacs(syllables[-1]) and not syllables[-1].endswith("ו"):
        syllables[-2] += syllables[-1]
        syllables = syllables[:-1]

    return syllables
    # return ['סֵ', 'דֶר']


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
