"""
Dictionaries are tab separated key value words
"""
from pathlib import Path
import json
import re
from mishkal.utils import remove_niqqud
from mishkal.utils import normalize

files = Path(__file__).parent.glob('*.json')

class Dictionary:
    def __init__(self):        
        self.dict = {}
        self.load_dictionaries()

    def load_dictionaries(self):
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                parsed = json.load(f)
                # normalize niqqud keys
                parsed = {normalize(k): v for k, v in parsed.items()}
                self.dict.update(parsed)

            
    def replace_callback(self, match: re.Match[str]) -> str:
        source = normalize(match.group(0))
        
        without_niqqud = remove_niqqud(source)
        
        without_niqqud_lookup = self.dict.get(without_niqqud)
        with_niqqud_lookup = self.dict.get(source)
        # Compare without niqqud ONLY if source has no niqqud
        if without_niqqud_lookup and source == without_niqqud:
            return without_niqqud_lookup
        elif with_niqqud_lookup:
            return with_niqqud_lookup
        return source

    def expand_text(self, text: str) -> str:
        """
        TODO: if key doesn't have diacritics expand even diacritized words
        """
        text = re.sub(r'\S+', self.replace_callback, text)
        return text