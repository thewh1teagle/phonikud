from mishkal import lexicon, phonemize
from pathlib import Path
import pandas as pd
import warnings
from mishkal.lexicon import STRESS

TEST_STRESS = False


def test_phonemize_hebrew_sanity():
    with_stress = phonemize("שָׁ֫לוֹם", preserve_stress=True)
    without_stress = phonemize("שָׁ֫לוֹם", preserve_stress=False)
    assert without_stress == "ʃalom" and lexicon.STRESS in with_stress


def test_phonemize_hebrew_manual():
    def test_file(basename, warn_only=False):
        filename = str(Path(__file__).parent / basename)
        df = pd.read_csv(filename)

        def check_output(
            nikkud, ipa, using_stress, use_post_normalize=True, use_expander=True
        ):
            output = phonemize(
                nikkud,
                preserve_stress=using_stress,
                use_post_normalize=use_post_normalize,
                use_expander=use_expander,
            )
            x, y = ipa, output
            if not using_stress:
                x = x.replace(STRESS, "")
                y = y.replace(STRESS, "")
            parenthetical = "" if using_stress else "; no stress"
            if warn_only:
                if x != y:
                    warnings.warn(
                        f"Incorrect phonemization: {x} != {y} ({nikkud}{parenthetical})"
                    )
            else:
                assert x == y, (
                    f"Incorrect phonemization: {x} != {y} ({nikkud}{parenthetical})"
                )

        def check_pair(nikkud, ipa):
            has_stress = STRESS in row.ipa
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

    test_file("phonemize_test_tables/basic.csv")
    test_file("phonemize_test_tables/advanced.csv", warn_only=True)


def test_phonemize_hebrew_sentences():
    pass
