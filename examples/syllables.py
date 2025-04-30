"""
https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

TODO: add to mishkal?
"""

import regex as re

from mishkal.utils import get_letters

data = [
    
    # "בָּט֫וּחַ",
    # "בְּמֶ֫שֶׁךְ",
    # "כְּאִ֫יֽלּוּ",
    # "בְּסֵ֫דֶר",
    
    # "לְמַ֫עַן",
    # "הָיִ֫ינוּ",
    # "עָלֵ֫ינוּ",
    # "ַקּוֹאָלִ֫יצְיָה",
    # "עָלֶ֫יהָ",
    # "קוֹבֵ֫עַ",
    # "ָאוֹפּוֹזִ֫יצְיָה",
    # "מִמֶּ֫נּוּ",
    # "וִיֽכּ֫וּחַ",
    # "שָׂמֵ֫חַ",
    # "ַתִּקְשֹׁ֫וֽרֶת",
    
    # "מֵאִתָּ֫נוּ",
    
    "שׁוֹמֵ֫עַ",
    "לִמְנֹ֫וֽעַ",
    "ּבַּ֫יִת",
    "מְבַקֶּ֫שֶׁת",
    "לְהַצְבִּ֫יעַ",
    "שָׁמַ֫עְתִּי",
    "ּדֶ֫רֶךְ",
    "מַעֲרֶ֫כֶת",
    "לִשְׁמֹ֫וֽעַ",
    "יַ֫חַד",
    "לָדַ֫עַת",
    "צֹ֫וֽרֶךְ",
    "חוֹשֶׁ֫בֶת",
    "קּוֹדֶ֫מֶת",
    "לָשֶׁ֫בֶת",
    "אֵינֶ֫נָּה",
    "רֶ֫גַע",
    "לָלֶ֫כֶת",
    "מֵעֵ֫בֶר",
    "הָיִ֫יתָ",
    "מִפְלֶ֫גֶת",
    "כֶּ֫סֶף",
    "הִגִּ֫יעַ",
    "דַּ֫עַת",
    "לִפְגֹּ֫וֽעַ",
    "מִסְגֶּ֫רֶת",
    "לִקְבֹּ֫וֽעַ",
    "מַגִּ֫יעַ",
    "כּ֫וֹחַ",
    "דַּ֫עַת",
    "אֵלֶ֫יךָ",
    "מְסֻוֽיֶּ֫מֶת",
    "קֶ֫שֶׁר",
    "בִּיֽקֹּ֫וֽרֶת",
    "רָאִ֫יתִי",
    "אָמַ֫רְתָּ",
    "לָקַ֫חַת",
    "סֵ֫דֶר",
]



def sort_diacritics(word: str):
    def sort_diacritics_callback(match):
        letter = match.group(1)
        diacritics = "".join(sorted(match.group(2)))  # Sort diacritics
        return letter + diacritics
    return re.sub(r"(\p{L})(\p{M}+)", sort_diacritics_callback, word)

vowel_diacs = [chr(i) for i in range(0x05b1, 0x05bc)]

def has_vowel_diacs(s: str):
    return any(i in s for i in vowel_diacs)

def get_syllables(word: str) -> list[str]:
    syllables = []
    letters = get_letters(word)
    i = 0
    cur = ''
    found_vowel = False

    while i < len(letters):
        letter = letters[i]
        cur += letter.char + letter.diac
        i += 1

        # Check if the letter has a vowel diacritic
        if has_vowel_diacs(letter.diac):
            if found_vowel:
                # Found a second vowel diacritic, break the syllable here
                syllables.append(cur[:-len(letter.char + letter.diac)])  # Remove the last added letter
                cur = letter.char + letter.diac  # Start new syllable with the current letter
            else:
                found_vowel = True

        # Check if we encounter ו without diacritics and close the current syllable
        if i + 1 < len(letters) and letters[i].char == 'ו' and not letters[i].diac:
            syllables.append(cur)
            cur = ''
            found_vowel = False  # Reset vowel flag

    if cur:  # Append the last syllable
        syllables.append(cur)

    return syllables
    # return ['סֵ', 'דֶר']

def add_stress_to_syllable(s: str):
    letters = get_letters(s)
    letters[0].diac = '\u05ab' + letters[0].diac
    return ''.join(letter.char + letter.diac for letter in letters)

def add_stress(word: str, syllable_position: int):
    syllables: list[str] = get_syllables(word)
    print(syllables)
    stressed_syllable = syllables[syllable_position]
    stressed_syllable = add_stress_to_syllable(stressed_syllable)
    syllables[syllable_position] = stressed_syllable
    return ''.join(syllables)

for src_with_stress in data:
    src_with_stress = src_with_stress.replace('\u05bc', '')
    without_stress = src_with_stress.replace('\u05ab', '')
    
    with_stress = add_stress(without_stress, -2)

    # Sort diacritics
    with_stress = sort_diacritics(with_stress)
    src_with_stress = sort_diacritics(src_with_stress)
    print(with_stress, src_with_stress)
    assert with_stress == src_with_stress