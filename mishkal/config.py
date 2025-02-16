# https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
HE_CHARS_PATTERN = r'\b[\u05B0-\u05EA]+\b' # Chars including niqqud
HE_NIQQUD_PATTERN = r'[\u05B0-\u05C7]'