"""
uv run pytest tests/test_syllables.py
"""

import pandas as pd
from mishkal.syllables import add_stress, sort_diacritics
from pathlib import Path

base_path = Path(__file__).parent / "syllables_test_tables"
second_filename = base_path / "second.csv"
third_filename = base_path / "third.csv"

STRESS = "\u05ab"
DAGESH = "\u05bc"


def check_syllables(filename, stress_index: int):
    df = pd.read_csv(filename)
    for row in df.itertuples():
        src_word = sort_diacritics(row.word)
        src_word = src_word.replace(DAGESH, "")
        src_without_stress = src_word.replace(STRESS, "")
        dst_with_stress = add_stress(src_without_stress, stress_index)

        dst_with_stress = sort_diacritics(dst_with_stress)
        assert dst_with_stress == src_word, (
            f"{row.word.encode('unicode_escape')} != {dst_with_stress.encode('unicode_escape')}"
        )


def test_syllables():
    check_syllables(second_filename, -2)
    check_syllables(third_filename, -3)
