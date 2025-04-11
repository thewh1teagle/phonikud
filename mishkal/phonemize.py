from mishkal import lexicon
from .expander import Expander
from mishkal.utils import get_letters, normalize, post_normalize, has_vowel, has_constant, remove_nikud, get_syllables
from typing import Callable
import regex as re
from mishkal.hebrew import phonemize_hebrew

ENGLISH_PHONEMES = set() # When using fallback

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
        predict_stress=False,
        predict_shva_nah=False,
        fallback: Callable[[str], str] = None,
    ) -> str | list[str]:
        # normalize
        text = normalize(text)
        
        
        # TODO: is that enough? what if there's punctuation around? other chars?
        
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
                ENGLISH_PHONEMES.add(c)
            return phonemes

        if fallback is not None:
            text = re.sub(fallback_pattern, fallback_replace_callback, text)
        if use_expander:
            text = self.expander.expand_text(text)
        self.fallback = fallback

        def heb_replace_callback(match: re.Match):
            word = match.group(0)

            word = normalize(word)
            letters: list[Letter] = get_letters(word)
            phonemes: list[str] = phonemize_hebrew(letters, predict_shva_na=predict_shva_nah)
            syllables = get_syllables(phonemes)

            phonemes_text = ''.join(phonemes)
            if predict_stress and lexicon.STRESS not in phonemes_text and syllables:
                if any(remove_nikud(word).endswith(i) for i in lexicon.MILHEL_PATTERNS):
                    # insert lexicon.STRESS in the first character of syllables[-2]
                    syllables[-2] = lexicon.STRESS + syllables[-2]
                else:
                    # insert in syllables[-1]
                    syllables[-1] = lexicon.STRESS + syllables[-1]

            phonemes = ''.join(syllables)
            if use_post_normalize:
                phonemes = post_normalize(phonemes)
            
            return phonemes


        text = re.sub(lexicon.HE_PATTERN, heb_replace_callback, text)

        if not preserve_punctuation:
            text = "".join(i for i in text if i not in lexicon.PUNCTUATION or i == " ")
        if not preserve_stress:
            text = "".join(
                i for i in text if i not in [lexicon.STRESS]
            )

        def expand_hyper_phonemes(text: str):
            """
            Expand hyper phonemes into normal phonemes
            eg. [hello](/hɛˈloʊ/) -> hɛˈloʊ
            """
            def hyper_phonemes_callback(match: re.Match):
                matched_phonemes = match.group(2)
                # for c in matched_phonemes:
                #     lexicon.SET_OUTPUT_CHARACTERS.add(c)
                return matched_phonemes  # The phoneme is in the second group

            text = re.sub(r"\[(.+?)\]\(\/(.+?)\/\)", hyper_phonemes_callback, text)
            return text

        text = expand_hyper_phonemes(text)

        if use_post_normalize:
            text = ''.join(i for i in text if i in lexicon.SET_PHONEMES or i in ENGLISH_PHONEMES or i == ' ')

        return text
