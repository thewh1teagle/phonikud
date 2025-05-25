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
    return " ".join(new_words)


def num_to_word(maybe_number: str) -> str:
    def replace_number(match):
        num: str = match.group()
        suffix, prefix = "", ""
        # prefix
        if not num.startswith("-") and not num[0].isdigit():
            prefix = num[0]
            num = num[1:]
        if not num[-1].isdigit():
            suffix = num[-1]
            num = num[:-1]
        words = num2words.num2words(num, lang="he", ordinal=False)
        words_with_diacritics = add_diacritics(words)
        return (
            f"{prefix.strip()} {words_with_diacritics.strip()} {suffix.strip()}".strip()
        )

    # Replace all whole numbers in the string
    result = re.sub(r"[^\d\-]?-?\d+(?:[\.,]\d+)?[^\d]?", replace_number, maybe_number)

    return result
