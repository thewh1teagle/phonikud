"""
ASCII IPA transcription of Hebrew consonants and vowels.
"""

# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

SHVA_NA_DIACRITIC = "\u05bd"
HATAMA_DIACRITIC = "\u05ab"
PREFIX_DIACRITIC = "|"
STRESS = "\u02c8"  # visually looks like '

MILHEL_PATTERNS = ["יים", "וע", "טו", "דיה"]  # Used for stress prediction
HE_PATTERN = r'[\u05b0-\u05ea\u05ab\u05bd\'"]+'
HE_NIKUD_PATTERN = rf"[\u05B0-\u05C7|{HATAMA_DIACRITIC}{SHVA_NA_DIACRITIC}]"
PUNCTUATION = set(r".,!? ")

SPECIAL_PHONEMES = ["w"]
MODERN_SCHEMA = {
    "x": "χ",  # Het
    "r": "ʁ",  # Resh
    "g": "ɡ",  # Gimel
}

GERESH_PHONEMES = {"ג": "dʒ", "ז": "ʒ", "ת": "ta", "צ": "tʃ", "ץ": "tʃ"}

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
    # Shin Sin
    "שׁ": "ʃ",
    "שׂ": "s",
    "'": "",
}

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
    "\u05b3": "o",  # Hataf qamats
    "\u05b8": "a",  # Kamataz
    HATAMA_DIACRITIC: "ˈ",  # Stress (Hat'ama)
    SHVA_NA_DIACRITIC: "e",  # Shva na
}

DEDUPLICATE = {
    "\u05f3": "'",  # Hebrew geresh to regular geresh
    "־": "-",  # Hebrew Makaf to hypen
}

ADDITIONAL_PHONEMES = set()  # When using fallback

SET_PHONEMES = set(
    sorted(
        {
            *NIKUD_PHONEMES.values(),
            *LETTERS_PHONEMES.values(),
            *GERESH_PHONEMES.values(),
            *MODERN_SCHEMA.values(),
            *SPECIAL_PHONEMES,
        }
    )
)
