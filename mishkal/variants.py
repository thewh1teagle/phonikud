import mishkal


class Letter:
    def __init__(self, char: str, diac: list[str]):
        self.char = mishkal.normalize(char)
        self.diac = mishkal.normalize(diac)

    def __repr__(self):
        return f"[Letter] {self.char}{''.join(self.diac)}"

    def __eq__(self, value: "Letter"):
        return value.diac == self.diac and value.char == self.char

    def __str__(self):
        return self.char + self.diac
