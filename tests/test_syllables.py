"""
uv run pytest tests/test_syllables.py
"""

import pandas as pd
from mishkal.syllables import add_stress, sort_diacritics
from pathlib import Path

base_path = Path(__file__).parent / "syllables_test_tables"
files = base_path.glob("*.csv")

STRESS = "\u05ab"
DAGESH = "\u05bc"


def check_syllables(filename):
    df = pd.read_csv(filename)
    errors = []

    for row in df.itertuples():
        src_word = sort_diacritics(row.word)
        src_word = src_word.replace(DAGESH, "")
        src_without_stress = src_word.replace(STRESS, "")
        dst_with_stress = add_stress(src_without_stress, int(row.stress_index))

        dst_with_stress = sort_diacritics(dst_with_stress)
        if src_word != dst_with_stress:
            errors.append(
                f"{src_word.encode('unicode_escape')} \nVS\n {dst_with_stress.encode('unicode_escape')}\n{src_word} != {dst_with_stress}"
            )
    assert not errors, "\n".join(errors) + f"\nFound {len(errors)} errors\n"


def test_syllables():
    for file in files:
        check_syllables(file)
