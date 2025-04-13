"""
ASCII IPA transcription of Hebrew consonants and vowels.
"""

# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

MILHEL_PATTERNS = ['יים', 'וע', 'טו', "דיה"] # Used for stress prediction

HE_PATTERN = r'[\u05b0-\u05ea\u05ab\u05bd\'"]+'
HE_NIKUD_PATTERN = r"[\u05B0-\u05C7]"
PUNCTUATION = r".,!? "
STRESS = "\u02c8"  # visually looks like '

GERESH_PHONEMES = {"ג": "dʒ", "ז": "ʒ", "ת": "ta", "צ": "tʃ", "ץ": "tʃ"}
SPECIAL_PHONEMES = ['w']

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

SHVA_NA_DIACRITIC = "\u05bd"
ATAMAHA_DIACRITIC = "\u05ab"

NIKUD_PHONEMES = {
    "\u05b4": "i",  # Hiriq
    "\u05b1": "e",  # Hataf segol
    "\u05b5": "e",  # Tsere
    "\u05b6": "e",  # Segol
    "\u05b2": "a",  # Hataf Patah
    "\u05b7": "a",  # Patah
    "\u05c7": "o",  # Kamatz katan
    "\u05b9": "o",  # Holam
    "\u05ba": "o",  # Holam haser for vav
    "\u05bb": "u",  # Qubuts

    "\u05b3": 'o', # Hataf qamats
    "\u05b8": "a", # Kamataz
    
    ATAMAHA_DIACRITIC: "ˈ",  # Stress (Atmaha)
    SHVA_NA_DIACRITIC: "e",  # Shva na
}

# Deprecated
DEDUPLICATE = {
    # "\u05b1": "\u05b5",  # Hataf Segol -> Tsere
    # "\u05b2": "\u05b7",  # Hataf Patah -> Patah
    # "\u05b3": "\u05b9",  # Hataf Qamats -> Holam
    # "\u05b6": "\u05b5",  # Segol -> Tsere
    # Kamatz -> Patah
    # "\u05b8": "\u05b7",  # Qamats -> Patah
    # "\u05c7": "\u05b9",  # Qamats Qatan -> Holam
    "\u05f3": "'",  # Hebrew geresh to regular geresh
}

SET_PHONEMES = set(sorted({
    *NIKUD_PHONEMES.values(), 
    *LETTERS_PHONEMES.values(), 
    *GERESH_PHONEMES.values(),
    *SPECIAL_PHONEMES
}))
