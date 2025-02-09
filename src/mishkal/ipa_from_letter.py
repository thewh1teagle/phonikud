from .characters.diacritics import Diacritics
from .tables.diacritics import IPA_DIACRITICS
from .tables.letters import IPA_LETTERS
from .rules import (
     BEGED_KEFET_LETTERS,
     PART_OF_LETTER_DIACRITICS
)
from .characters.letters import Letters
from itertools import takewhile
from . import rules_shva
from .utils import contains_any, is_sofit

def get_ipa_from_letter(
    current_letter: str, 
    diacritics: list[str], 
    previous_letter: str = None, 
    previous_diacritics: str = None,
    next_letter: str = None,
    next_diacritics: list[str] = None
):
    """
    Get IPA for letter based on current character and it's surround context
    """
    # log.debug('cur: %s (%s) next: %s (%s)', current_letter, list(hex(ord(i)) for i in diacritics), next_letter, list(hex(ord(i)) for i in (next_diacritics or [])))
    transcription = ''
    # if current_letter == 'ו':
    #     breakpoint()
    # Handle Dagesh for Beged Kefet
    if Diacritics.DAGESH in diacritics and current_letter in BEGED_KEFET_LETTERS:
        current_letter += Diacritics.DAGESH
    # Handle Shin and Sin
    for d in [Diacritics.SIN_DOT, Diacritics.SHIN_DOT]:
        if d in diacritics:
            current_letter += d
            diacritics.remove(d)
    # Vav vowels (with Holam Haser or Dagesh)
    if (
        # Vav with single diacritic with previous letter
        current_letter == Letters.VAV and len(diacritics) == 1 and previous_letter
        # Only if previous letter has no diacritics
        and (not previous_diacritics or any(d in PART_OF_LETTER_DIACRITICS for d in previous_diacritics))
    ):
        # Double Vav
        if previous_letter == Letters.VAV and Diacritics.DAGESH in previous_diacritics:
            return ''
        if next_letter == Letters.VAV and Diacritics.DAGESH in next_diacritics and Diacritics.DAGESH in diacritics:
            return 'vu'
        
        if Diacritics.DAGESH in diacritics:
            return 'u' # Like Uga
        elif any(d in [Diacritics.VAV_HOLAM_HASER, Diacritics.HOLAM] for d in diacritics):
            return 'o' # Like Or
    # Vav in start
    if current_letter == Letters.VAV and not previous_letter:
        if Diacritics.DAGESH in diacritics:
            return 'u'
    # Yod without diacritics and previous Hirik (or non diacritics in previous)
    if previous_letter and not diacritics and current_letter == Letters.YOD and (Diacritics.HIRIK in previous_diacritics or not previous_diacritics):
        if Diacritics.HIRIK in previous_diacritics:
            return '' # Handled by Hirik in previous letter
    # Haf in first letter with some kamatz or without
    if current_letter in [Letters.HAF, Letters.KAF_DAGESH]:
        has_kamatz = contains_any(
                diacritics,
                [Diacritics.KAMATZ, Diacritics.KAMATZ_KATAN, Diacritics.HOLAM]
        )
        previous_has_kamatz = contains_any(
                previous_diacritics or [],
                [Diacritics.KAMATZ, Diacritics.KAMATZ_KATAN, Diacritics.HOLAM]
        )
        condition = (
            (not previous_letter or not next_diacritics) 
            and has_kamatz and not previous_has_kamatz 
            and not is_sofit(next_letter)
        )
        if condition:
            return 'xo' if current_letter == Letters.HAF else 'ko'

    # Het in end of word with Patah should sound as Ax
    if not next_letter and current_letter == Letters.HET and Diacritics.PATAH in diacritics:
        return 'ax'    
    
    # Handle next letter in Gimel like Jirafa and keep diacritics for later
    if next_letter == "'" and current_letter in [Letters.GIMEL, Letters.GIMEL_DAGESH]:
        transcription += 'd͡ʒ' # J'irafa
    # Handle next letter in Gimel like Jirafa
    elif next_letter == "'" and current_letter in [Letters.TSADI, Letters.TSADI_SOFIT]:
        transcription += 'tʃ'
    else:
        transcription += IPA_LETTERS[current_letter]        
    
    # Convert diacritics to sounds excluding Dagesh
    
    
    diacritics.sort()
    for d in diacritics:
        # Dagesh handled with Vav or Beged Kefet already
        if d == Diacritics.DAGESH:
            continue
        # First letter with shva should sound like d(e)
        elif (
            d == Diacritics.SHVA
            and rules_shva.should_add_e(current_letter, previous_letter, previous_diacritics, next_letter, next_diacritics)
        ):
            transcription += 'e'
        # ALEF with Kamatz in start with next letter Shva is like in Hozniyot without Vav
        elif current_letter == Letters.ALEF and not previous_letter and d == Diacritics.KAMATZ and Diacritics.SHVA in (next_diacritics or []):
            transcription += 'o'
        else:
            # Rest of diacritics
            transcription += IPA_DIACRITICS[d]
    # log.debug(transcription)
    return transcription

def get_next_letter_with_diacritics(text: str):
    letter, diacritics = None, None
    if text and 'א' <= text[0] <= 'ת':
        letter = text[0]
        diacritics = list(takewhile(lambda c: c in IPA_DIACRITICS, text[1:]))
    return letter, diacritics
        