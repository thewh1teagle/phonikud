from string import printable as ENGLISH_PRINTABLE
from .ipa_tables.diacritics import IPA_DIACRITICS
from .ipa_tables.letters import IPA_LETTERS
from .characters.letters import Letters

BEFORE_G2P_WHITELIST = (
    list(ENGLISH_PRINTABLE) + list(IPA_LETTERS.keys()) + list(IPA_DIACRITICS.keys())
)

AFTER_G2P_WHITELIST = (
    list(map(chr, range(0x0250, 0x02B0))) +  # Basic IPA range (U+0250 to U+02AF)
    list(map(chr, range(0x1D00, 0x1D80)))    # IPA Extensions range (U+1D00 to U+1D7F)
)

# Letters that can have Dagesh with different sound
BEGED_KEFET_LETTERS = [
    Letters.VET,
    Letters.GIMEL,
    Letters.DALET,
    Letters.HAF,
    Letters.HAF_SOFIT,
    Letters.FEY,
    Letters.PE_SOFIT,
    Letters.TAF,
]

# Letters that affect previous letter sound
VOWEL_LETTERS = [Letters.VAV, Letters.YOD]  # Vav and Yod

# Letters that doesn't affected by Shva in first letter
BLACKLIST_START_AFFECTED_BY_SHVA = [
    Letters.SHIN,
    Letters.SHIN_RIGHT_POINT,
    Letters.VET,
    Letters.BET_DAGESH,
    Letters.KAF_DAGESH
]
