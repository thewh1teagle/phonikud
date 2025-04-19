"""
uv pip install phonemizer-fork espeakng-loader
uv run examples/with_fallback.py
"""

from phonemizer.backend.espeak.wrapper import EspeakWrapper
import phonemizer
import espeakng_loader
import mishkal

EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())


def fallback(text: str) -> str:
    """
    Make sure to return valid IPA phonemes and punctuation here
    """
    return phonemizer.phonemize(text)


text = """
מֵרְאִיָּה מְמֻחְשֶׁבֶת עַד Large Language Models: הֵרָשְׁמוּ לְמַחֲזוֹר הֶחָדָשׁ שֶׁל קוּרְס פִּתּוּחַ AI וְ-Deep Learning
"""

phonemes = mishkal.phonemize(
    text, preserve_punctuation=True, preserve_stress=True, fallback=fallback
)
print(phonemes)
