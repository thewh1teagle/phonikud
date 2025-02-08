# Mishkal

grapheme to phoneme in Hebrew

## How it works

1. Dates are expanded into diacritized words (eg. 20/01/2025 into spoken words)
2. Numbers are expanded into diacritized words (eg. 2000 into single word)
3. Characters iterated and diacritics collected for each
4. Early phonemes returns based on surround context (cur, cur_d, prev, prev_d, next)
5. If early phonemes not returned the base sound of the character added
6. Diacritics added as sounds that affect the letter