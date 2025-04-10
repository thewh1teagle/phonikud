"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

Early rules:
1. Nikud malle vowels
2. Dagesh (custom beged kefet)
3. Final letter without nikud
4. Final Het gnuva
5. Geresh (Gimel, Ttadik, Zain)
6. Shva na
Revised rules:
1. Consonants
2. Nikud

Reference:
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://hebrew-academy.org.il/2010/03/24/צהרים-נעמי-הגיית-קמץ-לפני-חט/
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
- https://he.wikipedia.org/wiki/הברה
"""

from mishkal.utils import has_vowel
from mishkal.variants import Letter, Syllable
from mishkal import lexicon
import re

def phonemize_hebrew(letters: list[Letter], predict_shva_na: bool) -> list[Syllable]:
    phonemes = []
    i = 0

    syllables = []
    cur_syllable = Syllable('', '')
    while i < len(letters):
        
        cur = letters[i]
        prev = letters[i - 1] if i > 0 else None
        next = letters[i + 1] if i < len(letters) - 1 else None
        cur_phonemes = []
        skip_diacritics = False
        skip_constants = False
        skip_offset = 0
        # revised rules

        # יַאלְלָה
        if cur.char == "ל" and cur.diac == "\u05b0" and next and next.char == "ל":
            skip_diacritics = True
            skip_constants = True

        if (
            cur.char == "ו"
            and not prev
            and next
            and not next.diac
            and cur.char + cur.diac == "וַא"
        ):
            skip_offset += 1
            cur_phonemes.append("wa")

        if cur.char == "א" and not cur.diac and prev:
            if next and next.char != 'ו':
                skip_constants = True

        # TODO ?
        if cur.char == "י" and next and not cur.diac and prev.char + prev.diac != 'אֵ':
            skip_constants = True

        if cur.char == "ש" and "\u05c2" in cur.diac:
            cur_phonemes.append("s")
            skip_constants = True

        # shin without nikud after sin = sin
        if cur.char == "ש" and not cur.diac and prev and "\u05c2" in prev.diac:
            cur_phonemes.append("s")
            skip_constants = True

        if not next and cur.char == "ח" and '\u05b7' in cur.diac:
            # Final Het gnuva
            cur_phonemes.append("ax")
            skip_diacritics = True
            skip_constants = True

        if cur and "'" in cur.diac and cur.char in lexicon.GERESH_PHONEMES:
            if cur.char == "ת":
                cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
                skip_diacritics = True
                skip_constants = True
            else:
                # Geresh
                cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
                skip_constants = True

        elif (
            "\u05bc" in cur.diac and cur.char + "\u05bc" in lexicon.LETTERS_PHONEMES
        ):  # dagesh
            cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char + "\u05bc", ""))
            skip_constants = True
        elif cur.char == "ו":
            skip_constants = True
            if next and next.char == "ו" and next.diac == cur.diac:
                # patah and next.diac empty
                if cur.diac in ["\u05b7", "\u05b8"] and not next.diac:
                    cur_phonemes.append("w")
                    skip_diacritics = True
                    skip_offset += 1
                elif cur.diac == next.diac:
                    # double vav
                    cur_phonemes.append("wo")
                    skip_diacritics = True
                    skip_offset += 1
                else:
                    # TODO ?
                    # skip_consonants = False
                    skip_diacritics = False
            else:
                # Single vav

                # Vav with Patah
                if re.search("[\u05b7-\u05b8]", cur.diac):
                    cur_phonemes.append("va")

                # Holam haser
                elif "\u05b9" in cur.diac:
                    cur_phonemes.append("o")
                # Shuruk / Kubutz
                elif "\u05bb" in cur.diac or "\u05bc" in cur.diac:
                    cur_phonemes.append("u")
                # Vav with Shva in start
                elif "\u05b0" in cur.diac and not prev:
                    cur_phonemes.append("ve")
                # Hirik
                elif "\u05b4" in cur.diac:
                    cur_phonemes.append("vi")
                # Tsere
                elif "\u05b5" in cur.diac:
                    cur_phonemes.append("ve")
                
                else:
                    cur_phonemes.append("v")
                skip_diacritics = True

        if not skip_constants:
            cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char, ""))
        
        if predict_shva_na and '\u05b0' in cur.diac and not skip_diacritics and lexicon.SHVA_NA_DIACRITIC not in cur.diac:
            # shva na prediction
            if not prev:
                if cur.char in 'למנרי' or cur.char in 'אהע' or cur.char in 'וכלב':
                    cur_phonemes.append("e")
                    skip_diacritics = True 
            else:
                if next and next.char == cur.char:
                    cur_phonemes.append("e")
                    skip_diacritics = True
                elif prev and '\u05b0' in prev.diac and phonemes[-1] != 'e':
                    cur_phonemes.append("e")
                    skip_diacritics = True

        if '\u05b8' in cur.diac and next and '\u05b3' in next.diac:
            cur_phonemes.append('o')
            skip_diacritics = True


        
        nikud_phonemes = (
            [lexicon.NIKUD_PHONEMES.get(nikud, "") for nikud in cur.diac]
            if not skip_diacritics
            else []
        )            
        
        cur_phonemes.extend(nikud_phonemes)
        # Ensure the stress is at the beginning of the syllable
        cur_phonemes.sort(key=lambda x: x != 'ˈ')
        phonemes.extend(cur_phonemes)
        
        cur_phonemes = [p for p in cur_phonemes if all(i in lexicon.SET_PHONEMES for i in p)]
        

        if not next:
            cur_syllable.chars += cur.char + cur.diac
            cur_syllable.phones += ''.join(cur_phonemes)
            syllables.append(cur_syllable)
        elif not prev:
            cur_syllable = Syllable(cur.char + cur.diac, ''.join(cur_phonemes))

        elif len(re.findall('[א-ת]', cur_syllable.chars)) >= 2 and has_vowel(cur_syllable.phones) and cur.diac:
            syllables.append(cur_syllable)
            cur_syllable = Syllable(cur.char + cur.diac, ''.join(cur_phonemes))

        elif not has_vowel(cur_phonemes):                
            cur_syllable.chars += cur.char + cur.diac
            cur_syllable.phones += ''.join(cur_phonemes)

        elif not has_vowel(cur_syllable.phones):
            cur_syllable.chars += cur.char + cur.diac
            cur_syllable.phones += ''.join(cur_phonemes)
        else:
            syllables.append(cur_syllable)
            cur_syllable = Syllable(cur.char + cur.diac, ''.join(cur_phonemes))
        i += skip_offset + 1
    return syllables
