from phonikud import lexicon
from phonikud.hebrew import Letter
from .expander import Expander
from phonikud.utils import (
    get_letters,
    normalize,
    post_normalize,
    post_clean,
    add_milra_hatama,
    mark_vocal_shva,
    sort_hatama,
)
from typing import Callable, Literal
import regex as re
from phonikud.hebrew import phonemize_word


class Phonemizer:
    # TODO: is that enough? what if there's punctuation around? other chars?
    fallback_pattern = r"[a-zA-Z]+"

    def __init__(self):
        self.expander = Expander()

    def phonemize(
        self,
        text: str,
        preserve_punctuation: bool,
        preserve_stress: bool,
        use_expander: bool,
        use_post_normalize: bool,  # For TTS
        predict_stress: bool,
        predict_vocal_shva: bool,
        schema: Literal["plain", "modern"],
        fallback: Callable[[str], str] = None,
    ) -> str | list[str]:
        # normalize
        text = normalize(text)

        def fallback_replace_callback(match: re.Match):
            word = match.group(0)

            if self.expander.dictionary.dict.get(word):
                # skip
                # TODO: better API
                return word
            phonemes = fallback(word).strip()
            # TODO: check that it has only IPA?!
            for c in phonemes:
                lexicon.ADDITIONAL_PHONEMES.add(c)
            return phonemes

        if fallback is not None:
            text = re.sub(self.fallback_pattern, fallback_replace_callback, text)

        if use_expander:
            text = self.expander.expand_text(text)

        def heb_replace_callback(match: re.Match, original_text: str):
            word = match.group(0)
            start_offset = match.start()
            if start_offset > 0 and original_text[start_offset - 1] == "[":
                # Skip if it starts with [ as it's used for hyper phonemes
                return word

            if predict_vocal_shva:
                mark_vocal_shva(word)
            if lexicon.HATAMA_DIACRITIC not in word and predict_stress:
                word = add_milra_hatama(word)
            letters: list[Letter] = get_letters(word)
            letters = sort_hatama(letters)

            phonemes: list[str] = phonemize_word(
                letters,
            )
            phonemes = "".join(phonemes)
            # syllables = get_syllables(phonemes)

            # phonemes_text = "".join(phonemes)
            # # if predict_stress and lexicon.STRESS not in phonemes_text and syllables:
            # #     if len(syllables) == 1:
            # #         syllables[-1] = lexicon.STRESS + syllables[-1]
            # #         syllables[-1] = "".join(sort_stress(syllables[-1]))
            # #     elif any(
            # #         remove_nikud(word).endswith(i) for i in lexicon.MILHEL_PATTERNS
            # #     ) or phonemes_text.endswith("ax"):
            # #         # insert lexicon.STRESS in the first character of syllables[-2]
            # #         syllables[-2] = lexicon.STRESS + syllables[-2]
            # #         syllables[-2] = "".join(sort_stress(syllables[-2]))
            # #     else:
            # #         # insert in syllables[-1]
            # #         syllables[-1] = lexicon.STRESS + syllables[-1]
            # #         syllables[-1] = "".join(sort_stress(syllables[-1]))

            # phonemes = "".join(syllables)
            if use_post_normalize:
                phonemes = post_normalize(phonemes)

            if schema == "modern":
                # We'll keep this feature simple for now
                for k, v in lexicon.MODERN_SCHEMA.items():
                    phonemes = re.sub(k, v, phonemes)
            return phonemes

        text = re.sub(
            lexicon.HE_PATTERN, lambda match: heb_replace_callback(match, text), text
        )

        def hyper_phonemes_callback(match: re.Match):
            """
            Expand hyper phonemes into normal phonemes
            eg. [hello](/hɛˈloʊ/) -> hɛˈloʊ
            """
            matched_phonemes = match.group(2)
            for c in matched_phonemes:
                lexicon.ADDITIONAL_PHONEMES.add(c)
            return matched_phonemes  # The phoneme is in the second group

        text = re.sub(r"\[(.+?)\]\(\/(.+?)\/\)", hyper_phonemes_callback, text)

        if not preserve_punctuation:
            text = "".join(i for i in text if i not in lexicon.PUNCTUATION or i == " ")
        if not preserve_stress:
            text = "".join(i for i in text if i not in [lexicon.STRESS_PHONEME])
        if use_post_normalize:
            # We don't keep hypens in the output, but we should replace it with space
            text = post_clean(text)
        return text
