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
            # Ensure points sorted
            diacritics.sort()
            new_text.append(char + "".join(diacritics))
        else:
            new_text.append(char)
            i += 1
    return "".join(new_text) 