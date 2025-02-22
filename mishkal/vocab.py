"""
ASCII IPA transcription of Hebrew consonants and vowels.
"""
import unicodedata

class Letter:
    def __init__(self, letter_str: str, symbols: list[str] = []):
        self.letter_str = letter_str
        self.symbols: list[str] = symbols
    
    def __repr__(self):
        return f"{self.letter_str + ' ' + ', '.join(unicodedata.name(s) for s in self.symbols)}"
    
    def __eq__(self, other: str):
        return self.letter_str == other or self.letter_str + ''.join(self.symbols) == other
    
    def as_str(self):
        return self.letter_str + ''.join(self.symbols)
        
class Token:
    def __init__(self, token: str, phonemes: str = ''):
        self.token = token
        self.phonemes: str = phonemes
        
    def __repr__(self):
        return f'{self.token} {self.phonemes}'

# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
HE_CHARS_PATTERN = r"\b[\u05B0-\u05EA\u05F3\u0027]+\b" # Chars including niqqud, geresh and en_geresh
HE_NIQQUD_PATTERN = r'[\u05B0-\u05C7]'

PUNCTUATION = r"""- .,"':!?()"""

# Special
GIMEL_OR_ZAIN_WITH_DAGESH = 'dʒ'
TSADIK_WITH_DAGESH = 'tʃ'
SHIN_WITH_POINT = 'ʃ'
SIN_WITH_POINT = 's'
STRESS = "\u02C8"
SECONDARY_STRESS = "\u02CC"
HET_GNUVA = 'ax'

LETTERS_NAMES_PHONEMES = {
    'א': 'ʔalef',  # Alef, glottal stop
    'ב': 'bet',  # Bet
    'ג': 'gimel',  # Gimel
    'ד': 'dalet',  # Dalet
    'ה': 'hej',  # He
    'ו': 'vav',  # Vav
    'ז': 'zajin',  # Zayin
    'ח': 'xet',  # Het
    'ט': 'tet',  # Tet
    'י': 'jud',  # Yod
    'ך': 'xaf sofit',  # Haf sofit
    'כ': 'xaf',  # Haf
    'ל': 'lamed',  # Lamed
    'ם': 'mem sofit',  # Mem Sofit
    'מ': 'mem',  # Mem
    'ן': 'nun sofit',  # Nun Sofit
    'נ': 'nun',  # Nun
    'ס': 'samex',  # Samekh
    'ע': 'ʔajin',  # Ayin, glottal stop
    'פ': 'fey',  # Fey
    'ף': 'fey sofit',  # Fey Sofit
    'ץ': 'tsadik sofit',  # Tsadik sofit
    'צ': 'tsadik',  # Tsadik
    'ק': 'kuf',  # Kuf
    'ר': 'rejiʃ',  # Resh
    'ש': 'ʃin',  # Shin
    'ת': 'taf',  # Taf
}

# Consonants
LETTERS_PHONEMES = {
    'א': 'ʔ',  # Alef, glottal stop
    'ב': 'v',  # Bet
    'ג': 'g',  # Gimel
    'ד': 'd',  # Dalet
    'ה': 'h',  # He
    'ו': 'v',  # Vav
    'ז': 'z',  # Zayin
    'ח': 'x',  # Het
    'ט': 't',  # Tet
    'י': 'j',  # Yod
    'ך': 'x',  # Haf sofit
    'כ': 'x',  # Haf
    'ל': 'l',  # Lamed
    'ם': 'm',  # Mem Sofit
    'מ': 'm',  # Mem
    'ן': 'n',  # Nun Sofit
    'נ': 'n',  # Nun
    'ס': 's',  # Samekh
    'ע': 'ʔ',  # Ayin, glottal stop
    'פ': 'f',  # Fey
    'ף': 'f',  # Fey Sofit
    'ץ': 'ts',  # Tsadik sofit
    'צ': 'ts',  # Tsadik
    'ק': 'k',  # Kuf
    'ר': 'r',  # Resh
    'ש': 'ʃ',  # Shin
    'ת': 't',  # Taf
    
    # Beged Kefet
    'בּ': 'b',
    'כּ': 'k',
    'פּ': 'p',
    'שׁ': 'ʃ',
    'שׂ': 's',
    
    'וּ': 'u'
}

# Vowels
VOWEL_A = 'a'
VOWEL_E = 'e'
VOWEL_I = 'i'
VOWEL_O = 'o'
VOWEL_U = 'u'

NIQQUD_PHONEMES = {
    '\u05B4': 'i',  # Hiriq
    '\u05B5': 'e',  # Tsere
    '\u05B7': 'a',  # Patah
    '\u05B9': 'o',  # Holam
    '\u05BA': 'o',  # Holam haser for vav
    '\u05BB': 'u',  # Qubuts
}

SET_LETTER_SYMBOLS = {
    '\u05B0',  # Shva
    '\u05B4',  # Hiriq
    '\u05B5',  # Tsere
    '\u05B7',  # Patah
    '\u05B9',  # Holam
    '\u05BA',  # Holam haser for vav
    '\u05BB',  # Qubuts
    '\u05BC',  # Dagesh
    '\u05C1',  # Shin dot
    '\u05C2',  # Sin dot
    "'", # Geresh
}

"""
We're left with the following niqqud (10):  
Shva, Hiriq, Tsere, Patah, Holam, Holam haser for vav, Qubuts, Dagesh, Shin dot, Sin dot
"""
NIQQUD_NORMALIZE = {
    '\u05B1': '\u05B5',  # Hataf Segol -> Tsere
    '\u05B2': '\u05B7',  # Hataf Patah -> Patah
    '\u05B3': '\u05B9',  # Hataf Qamats -> Holam
    '\u05B6': '\u05B5',  # Segol -> Tsere
    # Kamatz -> Patah
    '\u05B8': '\u05B7',  # Qamats -> Patah
    '\u05C7': '\u05B9',  # Qamats Qatan -> Holam
    '\u05F3': "'",  # Hebrew geresh to regular geresh
}

LETTERS_NORMALIZE = {
    '\u05DA': '\u05DB',  # Haf sofit -> Haf
    '\u05DD': '\u05DE',  # Mem Sofit -> Mem
    '\u05DF': '\u05E0',  # Nun Sofit -> Nun
    '\u05E3': '\u05E4',  # Fey Sofit -> Fey
    '\u05E5': '\u05E6',  # Tsadik sofit -> Tsadik
}




SET_OUTPUT_CHARACTERS = set(
    [GIMEL_OR_ZAIN_WITH_DAGESH, TSADIK_WITH_DAGESH, SHIN_WITH_POINT, SIN_WITH_POINT] +
    [STRESS, SECONDARY_STRESS] +
    list(LETTERS_PHONEMES.values())+ 
    list(NIQQUD_PHONEMES.values()) +
    [VOWEL_A, VOWEL_E, VOWEL_I, VOWEL_O, VOWEL_U] +
    list(PUNCTUATION)
)

SET_NIQQUD = {
    # Shva, Hiriq, Tsere, Patah, Holam, Holam haser for vav, Qubuts, Dagesh, Shin dot, Sin dot
    '\u05B0', '\u05B4', '\u05B5', '\u05B7', '\u05B9', '\u05BA', '\u05BB', '\u05BC', '\u05C1', '\u05C2'
}
SET_LETTERS = set(LETTERS_PHONEMES.keys())
SET_PUNCTUATION = set(PUNCTUATION)
    

# Set for fast lookup
SET_INPUT_CHARACTERS = set(
    list(LETTERS_PHONEMES.keys()) +
    list(SET_NIQQUD) +
    list(PUNCTUATION) + ["'"]
)
