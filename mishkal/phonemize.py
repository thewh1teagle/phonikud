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

from mishkal import vocab, utils
from .expander import Expander
from mishkal.utils import normalize, post_normalize
import re
from typing import Callable
import regex as re

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
        # TODO: is that enough? what if there's punctuation around? other chars?
        he_pattern = r"[\u05b0-\u05ea]+"
        fallback_pattern = r"[a-zA-Z]+"
        phonemes = []

        def fallback_replace_callback(match: re.Match):
            word = match.group(0)
            if self.expander.dictionary.dict.get(word):
                # skip
                # TODO: better API
                return word
            phonemes = fallback(word).strip()
            # TODO: check that it has only IPA?!
            for c in phonemes:
                vocab.SET_OUTPUT_CHARACTERS.add(c)
            return phonemes

        if fallback is not None:
            text = re.sub(fallback_pattern, fallback_replace_callback, text)
        text = self.expander.expand_text(text)
        self.fallback = fallback

        def heb_replace_callback(match: re.Match):
            word = match.group(0)
            word = normalize(word)
            word = "".join(
                i for i in word if i in vocab.SET_LETTERS or i in vocab.SET_NIQQUD
            )
            letters = re.findall(r'(\p{L})(\p{M}*)', word)
            hebrew_phonemes = self.phonemize_hebrew(letters)
            phonemes.extend(hebrew_phonemes)
            return "".join(phonemes)

        text = re.sub(he_pattern, heb_replace_callback, text)

        if not preserve_punctuation:
            text = "".join(i for i in text if i not in vocab.PUNCTUATION or i == " ")
        if not preserve_stress:
            text = "".join(
                i for i in text if i not in [vocab.STRESS, vocab.SECONDARY_STRESS]
            )
        text = post_normalize(text)
        text = "".join(i for i in text if i in vocab.SET_OUTPUT_CHARACTERS)

        return text

    def phonemize_hebrew(self, letters: list[str]):
        phonemes = []
        i = 0
        while i < len(letters):
            cur = letters[i]
            prev = letters[i - 1] if i > 0 else None
            next = letters[i + 1] if i < len(letters) - 1 else None
            # revised rules
            phoneme = vocab.LETTERS_PHONEMES.get(cur[0], "")
            phoneme += "".join(
                [vocab.NIQQUD_PHONEMES.get(niqqud, "") for niqqud in cur[1]]
            )
            phonemes.append(phoneme)
            i += 1
        return phonemes
