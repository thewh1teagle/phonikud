"""
Dictionaries are tab separated key value words
"""
from pathlib import Path
import json
import re
from mishkal.utils import has_niqqud, remove_niqqud
from mishkal import config

files = Path(__file__).parent.glob('*.json')

class Dictionary:
    def __init__(self):        
        self.dict = {}
        self.load_dictionaries()


    def load_dictionaries(self):
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                parsed = json.load(f)
                self.dict.update(parsed)
            
    def replace_callback(self, match: re.Match[str]) -> str:
        found = match.group(0)
        without_niqqud = remove_niqqud(found)
        replace_word = self.dict.get(without_niqqud)
        if not replace_word:
            return found
        elif not has_niqqud(replace_word):
            return replace_word
        return found

    def expand_text(self, text: str) -> str:
        """
        TODO: if key doesn't have diacritics expand even diacritized words
        """
        text = re.sub(config.HE_CHARS_PATTERN, self.replace_callback, text)
        return text