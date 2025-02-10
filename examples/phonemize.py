"""
Quick Nakdan https://nakdanlive.dicta.org.il
Pro Nakdan https://nakdanpro.dicta.org.il
Manual Nakdan https://www.yo-yoo.co.il/tools/niqqud
"""
from mishkal import phonemize

text = 'שָׁלוֹם עוֹלָם'
phonemes = phonemize(text)
print(phonemes)