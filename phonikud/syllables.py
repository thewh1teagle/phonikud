"""
https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

TODO: add to phonikud?
"""

import regex as re
import phonikud

VOWEL_DIACS = [chr(i) for i in range(0x05B1, 0x05BC)] + [chr(0x05C7)] + [chr(0x5BD)]

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
    if s == "וּ":
        return True
    return any(i in s for i in VOWEL_DIACS)


def get_syllables(word: str) -> list[str]:
    letters = phonikud.utils.get_letters(word)
    syllables, cur = [], ""
    vowel_state = False

    i = 0
    while i < len(letters):
        letter = letters[i]
        has_vowel = has_vowel_diacs(str(letter)) or (i == 0 and SHVA in letter.all_diac)
        # Look ahead
        vav1 = i + 2 < len(letters) and letters[i + 2].char == "ו"
        vav2 = i + 3 < len(letters) and letters[i + 3].char == "ו"

        if has_vowel:
            if vowel_state:
                syllables.append(cur)
                cur = str(letter)
            else:
                cur += str(letter)
            vowel_state = True
        else:
            cur += str(letter)

        i += 1

        # If two וs are coming: force current syllable to end, and join both וs as next syllable
        if vav1 and vav2:
            if cur:
                # Finish current syllable
                syllables.append(cur + str(letters[i]))
                cur = ""
            cur = str(letters[i + 1]) + str(letters[i + 2])
            i += 3  # skip past the double-vav
            vowel_state = True

        # If one ו is coming, end the syllable now
        elif vav1 and letters[i + 1].diac:
            if cur:
                syllables.append(cur)
                cur = ""
            vowel_state = False

    if cur:
        syllables.append(cur)
    # print(syllables)
    return syllables


def add_stress_to_syllable(s: str):
    letters = phonikud.utils.get_letters(s)
    letters[0].all_diac = STRESS + letters[0].all_diac
    return "".join(letter.char + letter.all_diac for letter in letters)


def add_stress(word: str, syllable_position: int):
    syllables: list[str] = get_syllables(word)

    if not syllables:
        return word  # no syllables, return original word

    # Normalize negative indices
    if syllable_position < 0:
        syllable_position += len(syllables)

    # Clamp to valid range
    syllable_position = max(0, min(syllable_position, len(syllables) - 1))

    stressed_syllable = syllables[syllable_position]
    stressed_syllable = add_stress_to_syllable(stressed_syllable)
    syllables[syllable_position] = stressed_syllable

    return "".join(syllables)
