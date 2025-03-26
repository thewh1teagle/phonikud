from mishkal import phonemize, vocab
from pathlib import Path
import pandas as pd
import warnings

TEST_STRESS = False


def test_phonemize_hebrew_sanity():
    with_stress = phonemize("שָׁלוֹם", preserve_stress=True)
    without_stress = phonemize("שָׁלוֹם", preserve_stress=False)
    assert without_stress == "ʃalom" and vocab.STRESS in with_stress


def test_phonemize_hebrew_manual():
    UNICODE_STRESS_MARK = chr(712)
    filename = str(Path(__file__).parent / "manual_phonemize_test_cases.csv")
    df = pd.read_csv(filename)

    def check_output(nikkud, ipa, using_stress):
        output = phonemize(nikkud, preserve_stress=using_stress)
        x, y = ipa, output
        if not using_stress:
            x = x.replace(UNICODE_STRESS_MARK, "")
            y = y.replace(UNICODE_STRESS_MARK, "")
        parenthetical = "" if using_stress else "; no stress"
        if x != y:
            warnings.warn(
                f"Incorrect phonemization: {x} != {y} ({nikkud}{parenthetical})"
            )
            # ^TODO: use assert once all tests pass

    def check_pair(nikkud, ipa):
        has_stress = UNICODE_STRESS_MARK in row.ipa
        # ^ if stress is marked manually, check both with and without stress
        # otherwise just check that output is correct disregarding stress

        if TEST_STRESS and has_stress:
            check_output(nikkud, ipa, True)
        check_output(nikkud, ipa, False)

    for row in df.itertuples():
        nikkud_to_check = [row.hebrew_with_nikkud]
        # also test punctuation variants:
        if '"' in row.hebrew_with_nikkud:
            nikkud_to_check.append(row.hebrew_with_nikkud.replace('"', "״"))
        if "'" in row.hebrew_with_nikkud:
            nikkud_to_check.append(row.hebrew_with_nikkud.replace("'", "׳"))
        for nikkud in nikkud_to_check:
            check_pair(nikkud, row.ipa)


def test_phonemize_hebrew_sentences():
    pass
