import re
from mishkal.phonemize import Letter
from mishkal import vocab

def remove_niqqud(text: str):
    return re.sub(vocab.HE_NIQQUD_PATTERN, '', text)

def has_niqqud(text: str):
    return re.search(vocab.HE_NIQQUD_PATTERN, text) is not None

def extract_letters(word: str) -> list[Letter]:
    """
    Extract letters from word
    We assume that:
        - Dates expanded to words
        - Numbers expanded to word
        - Symbols expanded already
        - Known words converted to phonemes
        - Rashey Tavot (acronyms) expanded already
        - English words converted to phonemes already
        - Text normalized using unicodedata.normalize('NFD')
    
    This function extract *ONLY* hebrew letters and niqqud from LEXICON
    Other characters ignored!
    """
    # Normalize niqqud
    for niqqud, normalized in vocab.NIQQUD_NORMALIZE.items():
        word = word.replace(niqqud, normalized)
    # Remove non-lexicon characters
    word = ''.join([c for c in word if c in vocab.SET_INPUT_CHARACTERS])
    letters = []
    i = 0
    while i < len(word):
        char = word[i]
        if char in vocab.SET_LETTERS or char == "'":
            symbols = []
            i += 1  # Move to potential niqqud
            # Collect symbols attached to this letter
            while i < len(word) and (word[i] in vocab.SET_LETTER_SYMBOLS or word[i] == "'"):
                symbols.append(word[i])
                i += 1  # Move to the next character

            if char in 'בכפו' and '\u05BC' in symbols:
                char += '\u05BC'
            if '\u05BC' in symbols:
                symbols.remove('\u05BC') # remove dagesh
            # Shin
            if '\u05C1' in symbols:
                char += '\u05C1'
                symbols.remove('\u05C1') 
            # Sin
            if '\u05C2' in symbols:
                char += '\u05C2'
                symbols.remove('\u05C2') 
            letters.append(Letter(char, set(symbols)))
        else:
            i += 1  # Skip non-letter symbols
    return letters
