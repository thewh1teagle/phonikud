"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

Early rules:
1. Niqqud malle vowels
2. Dagesh (custom beged kefet)
3. Final letter without niqqud
4. Final Het gnuva
5. Geresh (Gimel, Ttadik, Zain)
6. Shva nax and na
Revised rules:
1. Consonants
2. Niqqud

Reference:
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
"""

from .vocab import LETTERS_NAMES_PHONEMES, Letter, Token
from mishkal import vocab, utils
from .expander import Expander
from mishkal.utils import normalize
import re
from typing import Callable


# Vav vowel
vavs = {
    "doubles_identical": {"וּוּ": "vu", "וֹוֹ": "vo"},
    "doubles": {
        "ווּ": "vu",
        "ווֹ": "vo",
    },
    "start": {
        "וַ": "va",
        "וְ": "ve",
        "וֵ": "ve",
        "וִ": "vi",
        "וֹ": "vo",
        "וּ": "u",
        "וֻ": "vu",
    },
    "middle": {
        "וַ": "va",
        "וְ": "v",
        "וֵ": "ve",
        "וִ": "vi",
        "וֹ": "o",
        "וּ": "u",
        "וֻ": "u",
    },
}


class Phonemizer:
    def __init__(self):
        self.expander = Expander()

    def phonemize(
        self,
        text: str,
        preserve_punctuation=True,
        preserve_stress=True,
        fallback: Callable[[str], str] = None,
    ) -> str:
        he_pattern = r"[\u05b0-\u05ea]+"
        fallback_pattern = r"[a-zA-Z]+"

        def fallback_replace_callback(match: re.Match):
            word = match.group(0)

            if self.expander.dictionary.dict.get(word):
                # skip
                # TODO: better API
                return word
            if all(i in vocab.SET_OUTPUT_CHARACTERS for i in word):
                # already phonemized
                return word
            phonemes = fallback(word).strip()
            # TODO: check that it has only IPA?!
            for c in phonemes:
                vocab.SET_OUTPUT_CHARACTERS.add(c)
            return phonemes

        text = re.sub(fallback_pattern, fallback_replace_callback, text)
        text = self.expander.expand_text(text)
        tokens: list[Token] = []
        self.fallback = fallback

        def heb_replace_callback(match: re.Match):
            word = match.group(0)
            word = normalize(word)
            word = "".join(
                i for i in word if i in vocab.SET_LETTERS or i in vocab.SET_NIQQUD
            )
            letters = utils.extract_letters(word)
            hebrew_tokens = self.phonemize_hebrew(letters)
            tokens.extend(hebrew_tokens)
            return "".join(i.phonemes for i in hebrew_tokens)

        text = re.sub(he_pattern, heb_replace_callback, text)

        if not preserve_punctuation:
            text = "".join(i for i in text if i not in vocab.PUNCTUATION or i == " ")
        if not preserve_stress:
            text = "".join(
                i for i in text if i not in [vocab.STRESS, vocab.SECONDARY_STRESS]
            )
        text = "".join(i for i in text if i in vocab.SET_OUTPUT_CHARACTERS)
        return text

    def phonemize_hebrew(self, letters: list[Letter]) -> list[Token]:
        tokens: list[Token] = []
        i = 0
        while i < len(letters):
            cur = letters[i]
            prev = letters[i - 1] if i > 0 else None
            next = letters[i + 1] if i < len(letters) - 1 else None

            # early rules

            # Single letter name
            if not next and not prev and cur and not cur.symbols:
                token = Token(
                    cur.as_str(), LETTERS_NAMES_PHONEMES.get(cur.letter_str, "")
                )
                tokens.append(token)
                i += 1
                continue

            if cur.letter_str == "ו":
                # special doubles
                if next and cur.as_str() == next.as_str():
                    phonemes = vavs["doubles_identical"].get(
                        cur.as_str() + next.as_str(), "vo"
                    )
                    tokens.append(Token(cur.as_str() + next.as_str(), phonemes))
                    i += 2
                    continue
                # doubles with one has no symbols
                if next and (
                    cur == "ו" and next == "ו" and (not cur.symbols or not next.symbols)
                ):
                    phonemes = vavs["doubles"].get(cur.as_str() + next.as_str())
                    if not phonemes:
                        # take the one with the symbols
                        letter = cur.as_str() if cur.symbols else next.as_str()
                        phonemes = vavs["middle"].get(letter, "v")
                    tokens.append(Token(cur.as_str() + next.as_str(), phonemes))
                    i += 2
                    continue
                # start
                if not prev:
                    phonemes = vavs["start"].get(cur.as_str(), "v")
                    tokens.append(Token(cur.as_str(), phonemes))
                    i += 1
                    continue
                # middle
                phonemes = vavs["middle"].get(cur.as_str(), "v")
                tokens.append(Token(cur.as_str(), phonemes))
                i += 1
                continue
            # Yod vowel
            if cur == "י" and prev and not cur.symbols:  # Yod without niqqud
                # Not possible to say ii
                if tokens[-1].phonemes.endswith("i"):
                    token = Token(prev.as_str() + cur.as_str(), "")
                    tokens.append(token)
                    i += 1
                    continue
                if not prev.symbols:
                    phoneme = vocab.VOWEL_I
                    token = Token(prev.as_str() + cur.as_str(), phoneme)
                    tokens.append(token)
                    i += 1
                    continue
                elif "\u05b4" in prev.symbols:  # Hirik
                    phoneme = ""
                    token = Token(cur.as_str(), phoneme)
                    tokens.append(token)
                    i += 1
                    continue

            # Some final letters can be silent
            if not next and cur.letter_str in "אהע" and not cur.symbols:
                phoneme = ""
                token = Token(cur.as_str(), phoneme)
                tokens.append(token)
                i += 1
                continue
            # Het gnuva
            if not next and cur == "ח" and "\u05b7" in cur.symbols:  # Patah
                phoneme = vocab.HET_GNUVA
                token = Token(cur.as_str(), phoneme)
                tokens.append(token)
                i += 1
                continue

            # Geresh
            if "'" in cur.symbols and cur.letter_str in ["ג", "ז", "צ"]:
                phoneme = (
                    vocab.GIMEL_OR_ZAIN_WITH_DAGESH
                    if cur.letter_str in ["ג", "ז"]
                    else vocab.TSADIK_WITH_DAGESH
                )
                phoneme += "".join(
                    [vocab.NIQQUD_PHONEMES.get(niqqud, "") for niqqud in cur.symbols]
                )
                token = Token(cur.as_str() + (next.as_str() if next else ""), phoneme)
                tokens.append(token)
                i += 1
                continue

            # Shva nax and na
            if "\u05b0" in cur.symbols:
                phoneme = vocab.LETTERS_PHONEMES.get(cur.letter_str, "")
                # First
                if not prev:
                    if cur.letter_str == "ו":
                        phoneme += vocab.VOWEL_E
                    elif cur.letter_str in "למנרי":
                        phoneme += vocab.VOWEL_E
                    elif next and next.letter_str in "אהע":  # Groni
                        phoneme += vocab.VOWEL_E
                # Middle
                else:
                    # After vav with dagesh nax
                    if prev and prev.letter_str == "ו" and "\u05bc" in prev.symbols:
                        phoneme += ""
                    # Double final shva(s) nax
                    elif i == len(letters) - 1 and prev and "\u05b0" in prev.symbols:
                        phoneme += ""
                    elif i == len(letters) - 1 and next and "\u05b0" in next.symbols:
                        phoneme += ""
                    # Double shva same letter
                    elif next and next.letter_str == cur.letter_str:
                        phoneme += vocab.VOWEL_E
                    # Double shva
                    elif next and "\u05b0" in next.symbols:
                        phoneme += ""
                    # Previous nax
                    elif tokens:
                        if "\u05b0" in prev.symbols and not tokens[
                            -1
                        ].phonemes.endswith(vocab.VOWEL_E):
                            phoneme += vocab.VOWEL_E
                token = Token(cur.letter_str, phoneme)
                tokens.append(token)
                i += 1
                continue

            # revised rules
            phoneme = vocab.LETTERS_PHONEMES.get(cur.letter_str, "")
            phoneme += "".join(
                [vocab.NIQQUD_PHONEMES.get(niqqud, "") for niqqud in cur.symbols]
            )
            token = Token(cur.letter_str, phoneme)
            tokens.append(token)
            i += 1
        return tokens
