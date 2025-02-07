import unicodedata
from .chars import BEGED_KEFET

DAGESH = chr(0x05BC)

def normailze(text: str, normalize_beged_kefet = True) -> str:
    text = unicodedata.normalize("NFD", text)  # Decompose to separate diacritics
    new_text = []
    
    i = 0
    while i < len(text):
        char = text[i]
        if "א" <= char <= "ת":  # If it's a Hebrew letter
            
            diacritics = []
            i += 1
            # Collect diacritics
            while i < len(text) and unicodedata.category(text[i]) == "Mn":
                diacritics.append(text[i])
                i += 1
            # Ensure Dagesh is last if it exists
            
            if DAGESH in diacritics:
                diacritics.remove(DAGESH)
                if char in BEGED_KEFET or not normalize_beged_kefet:
                    # Keep Dagesh only if letter in beged kefet
                    diacritics.append(DAGESH)
                diacritics.sort()
            new_text.append(char + "".join(diacritics))
        else:
            new_text.append(char)
            i += 1
    return "".join(new_text) 