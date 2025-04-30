"""
uv run  examples/hyper_phonemes.py
"""

from mishkal import phonemize

text = """
שָׁל֫וֹם לְכֻלָּ֫ם! הַיּ֫וֹם נִלְמַ֫ד אַנְגְּלִ֫ית:
[hello](/hɛˈloʊ/) [world](/wɜːrld/)
[אנציקלופדיה](/ʔantsikloˈpedja/)
"""

phonemes = phonemize(text)
print(phonemes)
