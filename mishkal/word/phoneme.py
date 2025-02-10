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
