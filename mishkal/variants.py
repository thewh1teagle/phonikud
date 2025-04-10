import mishkal

class Letter:
    def __init__(self, char: str, diac: list[str]):
        self.char = mishkal.normalize(char)
        self.diac = mishkal.normalize(diac)

    def __repr__(self):
        return f"[Letter] {self.char}{''.join(self.diac)}"
    
    def __eq__(self, value: 'Letter'):
        return value.diac == self.diac and value.char == self.char
    
class Syllable:
    def __init__(self, chars, phones):
        self.chars = mishkal.normalize(chars)
        self.phones = phones

    def __repr__(self):
        return f'[Syllable] {self.chars}: {self.phones}'
    
    def __eq__(self, value: 'Syllable'):
        return self.chars == value.chars and self.phones == value.phones