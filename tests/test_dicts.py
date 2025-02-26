from mishkal.expander.dictionary import Dictionary
from mishkal import vocab


def test_dictionary():
    phonemes_without_punctuation = vocab.SET_OUTPUT_CHARACTERS.difference(
        vocab.SET_PUNCTUATION
    )
    dict = Dictionary()
    for k, v in dict.dict.items():
        for c in v:
            assert c in phonemes_without_punctuation, (
                f"The value of the word {k} is invalid: {v} the invalid character: {c}"
            )
