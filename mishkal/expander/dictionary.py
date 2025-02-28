"""
Dictionaries are tab separated key value words
"""

from pathlib import Path
import json
import re
from mishkal.utils import remove_niqqud
from mishkal.utils import normalize
import unicodedata

files = Path(__file__).parent.joinpath("../data").glob("*.json")
# Sort in reverse order to prioritize the most recent and best
order = {"bronze": 1, "silver": 2, "gold": 3}
files = sorted(
    files, key=lambda f: order.get(next((x for x in order if x in f.stem), ""), 0)
)


class Dictionary:
    def __init__(self):
        self.dict = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                dictionary: dict = json.load(f)
                normalized_dictionary = {}

                # normalize niqqud keys
                for k, v in dictionary.items():
                    k = normalize(k)
                    # Ensure not empty
                    if k and v:
                        normalized_dictionary[k] = v
                self.dict.update(normalized_dictionary)

    def replace_hebrew_only_callback(self, match: re.Match[str]) -> str:
        source: str = match.group(0)
        # decomposite
        source = unicodedata.normalize("NFD", source)
        raw_lookup = self.dict.get(source)

        without_niqqud_lookup = self.dict.get(remove_niqqud(source))
        with_niqqud_lookup = self.dict.get(normalize(source))
        # Compare without niqqud ONLY if source has no niqqud
        if raw_lookup:
            return raw_lookup
        if without_niqqud_lookup:
            return without_niqqud_lookup
        elif with_niqqud_lookup:
            return with_niqqud_lookup
        return source

    def replace_non_whitespace_callback(self, match: re.Match[str]) -> str:
        raw_source: str = match.group(0)
        if raw_source.isnumeric():
            return raw_source

        raw_lookup = self.dict.get(raw_source)

        # Compare without niqqud ONLY if source has no niqqud
        if raw_lookup:
            return raw_lookup
        # search by only ', space, regular niqqud, alphabet
        raw_source = re.sub(
            r"[\u05B0-\u05EB ']+", self.replace_hebrew_only_callback, raw_source
        )
        return raw_source

    def expand_text(self, text: str) -> str:
        """
        TODO: if key doesn't have diacritics expand even diacritized words
        """
        text = re.sub(r"\S+", self.replace_non_whitespace_callback, text)

        return text
