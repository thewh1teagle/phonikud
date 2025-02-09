from .characters.diacritics import Diacritics
from .tables.diacritics import IPA_DIACRITICS
from .tables.letters import IPA_LETTERS
from .rules import (
    BEFORE_G2P_WHITELIST, BEGED_KEFET_LETTERS, BLACKLIST_START_AFFECTED_BY_SHVA,
    AFTER_G2P_WHITELIST, PART_OF_LETTER_DIACRITICS
)
from .characters.letters import Letters
from itertools import takewhile
import unicodedata
from .expanders import expand_word
from .log import log

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
    log.debug('cur: %s (%s) next: %s (%s)', current_letter, list(hex(ord(i)) for i in diacritics), next_letter, list(hex(ord(i)) for i in (next_diacritics or [])))
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
    if current_letter in [Letters.HAF, Letters.KAF_DAGESH] and not previous_letter:
        if any(d in diacritics for d in [Diacritics.KAMATZ, Diacritics.KAMATZ_KATAN, Diacritics.HOLAM]):
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
            and not previous_letter and not previous_diacritics
            and next_diacritics # Eg. Klomar has no in Lamed
            and not any(d in next_diacritics for d in [Diacritics.KAMATZ ,Diacritics.KAMATZ_KATAN, Diacritics.HATAF_KAMATZ])
            # and current_letter not in BLACKLIST_START_AFFECTED_BY_SHVA
            # TODO: is is correct?
            # and Diacritics.DAGESH not in diacritics
        ):
            transcription += 'e'
        
        transcription += IPA_DIACRITICS[d]
    # log.debug(transcription)
    return transcription

def get_next_letter_with_diacritics(text: str):
    letter, diacritics = None, None
    if text and 'א' <= text[0] <= 'ת':
        letter = text[0]
        diacritics = list(takewhile(lambda c: c in IPA_DIACRITICS, text[1:]))
    return letter, diacritics
        

def get_ipa_from_word(text: str):
    """
    Iterate characters and get IPA based on character or character + diacritics
    """
    
    transcription = ''
    # Offset
    i = 0
    
    previous_diacritics = None
    previous_letter = None
    
    while i < len(text):
        char = text[i]
        
        if 'א' <= char <= 'ת':
            # Move offset to diacritics
            
            i += 1
            diacritics = list(takewhile(lambda c: c in IPA_DIACRITICS, text[i:]))
            
            next_letter, next_diacritics = get_next_letter_with_diacritics(text[i+len(diacritics):])
            
            letter_ipa = get_ipa_from_letter(
                char, 
                diacritics.copy(), 
                previous_letter, 
                previous_diacritics, 
                next_letter, 
                next_diacritics
            )
            log.debug('letter %s', letter_ipa)
            transcription += letter_ipa
            
            
            # Store previous
            previous_letter = char
            previous_diacritics = diacritics
            
            # Move offset
            i += len(diacritics)
        else:
            transcription += char
            i += 1

    return transcription

def clean_wrong_diacritics(text: str) -> str:
    """
    clean diacritics that's randomally placed not after letter
    """
    new_text = ''
    # Offest
    i = 0   
    while i < len(text):
        char = text[i]
        if char in IPA_LETTERS:
            # Move offset to diacritics
            i += 1
            diacritics = ''.join(takewhile(lambda c: c in IPA_DIACRITICS, text[i:]))
            new_text += char + diacritics
            i += len(diacritics)
        elif char in IPA_DIACRITICS:
            i += 1 # Skip it!
        else:
            new_text += char
            i += 1
    return text

def normalize(text: str) -> str:
    # Decomposite diacritics
    text = unicodedata.normalize('NFD', text)
    # Keep only chars from whitelist
    chars = []
    for c in text:
        if c in BEFORE_G2P_WHITELIST:
            chars.append(c)
        else:
            log.warning(f'Ignoring {c}')
            
    text = ''.join(chars) 
    text = clean_wrong_diacritics(text)

    return text

def text_to_ipa(text: str) -> str:
    ipa_words = []
    for line in text.splitlines():
        for word in line.split():
            for expanded_word in expand_word(word).split():
                log.debug('before normalize %s', expanded_word)
                expanded_word = normalize(expanded_word)
                log.debug('after normalize %s', expanded_word)
                ipa_transcription = get_ipa_from_word(expanded_word)
                log.debug('IPA %s', ipa_transcription)
                ipa_words.append(ipa_transcription)
    phonemes = ' '.join(ipa_words)
    return phonemes
    
    # TODO    
    # valid_phonemes = []
    # for c in phonemes:
    #     if c in AFTER_G2P_WHITELIST:
    #         valid_phonemes.append(c)
    #     else:
    #         log.warning(f'Ignoring {c} after g2p')
            
            
    # return ''.join(valid_phonemes)