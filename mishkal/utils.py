from typing import Literal
from mishkal import lexicon
import unicodedata
import regex as re
import mishkal.syllables
from mishkal.variants import Letter
import mishkal


def sort_diacritics(match):
    letter = match.group(1)
    diacritics = "".join(sorted(match.group(2)))  # Sort diacritics
    return letter + diacritics


NORMALIZE_PATTERNS = {
    # Sort diacritics
    r"(\p{L})(\p{M}+)": sort_diacritics,
    "״": '"',  # Hebrew geresh to normal geresh
    "׳": "'",  # Same
}


def remove_nikud(text: str):
    return re.sub(
        lexicon.HE_NIKUD_PATTERN,
        "",
        text,
    )


def normalize(text: str) -> str:
    """
    Normalize unicode (decomposite)
    Keep only Hebrew characters / punctuation / IPA
    Sort diacritics
    """

    # Decompose text
    text = unicodedata.normalize("NFD", text)
    for k, v in NORMALIZE_PATTERNS.items():
        text = re.sub(k, v, text)
    for k, v in lexicon.DEDUPLICATE.items():
        text = re.sub(k, v, text)
    return text


def post_normalize(phonemes: str):
    new_phonemes = []
    for word in phonemes.split(" "):
        # remove glottal stop from end
        word = re.sub(r"ʔ$", "", word)
        # remove h from end
        word = re.sub(r"h$", "", word)
        word = re.sub(r"ˈh$", "", word)
        # remove j followed by a i
        word = re.sub(r"ij$", "i", word)
        new_phonemes.append(word)
    phonemes = " ".join(new_phonemes)
    return phonemes


def post_clean(phonemes: str):
    clean = []
    for i in phonemes:
        if i == "-":
            clean.append(" ")
        elif (
            i in lexicon.SET_PHONEMES
            or i in lexicon.ADDITIONAL_PHONEMES
            or i == " "
            or i in lexicon.PUNCTUATION
        ):
            clean.append(i)
    return "".join(clean)


letters_pattern = re.compile(r"(\p{L})([\p{M}'|]*)")


def get_letters(word: str):
    letters: list[tuple[str, str]] = letters_pattern.findall(word)  # with en_geresh
    letters: list[Letter] = [Letter(i[0], i[1]) for i in letters]
    return letters


def get_unicode_names(text: str):
    return [unicodedata.name(c, "?") for c in text]


def has_vowel(s: iter):
    return any(i in s for i in "aeiou")


def has_constant(s: iter):
    return any(i not in "aeiou" for i in s)


def get_phoneme_syllables(phonemes: list[str]) -> list[str]:
    syllables = []
    cur_syllable = ""

    i = 0
    while i < len(phonemes):
        # Add current phoneme to the syllable

        cur_syllable += phonemes[i]

        # If we have a vowel in the current syllable
        if has_vowel(cur_syllable):
            # If there's a next phoneme that's a consonant followed by a vowel-containing phoneme
            if (
                i + 2 < len(phonemes)
                and not has_vowel(phonemes[i + 1])
                and has_vowel(phonemes[i + 2])
            ):
                # End the current syllable and start a new one
                syllables.append(cur_syllable)
                cur_syllable = ""
            # If we're at the end or next phoneme has a vowel
            elif i + 1 >= len(phonemes) or has_vowel(phonemes[i + 1]):
                # End the current syllable
                syllables.append(cur_syllable)
                cur_syllable = ""

        i += 1

    # Add any remaining syllable
    if cur_syllable:
        syllables.append(cur_syllable)

    # Iterate over syllables and move any syllable ending with lexicon.STRESS to the next one
    for i in range(len(syllables) - 1):  # Ensure we're not at the last syllable
        if syllables[i].endswith(lexicon.STRESS_PHONEME):
            syllables[i + 1] = (
                lexicon.STRESS_PHONEME + syllables[i + 1]
            )  # Move stress to next syllable
            syllables[i] = syllables[i][
                : -len(lexicon.STRESS_PHONEME)
            ]  # Remove stress from current syllable

    return syllables


def sort_stress(
    phonemes: list[str], placement: Literal["syllable", "vowel"] = "vowel"
) -> list[str]:
    """
    TTS systems expect that the stress will be BEFORE vowel
    Linguistics expect in the START of the syllable
    at_start=True for place it in the beginning
    """
    if "ˈ" not in "".join(phonemes):
        # ^ Does not contains stress
        return phonemes
    if not any(i in "".join(phonemes) for i in "aeiou"):
        # ^ Does not contains vowel
        return phonemes

    # Remove stress marker
    phonemes = [p for p in phonemes if p != "ˈ"]

    if placement == "syllable":
        return ["ˈ"] + phonemes

    # Define vowels
    vowels = "aeiou"

    # Find the first phoneme that contains a vowel, and inject the stress before the vowel

    for i, phoneme in enumerate(phonemes):
        for j, char in enumerate(phoneme):
            if char in vowels:
                # Insert stress before the vowel
                phonemes[i] = phoneme[:j] + "ˈ" + phoneme[j:]
                return phonemes

    # If no vowels found, return unchanged
    return phonemes


def mark_shva_na(word: str):
    """
    Shva Na is context-independent and can be predicted with just the word or a dictionary.
    See https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
    Note: we predict only if Shva in the first letter in the word
    Note: we assume that the word comes with | to mark 'Txiliyot'
    Note: Shva Na rules mid-word are unreliable, so we don’t code them.

    Meteg (\u05bd) will be added in the letter with Shva Na

    What we don't predict:
    (1) some shva in beginning in future form (we don't know)
    (2) shva in the middle of the word
    """
    letters = get_letters(word)
    if not letters:
        return word
    if letters[0].char in "למנרי":
        letters[0].all_diac += lexicon.SHVA_NA_DIACRITIC
    elif len(letters) > 1 and letters[1].char in "אעה":
        letters[0].all_diac += lexicon.SHVA_NA_DIACRITIC
    elif letters[0].char in "וכלב" and lexicon.PREFIX_DIACRITIC in letters[0].all_diac:
        # ^ The nakdan should add |
        letters[0].all_diac += lexicon.SHVA_NA_DIACRITIC
    # Ensure that prefix character will be last
    for letter in letters:
        if "|" in letter.all_diac:
            letter.all_diac = letter.all_diac.replace("|", "") + "|"
    return "".join(str(i) for i in letters)


def add_milra_hatama(word: str):
    syllables = mishkal.syllables.get_syllables(word)
    stress_index = -1

    if not syllables:
        return word

    if len(syllables) == 1:
        stress_index = 0

    # Get latest syllable
    milra = syllables[stress_index]
    # Get letters
    letters = get_letters(milra)
    # Add Hatama
    letters[0].all_diac += lexicon.HATAMA_DIACRITIC

    # Replace latest syllable
    syllables[stress_index] = "".join(str(i) for i in letters)
    return "".join(syllables)
