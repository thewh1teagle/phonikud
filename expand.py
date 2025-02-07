import num2words

def expand(text: str) -> str:
    result = []
    for word in text.split():
        word = word.strip()
        if word.isdigit():
            result.append(num2words.num2words(word, lang='he'))
        else:
            result.append(word)
    return ' '.join(result)
