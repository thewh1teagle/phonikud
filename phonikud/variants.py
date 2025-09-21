import phonikud
from phonikud import lexicon


class Letter:
    def __init__(self, char: str, diac: list[str]):
        self.char = phonikud.normalize(char)
        self.all_diac = phonikud.normalize(diac)
        self.diac = "".join(
            i for i in self.all_diac if i not in lexicon.SET_ENHANCED_DIACRITICS
        )

    def __str__(self):
        return self.char + self.all_diac
