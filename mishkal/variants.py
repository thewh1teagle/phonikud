"""
All variants in Hebrew that important for turning word into sound
We assume that the letters has niqqud, those we don't need to know what are the other words.
"""

import unicodedata

class Letter:
    def __init__(self, letter: str, symbols: str = []):
        self.letter = letter
        self.symbols = symbols

    def __repr__(self):
        symbols = ', '.join(unicodedata.name(c) for c in self.symbols) or None
        return f"Letter(letter='{self.letter}', symbols='{symbols}')"

class Phoneme:
    def __init__(self, phonemes: str, word: str, letter, reasons: list[str] = []):
        self.phonemes = phonemes
        self.word = word
        self.letter: 'Letter' = letter
        self.reasons = reasons
        
    def __repr__(self):
        return f"Phoneme(phonemes={self.phonemes!r}, word={self.word!r}, letter={self.letter!r}, reasons={self.reasons})"

class PhonemizedWord:
    def __init__(self, word: str, phonemes: list[Phoneme]):
        self.word = word
        self.phonemes = phonemes
    
    def as_phonemes_str(self) -> str:
        return ''.join(p.phonemes for p in self.phonemes)
    
    def as_word_str(self) -> str:
        return self.word
    
    def symbols_names(self) -> list[str]:
        names = []
        for phoneme in self.phonemes:
            for symbol in phoneme.letter.symbols:
                names.append(unicodedata.name(symbol, '?'))
        return ', '.join(names)