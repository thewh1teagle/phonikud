from .tables.diacritics import IPA_DIACRITICS
from .tables.letters import IPA_LETTERS
from .rules import (
    BEFORE_G2P_WHITELIST
)
from itertools import takewhile
import unicodedata
from .expanders import expand_word
from .log import log
from .ipa_from_word import get_ipa_from_word


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

class IpaWord:
    def __init__(self, source, ipa):
        self.source = source
        self.ipa = ipa

def text_to_ipa(text: str, get_words = False) -> str | list[IpaWord]:
    ipa_words: list[IpaWord] = []
    for line in text.splitlines():
        for word in line.split():
            for expanded_word in expand_word(word).split():
                # log.debug('before normalize %s', expanded_word)
                expanded_word = normalize(expanded_word)
                # log.debug('after normalize %s', expanded_word)
                ipa_transcription = get_ipa_from_word(expanded_word)
                # log.debug('IPA %s', ipa_transcription)
                ipa_words.append(IpaWord(word, ipa_transcription))
    if get_words:
        return ipa_words
    return ' '.join([i.ipa for i in ipa_words])
    
    # TODO    
    # valid_phonemes = []
    # for c in phonemes:
    #     if c in AFTER_G2P_WHITELIST:
    #         valid_phonemes.append(c)
    #     else:
    #         log.warning(f'Ignoring {c} after g2p')
            
            
    # return ''.join(valid_phonemes)