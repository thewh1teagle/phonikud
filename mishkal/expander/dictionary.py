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
                parsed: dict = json.load(f)

                # normalize niqqud keys
                parsed = {normalize(k): v for k, v in parsed.items()}
                self.dict.update(parsed)

    def replace_hebrew_only_callback(self, match: re.Match[str]) -> str:
        raw_source: str = match.group(0)
        # decomposite
        source = unicodedata.normalize("NFD", raw_source)

        # Keep only ', space, regular niqqud, alphabet
        source = re.sub(r"[^'\u05B0-\u05EB ]", "", source)
        raw_lookup = self.dict.get(raw_source)
        without_niqqud_lookup = self.dict.get(remove_niqqud(source))
        with_niqqud_lookup = self.dict.get(normalize(source))
        # Compare without niqqud ONLY if source has no niqqud
        if raw_lookup:
            return raw_lookup
        if without_niqqud_lookup:
            return without_niqqud_lookup
        elif with_niqqud_lookup:
            return with_niqqud_lookup
        return raw_source

    def replace_non_whitespace_callback(self, match: re.Match[str]) -> str:
        raw_source: str = match.group(0)
        if raw_source.isnumeric():
            return raw_source
        raw_lookup = self.dict.get(raw_source)
        # Compare without niqqud ONLY if source has no niqqud
        if raw_lookup:
            return raw_lookup
        return self.replace_hebrew_only_callback(match)

    def expand_text(self, text: str) -> str:
        """
        TODO: if key doesn't have diacritics expand even diacritized words
        """
        text = re.sub(r"\S+", self.replace_non_whitespace_callback, text)
        return text
