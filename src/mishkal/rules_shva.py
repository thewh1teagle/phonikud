"""
Special rules for when to add 'e' when there's Shva
"""

from .characters.diacritics import Diacritics
from .characters.letters import Letters
from .utils import contains_any, is_sofit

def should_add_e(current_letter: str, previous_letter: str, previous_diacritics: list, next_letter: str, next_diacritics: list) -> bool:
    # Start of word
    if not previous_letter and not previous_diacritics:
        has_next_kamatz = contains_any(
            next_diacritics,
            [Diacritics.KAMATZ ,Diacritics.KAMATZ_KATAN, Diacritics.HATAF_KAMATZ]
        )
        has_next_hirik = contains_any(
            next_diacritics,
            [Diacritics.HIRIK]
        )
        return (
            (not has_next_kamatz and not has_next_hirik)
            or next_letter in [Letters.HAF, Letters.KAF_DAGESH]
        )
    # Not start of word    
    else:
        
        has_previous_patah = contains_any(previous_diacritics, Diacritics.PATAH)
        has_previous_shva = contains_any(previous_diacritics, Diacritics.SHVA)
        has_previous_segol = contains_any(previous_diacritics, Diacritics.SEGOL)
        has_previous_kubutz = contains_any(previous_diacritics, Diacritics.KUBUTZ)
        
        has_next_kubutz = contains_any(next_diacritics, [Diacritics.KUBUTZ, Diacritics.KAMATZ])
        has_next_kamatz = contains_any(next_diacritics, [Diacritics.KAMATZ])
        has_next_patah = contains_any(next_diacritics, [Diacritics.PATAH])
        has_next_holam = contains_any(next_diacritics, [Diacritics.HOLAM])
        
        if is_sofit(current_letter):
            return False
        
        if has_previous_shva and has_next_holam:
            return True
        if has_previous_shva and not has_next_patah:
            return True
        if has_previous_shva and has_next_patah:
            return False
        if previous_letter == Letters.HE and has_previous_patah:
            # He Ayedia
            return False
        if (
            (has_previous_patah and not next_diacritics)
            or (
                (has_next_kubutz or has_next_kamatz) 
                and not (has_previous_patah and has_next_kamatz)
                and not has_previous_segol
                and not has_previous_kubutz
            )
        ):
            return True
    return False