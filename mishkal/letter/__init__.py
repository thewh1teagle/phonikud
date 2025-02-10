"""
The core of Mishkal.
Phonemes generated based on rules.

1. Vowels letters
2. Dagesh (Bet, Kaf, Kaf sofit, Fey, Fey Sofit), Sin, Shin dots
3. Vav vowels
4. Yod vowels
5. Het in end like Ko(ax)
6. Kamatz Gadol and Kamatz Katan (Kol VS Kala)
7. Shva Nah and Shva Na
"""

from mishkal.word.phoneme import Letter, Phoneme


def phonemize_letters(letters: list[Letter]) -> list[Phoneme]:
    phonemes: list[Phoneme] = []
    index = 0
    while index < len(letters):
        letter = letters[index]
        phonemes.append(Phoneme('o', '', letter, []))
        index += 1
    return phonemes
