import re
import unicodedata
from itertools import takewhile

def remove_niqqud(text: str) -> str:
    """
    https://github.com/elazarg/nakdimon/blob/08314aa8f0e98b6dc678f2d2433d9522d4c635df/nakdimon/hebrew.py#L321
    """
    return re.sub('[\u05B0-\u05BC\u05C1\u05C2ׇ\u05c7\u05BF]', '', text)

def get_diacritized_letters(text: str) -> list[str]:
    diacritized_letters = []
    text_nfd = unicodedata.normalize("NFD", text)
    i = 0
    while i < len(text_nfd):
        char = text_nfd[i]
        if "א" <= char <= "ת":  # Hebrew letter check
            diacritics = "".join(takewhile(lambda c: unicodedata.category(c) == "Mn", text_nfd[i+1:]))
            diacritized_letters.append(char + diacritics)
            i += len(diacritics)  # Skip the diacritics since we already processed them
        i += 1

    return diacritized_letters