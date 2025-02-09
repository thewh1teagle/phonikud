from itertools import takewhile
from .ipa_from_letter import get_ipa_from_letter
from .tables.diacritics import IPA_DIACRITICS


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
            # log.debug('letter %s', letter_ipa)
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
