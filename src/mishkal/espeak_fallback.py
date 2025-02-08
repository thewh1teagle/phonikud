"""
Not used currently. may use it later for English letters and words
"""

from phonemizer.backend.espeak.wrapper import EspeakWrapper
import phonemizer
import espeakng_loader

EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())

def phonemize(text: str) -> str:
    return phonemizer.phonemize(text, language='en-us')