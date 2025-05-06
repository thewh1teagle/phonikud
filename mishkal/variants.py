import mishkal
from mishkal import lexicon


class Letter:
    def __init__(self, char: str, diac: list[str]):
        self.char = mishkal.normalize(char)
        self.all_diac = mishkal.normalize(diac)
        self.diac = "".join(
            i for i in self.all_diac if i not in lexicon.SET_PHONETIC_DIACRITICS
        )

    def __repr__(self):
        return f"[Letter] {self.char}{''.join(self.all_diac)}"

    def __eq__(self, value: "Letter"):
        return value.all_diac == self.all_diac and value.char == self.char

    def __str__(self):
        return self.char + self.all_diac
