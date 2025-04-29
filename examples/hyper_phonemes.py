"""
uv run  examples/hyper_phonemes.py
"""

from mishkal import phonemize

text = """
שָׁל֫וֹם לְכֻלָּ֫ם! הַיּ֫וֹם נִלְמַ֫ד אַנְגְּלִ֫ית:
[hello](/hɛˈloʊ/) [world](/wɜːrld/)
[אנציקלופדיה](/ʔantsikloˈpedja/)
"""

phonemes = phonemize(
    text,
    preserve_punctuation=True,
    preserve_stress=True,
    use_expander=True,
    use_post_normalize=True,  # For TTS
    predict_stress=False,
    predict_shva_nah=False,
)
print(phonemes)
