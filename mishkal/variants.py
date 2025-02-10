"""
All variants in Hebrew that important for turning word into sound
We assume that the letters has niqqud, therefore we don't need to know what are the other words.
"""

import unicodedata
from mishkal.lexicon.symbols import LetterSymbol

class Letter:
    def __init__(self, letter_str: str, symbols: list[str] = []):
        self.letter_str = letter_str
        self.symbols: list[str] = symbols

    def __repr__(self):
        symbols = ', '.join(unicodedata.name(c) for c in self.symbols) or None
        return f"Letter(letter='{self.letter_str}', symbols='{symbols}')"
    
    def as_str(self) -> str:
        return self.letter_str
    
    def as_str_with_niqqud(self) -> str:
        return self.letter_str + ''.join(self.symbols)
    
    def get_symbols(self):
        return self.symbols
    
    def plain_niqqud(self):
        """
        niqqud without dagesh / points / geresh
        """
        return [
            i for i in self.symbols 
            if i not in [
                LetterSymbol.dagesh_or_mapiq,  
                LetterSymbol.geresh_en, 
                LetterSymbol.geresh, 
                LetterSymbol.shin_dot, 
                LetterSymbol.sin_dot
            ]
        ]
    
    def contains_any_symbol(self, symbols: iter):
        return any(i in self.symbols for i in symbols)
    
    def contains_all_symbol(self, symbols: iter):
        return all(i in self.symbols for i in symbols)
    
    def contains(self, symbols: iter):
        return any(i in self.symbols + self.letter_str for i in symbols)

    def niqqud_without_geresh(self):
            """
            niqqud without dagesh / points / geresh
            """
            return [
                i for i in self.symbols 
                if i not in [
                    LetterSymbol.geresh, 
                    LetterSymbol.geresh_en, 
                ]
            ]

class Phoneme:
    def __init__(self, phonemes: str, word: str, letter, reasons: list[str] = []):
        self.phonemes = phonemes
        self.word = word
        self.letter: 'Letter' = letter
        self.reasons = reasons
        self.phoneme_ready = False
        self.letter_ready = False
        
    def add_phonemes(self, phonemes: str, reason: str):
        if self.phoneme_ready:
            raise RuntimeError(f'Trying to add phonemes for ready letter: {self.letter}', )
        self.phonemes += phonemes
        self.reasons.append(f'add {phonemes} reason: {reason}')
        
    def __repr__(self):
        return f"Phoneme(phonemes={self.phonemes!r}, word={self.word!r}, letter={self.letter!r}, reasons={self.reasons})"
    
    def get_reasons(self):
        return self.reasons
    
    def is_letter_ready(self) -> bool:
        return self.letter_ready
    
    def mark_letter_ready(self):
        self.letter_ready = True
    
    def is_ready(self) -> bool:
        return self.phoneme_ready

    def mark_ready(self):
        self.phoneme_ready = True
        

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
    
    def __repr__(self):
        return ', '.join([repr(i) for i in self.phonemes])