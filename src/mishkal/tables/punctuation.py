"""
See https://github.com/python/cpython/blob/c1f352bf0813803bb795b796c16040a5cd4115f2/Lib/string.py#L25
"""

import string

IPA_PUNCTUATION = {
    '!': '',    # Affects prosody, but no IPA equivalent in Hebrew
    '"': '',    # Not used in IPA
    '#': 'sulamit',    # Not used in IPA
    '$': 'dolar',  # Represented as "dollar" in Hebrew
    '%': 'axuz', # Represented as "percent" in Hebrew
    '&': 've',  # Often replaced with "וְ" (ve) in Hebrew pronunciation
    "'": '',    # Hebrew doesn't mark primary stress with apostrophes
    '(': '',    # No IPA equivalent, used for grouping
    ')': '',    # No IPA equivalent
    '*': '',    # Not used in IPA
    '+': 'plus',  # Used to represent "plus" in Hebrew
    ',': 'ˌ',   # Can be used for slight pause
    '-': '',  # Commonly used as "minus" in Hebrew
    '.': '|',   # Marks sentence breaks (not a syllable break in Hebrew)
    '/': '|',   # Alternative sentence or phrase boundary
    ':': '',    # No standard use in Hebrew IPA
    ';': '',    # Not used in IPA
    '<': '',    # Not used in IPA
    '=': '',    # Not used in IPA
    '>': '',    # Not used in IPA
    '?': '',    # Rising intonation, but no direct IPA equivalent for Hebrew
    '@': '',    # Not used in IPA
    '[': '',    # Used for phonetic transcription brackets
    '\\': '',   # Not used in IPA
    ']': '',    # Used for phonetic transcription brackets
    '^': '',    # Not used in IPA
    '_': '',    # Not used in IPA
    '`': '',    # Not used in IPA
    '{': '',    # Not used in IPA
    '|': '|',   # Minor prosodic break
    '}': '',    # Not used in IPA
    '~': '',    # Hebrew does not have nasalized vowels
}


assert string.punctuation in IPA_PUNCTUATION