import num2words
from .number_names import NUMBER_NAMES
import re

def add_diacritics(words: str):
    new_words = []
    for word in words.split():
        if NUMBER_NAMES.get(word):
            new_words.append(NUMBER_NAMES[word])  
        elif NUMBER_NAMES.get(word[1:]):
            # With Vav or Bet
            new_words.append(NUMBER_NAMES[word[0]] + NUMBER_NAMES[word[1:]])  
        else:
            new_words.append(word)
    return ' '.join(new_words)


def num_to_word(maybe_number: str) -> str:
    def replace_number(match):
        num = match.group()
        words = num2words.num2words(num, lang="he", ordinal=False)
        return add_diacritics(words)

    # Replace all whole numbers in the string
    result = re.sub(r'\d+', replace_number, maybe_number)
    
    return result