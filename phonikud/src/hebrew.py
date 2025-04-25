import re

def is_hebrew_letter(char):
   return 'א' <= char <= 'ת'

MATRES_LETTERS = list('אוי')
def is_matres_letter(char):
    return char in MATRES_LETTERS

nikud_pattern = re.compile(r'[\u05B0-\u05BD\u05C1\u05C2\u05C7]')
def remove_nikud(text):
    return nikud_pattern.sub('', text)

STRESS_CHAR = chr(1451) # "ole" symbol marks stress
MOBILE_SHVA_CHAR = chr(1469) # "meteg" symbol marks shva na (mobile shva)