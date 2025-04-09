class Letter:
    def __init__(self, char: str, diac: list[str]):
        self.char = char
        self.diac = diac

    def __repr__(self):
        return f"{self.char}{''.join(self.diac)}"