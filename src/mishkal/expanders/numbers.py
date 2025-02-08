import num2words
from .numbers_with_diacritics import ALL_NUMBERS
import re

def add_diacritics(words: str):
    new_words = []
    for word in words.split():
        if ALL_NUMBERS.get(word):
            new_words.append(ALL_NUMBERS[word])  
        elif ALL_NUMBERS.get(word[1:]):
            # With Vav or Bet
            new_words.append(ALL_NUMBERS[word[0]] + ALL_NUMBERS[word[1:]])  
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
