from itertools import takewhile
from .tables.diacritics import IPA_DIACRITICS
from .characters.letters import Letters


def get_diacritics(letter: str):
    diacritics = []
    if letter and "א" <= letter[0] <= "ת":
        diacritics = list(takewhile(lambda c: c in IPA_DIACRITICS, letter[1:]))
    return diacritics


def is_sofit(letter: str):
    return contains_any(
        letter,
        [
            Letters.HAF_SOFIT,
            Letters.KAF_SOFIT_DAGESH,
            Letters.MEM_SOFIT,
            Letters.NUN_SOFIT,
            Letters.PE_SOFIT,
            Letters.PE_SOFIT_DAGESH,
            Letters.TSADI_SOFIT,
        ],
    )


def contains_any(the_iter: list, values):
    if the_iter is None:
        return False
    return any(v in the_iter for v in values)
