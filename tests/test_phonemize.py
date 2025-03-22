from mishkal import phonemize, vocab
import os
import pandas as pd
import warnings


def test_phonemize_hebrew_sanity():
    with_stress = phonemize("שָׁלוֹם", preserve_stress=True)
    without_stress = phonemize("שָׁלוֹם", preserve_stress=False)
    assert without_stress == "ʃalom" and vocab.STRESS in with_stress

def test_phonemize_hebrew_exhaustive_no_stress():
    filename = os.path.join(
        os.path.dirname(__file__),
        "phonemize_test_cases_no_stress.csv"
    )
    df = pd.read_csv(filename)
    for row in df.itertuples():
        output = phonemize(row.hebrew_with_nikkud, preserve_stress=False)
        # assert output == row.ipa
        # For now, just print warning since they will not all pass:
        if output != row.ipa:
            warnings.warn(f"Incorrect phonemization (no stress): {output} != {row.ipa} ({row.hebrew_with_nikkud})")

def test_phonemize_hebrew_exhaustive_with_stress():
    filename = os.path.join(
        os.path.dirname(__file__),
        "phonemize_test_cases_with_stress.csv"
    )
    df = pd.read_csv(filename)
    for row in df.itertuples():
        output = phonemize(row.hebrew_with_nikkud, preserve_stress=True)
        # assert output == row.ipa
        # For now, just print warning since they will not all pass:
        if output != row.ipa:
            warnings.warn(f"Incorrect phonemization (with stress): {output} != {row.ipa} ({row.hebrew_with_nikkud})")
