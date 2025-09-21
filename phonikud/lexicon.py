"""
ASCII IPA transcription of Hebrew consonants and vowels.
"""

# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table

# Non standard diacritics
VOCAL_SHVA_DIACRITIC = "\u05bd"  # Meteg
HATAMA_DIACRITIC = "\u05ab"  # Ole
PREFIX_DIACRITIC = "|"  # Vertical bar
NIKUD_HASER_DIACRITIC = "\u05af"  # Masora, not in use
EN_GERESH = "'"
NON_STANDARD_DIAC = "".join(
    [
        VOCAL_SHVA_DIACRITIC,
        HATAMA_DIACRITIC,
        PREFIX_DIACRITIC,
        NIKUD_HASER_DIACRITIC,
        EN_GERESH,
    ]
)

HE_PATTERN = rf'[\u05b0-\u05ea{NON_STANDARD_DIAC}"]+'
# ^ Standard nikud and letters, ole, meteg, masora, vertical bar, en geresh
HE_NIKUD_PATTERN = rf"[\u05b0-\u05c7{NON_STANDARD_DIAC}]"
# ^ Letters, diacritics, en geresh
PUNCTUATION = set(r".,!? ")

STRESS_PHONEME = "ˈ"  # \u02c8 visually looks like single quote
SPECIAL_PHONEMES = ["w"]
MODERN_SCHEMA = {
    "x": "χ",  # Het
    "r": "ʁ",  # Resh
    "g": "ɡ",  # Gimel
}

# Geresh
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
    HATAMA_DIACRITIC: STRESS_PHONEME,  # Stress (Hat'ama)
    VOCAL_SHVA_DIACRITIC: "e",  # Vocal Shva
}

DEDUPLICATE = {
    "\u05f3": "'",  # Hebrew geresh to regular geresh
    "־": "-",  # Hebrew Makaf to hypen
}

# Sets
SET_ENHANCED_DIACRITICS = set(
    [HATAMA_DIACRITIC, PREFIX_DIACRITIC, VOCAL_SHVA_DIACRITIC]
)

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

NIKUD = {
    "PATAH": "\u05b7",
    "KAMATZ": "\u05b8",
    "HIRIK": "\u05b4",
    "SEGOL": "\u05b6",
    "TSERE": "\u05b5",
    "HOLAM": "\u05b9",
    "KUBUTS": "\u05bb",
    "SHVA": "\u05b0",
    "HATAF_KAMATZ": "\u05b3",
    "DAGESH": "\u05bc",
    "SIN": "\u05c2",
    "HATAMA": "\u05ab",
    "VAV_HOLAM": "\u05ba",
}
NIKUD_PATAH_LIKE_PATTERN = "[\u05b7-\u05b8]"
