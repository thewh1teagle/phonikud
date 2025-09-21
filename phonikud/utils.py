from functools import lru_cache
from phonikud import lexicon
import unicodedata
import regex as re
import phonikud.syllables
import phonikud
from phonikud.variants import Letter


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


def remove_nikud(text: str, to_keep=""):
    pattern = lexicon.HE_NIKUD_PATTERN
    pattern = "".join(i for i in pattern if i not in to_keep)
    return re.sub(
        pattern,
        "",
        text,
    )


@lru_cache(maxsize=10000)
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


# @lru_cache(maxsize=10000) TODO?
def get_letters(word: str):
    letters: list[tuple[str, str]] = letters_pattern.findall(word)  # with en_geresh
    letters: list[Letter] = [Letter(i[0], i[1]) for i in letters]
    return letters


def get_unicode_names(text: str):
    return [unicodedata.name(c, "?") for c in text]


def has_vowel(s: iter):
    return any(i in s for i in "aeiou")


def has_consonant(s: iter):
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


def sort_stress(syllable: list[str]) -> list[str]:
    vowels = "aeiou"
    text = "".join(syllable)
    # No stress or no vowels
    if "ˈ" not in text or not re.search(f"[{vowels}]", text):
        return syllable

    # remove all stress
    syllable = [p.replace("ˈ", "") for p in syllable]

    # insert before first vowel in the first chunk that has one
    for i, p in enumerate(syllable):
        syllable[i], n = re.subn(f"([{vowels}])", r"ˈ\1", p, 1)
        if n:
            break
    return syllable


def mark_vocal_shva(word: str):
    """
    Vocal Shva is context-independent and can be predicted with just the word or a dictionary.
    See https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
    Note: we predict only if Shva in the first letter in the word
    Note: we assume that the word comes with | to mark 'Txiliyot'
    Note: Vocal Shva rules mid-word are unreliable, so we don’t code them.

    Meteg (\u05bd) will be added in the letter with Vocal Shva

    What we don't predict:
    (1) some shva in beginning in future form (we don't know)
    (2) shva in the middle of the word
    """
    letters = get_letters(word)
    if not letters:
        return word
    if letters[0].char in "למנרי":
        letters[0].all_diac += lexicon.VOCAL_SHVA_DIACRITIC
    elif len(letters) > 1 and letters[1].char in "אעה":
        letters[0].all_diac += lexicon.VOCAL_SHVA_DIACRITIC
    elif letters[0].char in "וכלב" and lexicon.PREFIX_DIACRITIC in letters[0].all_diac:
        # ^ The nakdan should add |
        letters[0].all_diac += lexicon.VOCAL_SHVA_DIACRITIC
    # Ensure that prefix character will be last
    for letter in letters:
        if "|" in letter.all_diac:
            letter.all_diac = letter.all_diac.replace("|", "") + "|"
    return "".join(str(i) for i in letters)


def sort_hatama(letters: list[Letter]) -> list[Letter]:
    for i in range(len(letters) - 1):
        diacs = list(letters[i].all_diac)
        if lexicon.HATAMA_DIACRITIC in diacs and lexicon.NIKUD_HASER_DIACRITIC in diacs:
            diacs.remove(lexicon.HATAMA_DIACRITIC)
            letters[i].all_diac = "".join(diacs)  # Reassign the updated diacritics
            letters[i + 1].all_diac += lexicon.HATAMA_DIACRITIC
    return letters


def add_milra_hatama(word: str):
    """
    Add stress to the first letter of the latest syllable
    """
    syllables = phonikud.syllables.get_syllables(word)
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
