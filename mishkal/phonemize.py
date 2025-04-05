"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

Early rules:
1. Niqqud malle vowels
2. Dagesh (custom beged kefet)
3. Final letter without niqqud
4. Final Het gnuva
5. Geresh (Gimel, Ttadik, Zain)
6. Shva na
Revised rules:
1. Consonants
2. Niqqud

Reference:
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
"""

from mishkal import lexicon
from .expander import Expander
from mishkal.utils import normalize, post_normalize
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
        use_expander=False,
        use_post_normalize=False,  # For TTS
        fallback: Callable[[str], str] = None,
    ) -> str:
        # normalize
        text = normalize(text)
        # TODO: is that enough? what if there's punctuation around? other chars?
        he_pattern = r"[\u05b0-\u05ea\u05ab\u05bd']+"
        fallback_pattern = r"[a-zA-Z]+"

        def fallback_replace_callback(match: re.Match):
            word = match.group(0)

            if self.expander.dictionary.dict.get(word):
                # skip
                # TODO: better API
                return word
            phonemes = fallback(word).strip()
            # TODO: check that it has only IPA?!
            for c in phonemes:
                lexicon.SET_OUTPUT_CHARACTERS.add(c)
            return phonemes

        if fallback is not None:
            text = re.sub(fallback_pattern, fallback_replace_callback, text)
        if use_expander:
            text = self.expander.expand_text(text)
        self.fallback = fallback

        def heb_replace_callback(match: re.Match):
            word = match.group(0)

            word = normalize(word)
            word = "".join(
                i for i in word if i in lexicon.SET_LETTERS or i in lexicon.SET_NIQQUD
            )
            letters = re.findall(r"(\p{L})([\p{M}']*)", word)  # with en_geresh
            phonemes = self.phonemize_hebrew(letters)
            return "".join(phonemes)

        text = re.sub(he_pattern, heb_replace_callback, text)

        if not preserve_punctuation:
            text = "".join(i for i in text if i not in lexicon.PUNCTUATION or i == " ")
        if not preserve_stress:
            text = "".join(
                i for i in text if i not in [lexicon.STRESS, lexicon.SECONDARY_STRESS]
            )
        if use_post_normalize:
            text = post_normalize(text)
        text = "".join(i for i in text if i in lexicon.SET_OUTPUT_CHARACTERS)

        return text

    def phonemize_hebrew(self, letters: list[str]):
        phonemes = []
        i = 0

        while i < len(letters):
            cur = letters[i]
            prev = letters[i - 1] if i > 0 else None
            next = letters[i + 1] if i < len(letters) - 1 else None
            skip_diacritics = False
            skip_consonants = False
            # revised rules

            # יַאלְלָה
            if cur[0] == "ל" and cur[1] == "\u05b0" and next and next[0] == "ל":
                skip_diacritics = True
                skip_consonants = True

            if (
                cur[0] == "ו"
                and not prev
                and next
                and not next[1]
                and cur[0] + cur[1] == "וַא"
            ):
                i += 1
                phonemes.append("wa")

            if cur[0] == "א" and not cur[1] and prev:
                skip_consonants = True

            # TODO ?
            if cur[0] == "י" and next and not cur[1]:
                skip_consonants = True

            if cur[0] == "ש" and "\u05c2" in cur[1]:
                phonemes.append("s")
                skip_consonants = True

            # shin without niqqud after sin = sin
            if cur[0] == "ש" and not cur[1] and prev and "\u05c2" in prev[1]:
                phonemes.append("s")
                skip_consonants = True

            if not next and cur[0] == "ח":
                # Final Het gnuva
                phonemes.append("ax")
                skip_diacritics = True
                skip_consonants = True

            if cur and "'" in cur[1] and cur[0] in lexicon.GERESH_LETTERS:
                if cur[0] == "ת":
                    phonemes.append(lexicon.GERESH_LETTERS.get(cur[0], ""))
                    skip_diacritics = True
                    skip_consonants = True
                else:
                    # Geresh
                    phonemes.append(lexicon.GERESH_LETTERS.get(cur[0], ""))
                    skip_consonants = True

            elif (
                "\u05bc" in cur[1] and cur[0] + "\u05bc" in lexicon.LETTERS_PHONEMES
            ):  # dagesh
                phonemes.append(lexicon.LETTERS_PHONEMES.get(cur[0] + "\u05bc", ""))
                skip_consonants = True
            elif cur[0] == "ו":
                skip_consonants = True
                if next and next[0] == "ו":
                    # patah and next[1] empty
                    if cur[1] == "\u05b7" and not next[1]:
                        phonemes.append("w")
                        i += 2
                    else:
                        # double vav
                        phonemes.append("wo")
                        skip_diacritics = True
                else:
                    # Single vav

                    # Vav with Patah
                    if "\u05b7" in cur[1]:
                        phonemes.append("va")

                    # Holam haser
                    elif "\u05b9" in cur[1]:
                        phonemes.append("o")
                    # Shuruk / Kubutz
                    elif "\u05bb" in cur[1] or "\u05bc" in cur[1]:
                        phonemes.append("u")
                    # Vav with Shva in start
                    elif "\u05b0" in cur[1] and not prev:
                        phonemes.append("ve")
                    # Hirik
                    elif "\u05b4" in cur[1]:
                        phonemes.append("vi")
                    else:
                        phonemes.append("v")
                    skip_diacritics = True

            if not skip_consonants:
                phonemes.append(lexicon.LETTERS_PHONEMES.get(cur[0], ""))
            niqqud_phonemes = (
                [lexicon.NIQQUD_PHONEMES.get(niqqud, "") for niqqud in cur[1]]
                if not skip_diacritics
                else []
            )

            if "\u05ab" in cur[1] and phonemes:
                # Ensure ATMAHA is before the letter (before the last phoneme added)
                niqqud_phonemes.remove(lexicon.NIQQUD_PHONEMES["\u05ab"])
                phonemes = (
                    phonemes[:-1] + [lexicon.NIQQUD_PHONEMES["\u05ab"]] + [phonemes[-1]]
                )

            phonemes.extend(niqqud_phonemes)
            i += 1
        return phonemes
