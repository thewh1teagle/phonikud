"""
Special rules for when to add 'e' when there's Shva
"""

from .characters.diacritics import Diacritics
from .characters.letters import Letters
from .utils import contains_any

def should_add_e(previous_letter: str, previous_diacritics: list, next_letter: str, next_diacritics: list) -> bool:
    # Start of word
    if not previous_letter and not previous_diacritics:
        has_next_kamatz = all(
            d in  next_diacritics for d in 
            [Diacritics.KAMATZ ,Diacritics.KAMATZ_KATAN, Diacritics.HATAF_KAMATZ]
        )
        return (
            not has_next_kamatz
            or next_letter in [Letters.HAF, Letters.KAF_DAGESH]
        )
    # Not start of word    
    else:
        has_next_diacritics = bool(next_diacritics)
        has_previous_patah = contains_any(previous_diacritics, Diacritics.PATAH)
        has_previous_shva = contains_any(previous_diacritics, Diacritics.SHVA)
        has_previous_segol = contains_any(previous_diacritics, Diacritics.SEGOL)
        has_previous_kubutz = contains_any(previous_diacritics, Diacritics.KUBUTZ)
        has_next_kubutz_or_kamatz = contains_any(next_diacritics, [Diacritics.KUBUTZ, Diacritics.KAMATZ])
        has_next_kamatz = contains_any(next_diacritics, [Diacritics.KAMATZ])
        if (
            has_previous_shva
            or (has_previous_patah and not next_diacritics)
            or (
                has_next_kubutz_or_kamatz 
                and not (has_previous_patah and has_next_kamatz)
                and not has_previous_segol
                and not has_previous_kubutz
            )
        ):
            return True
    return False