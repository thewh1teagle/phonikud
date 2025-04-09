"""
ASCII IPA transcription of Hebrew consonants and vowels.
"""

# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
HE_CHARS_PATTERN = (
    r"\b[\u05B0-\u05EA\u05F3\u0027]+\b"  # Chars including niqqud, geresh and en_geresh
)
HE_NIQQUD_PATTERN = r"[\u05B0-\u05C7]"
PUNCTUATION = r".,!? "

# Special
GIMEL_OR_ZAIN_WITH_DAGESH = "dʒ"
TSADIK_WITH_DAGESH = "tʃ"
SHIN_WITH_POINT = "ʃ"
SIN_WITH_POINT = "s"
STRESS = "\u02c8"  # visually looks like '
HET_GNUVA = "ax"
W_AS_WALLA = "w"

GERESH_LETTERS = {"ג": "dʒ", "ז": "ʒ", "ת": "ta", "צ": "tʃ", "ץ": "tʃ"}

LETTERS_NAMES_PHONEMES = {
    "א": "alef",  # Alef, glottal stop
    "ב": "bet",  # Bet
    "ג": "gimel",  # Gimel
    "ד": "dalet",  # Dalet
    "ה": "hej",  # He
    "ו": "vav",  # Vav
    "ז": "zajin",  # Zayin
    "ח": "xet",  # Het
    "ט": "tet",  # Tet
    "י": "jud",  # Yod
    "ך": "xaf sofit",  # Haf sofit
    "כ": "xaf",  # Haf
    "ל": "lamed",  # Lamed
    "ם": "mem sofit",  # Mem Sofit
    "מ": "mem",  # Mem
    "ן": "nun sofit",  # Nun Sofit
    "נ": "nun",  # Nun
    "ס": "samex",  # Samekh
    "ע": "ajin",  # Ayin, glottal stop
    "פ": "fey",  # Fey
    "ף": "fey sofit",  # Fey Sofit
    "ץ": "tsadik sofit",  # Tsadik sofit
    "צ": "tsadik",  # Tsadik
    "ק": "kuf",  # Kuf
    "ר": "rejiʃ",  # Resh
    "ש": "ʃin",  # Shin
    "ת": "taf",  # Taf
}

# Consonants
LETTERS_PHONEMES = {
    "א": "ʔ",  # Alef
    "ב": "v",  # Bet
    "ג": "g",  # Gimel
    "ד": "d",  # Dalet
    "ה": "h",  # He
    "ו": "v",  # Vav
    "ז": "z",  # Zayin
    "ח": "x",  # Het
    "ט": "t",  # Tet
    "י": "j",  # Yod
    "ך": "x",  # Haf sofit
    "כ": "x",  # Haf
    "ל": "l",  # Lamed
    "ם": "m",  # Mem Sofit
    "מ": "m",  # Mem
    "ן": "n",  # Nun Sofit
    "נ": "n",  # Nun
    "ס": "s",  # Samekh
    "ע": "ʔ",  # Ayin, only voweled
    "פ": "f",  # Fey
    "ף": "f",  # Fey Sofit
    "ץ": "ts",  # Tsadik sofit
    "צ": "ts",  # Tsadik
    "ק": "k",  # Kuf
    "ר": "r",  # Resh
    "ש": "ʃ",  # Shin
    "ת": "t",  # Taf
    # Beged Kefet
    "בּ": "b",
    "כּ": "k",
    "פּ": "p",
    "שׁ": "ʃ",
    "שׂ": "s",
    "'": "",
}

# Vowels
VOWEL_A = "a"
VOWEL_E = "e"
VOWEL_I = "i"
VOWEL_O = "o"
VOWEL_U = "u"

SHVA_NA_DIACRITIC = "\u05bd"
ATAMAHA_DIACRITIC = "\u05ab"

NIQQUD_PHONEMES = {
    "\u05b4": "i",  # Hiriq
    "\u05b5": "e",  # Tsere
    "\u05b7": "a",  # Patah
    "\u05b9": "o",  # Holam
    "\u05ba": "o",  # Holam haser for vav
    "\u05bb": "u",  # Qubuts

    "\u05b3": 'o', # Hataf qamats
    "\u05b8": "a", # Kamataz
    
    ATAMAHA_DIACRITIC: "ˈ",  # Stress (Atmaha)
    SHVA_NA_DIACRITIC: "e",  # Shva na
}

SET_LETTER_SYMBOLS = {
    "\u05b0",  # Shva
    "\u05b4",  # Hiriq
    "\u05b5",  # Tsere
    "\u05b7",  # Patah
    "\u05b9",  # Holam
    "\u05ba",  # Holam haser for vav
    "\u05bb",  # Qubuts
    "\u05bc",  # Dagesh
    "\u05c1",  # Shin dot
    "\u05b3", # Hataf qamats
    "\u05b8", # Kamataz
    "\u05c2",  # Sin dot
    "'",  # Geresh
}

"""
We're left with the following niqqud (10):  
Shva, Hiriq, Tsere, Patah, Holam, Qubuts, Dagesh, 
Holam haser for vav, Shin dot, Sin dot
"""
NIQQUD_DEDUPLICATE = {
    "\u05b1": "\u05b5",  # Hataf Segol -> Tsere
    "\u05b2": "\u05b7",  # Hataf Patah -> Patah
    # "\u05b3": "\u05b9",  # Hataf Qamats -> Holam
    "\u05b6": "\u05b5",  # Segol -> Tsere
    # Kamatz -> Patah
    # "\u05b8": "\u05b7",  # Qamats -> Patah
    "\u05c7": "\u05b9",  # Qamats Qatan -> Holam
    "\u05f3": "'",  # Hebrew geresh to regular geresh
}


SET_OUTPUT_CHARACTERS = set(
    [
        *GIMEL_OR_ZAIN_WITH_DAGESH,
        TSADIK_WITH_DAGESH,
        SHIN_WITH_POINT,
        SIN_WITH_POINT,
        W_AS_WALLA,
    ]
    + [STRESS]
    + list(LETTERS_PHONEMES.values())
    + list(NIQQUD_PHONEMES.values())
    + [VOWEL_A, VOWEL_E, VOWEL_I, VOWEL_O, VOWEL_U]
    + list(PUNCTUATION)
)

SET_NIQQUD = {
    # Shva, Hiriq, Tsere, Patah, Holam, Holam haser for vav, Qubuts, Dagesh, Shin dot, Sin dot
    "\u05b0", # Shva
    "\u05b4", # Hiriq
    "\u05b5", # Tsere
    "\u05b7", # Patah
    "\u05b9", # Holam
    "\u05ba", # Holam for vav
    "\u05bb", # Qubuts
    "\u05bc", # Dagesh
    "\u05c1", # Shin
    "\u05c2", # Sin
    "\u05b3", # Hataf qamats
    "\u05b8", # Kamataz
    # shva na and atmaha
    "\u05bd",  # shva na
    "\u05ab",  # atmaha
}
SET_LETTERS = set(LETTERS_PHONEMES.keys())
SET_PUNCTUATION = set(PUNCTUATION)


# Set for fast lookup
SET_INPUT_CHARACTERS = set(
    list(LETTERS_PHONEMES.keys()) + list(SET_NIQQUD) + list(PUNCTUATION) + ["'"]
)
