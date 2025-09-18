from phonikud import lexicon, phonemize_fst
from pathlib import Path
import pandas as pd
import warnings
from phonikud.lexicon import STRESS_PHONEME

TEST_STRESS = True


def run_phoneme_check(
    nikkud, expected_ipa, using_stress, *, filename, line_number, warn_only
):
    output = phonemize_fst(
        nikkud,
    )
    ref = expected_ipa
    if not using_stress:
        ref = ref.replace(STRESS_PHONEME, "")
        output = output.replace(STRESS_PHONEME, "")

    msg = f"Incorrect phonemization: {ref} != {output} ({nikkud}; {'with' if using_stress else 'no'} stress) FILE {filename} LINE {line_number}"

    if warn_only and ref != output:
        warnings.warn(msg)
    elif not warn_only:
        assert ref == output, msg


def check_file(filename: str, warn_only=False):
    df = pd.read_csv(filename)
    for line_number, row in enumerate(df.itertuples()):
        nikkud_forms = [row.hebrew_with_nikkud]
        # handle Hebrew punctuation variants
        nikkud_forms += (
            [
                row.hebrew_with_nikkud.replace('"', "״"),
                row.hebrew_with_nikkud.replace("'", "׳"),
            ]
            if any(c in row.hebrew_with_nikkud for c in ['"', "'"])
            else []
        )

        for nikkud in nikkud_forms:
            run_phoneme_check(
                nikkud,
                row.ipa,
                using_stress=TEST_STRESS and STRESS_PHONEME in row.ipa,
                filename=filename,
                line_number=line_number,
                warn_only=warn_only,
            )


def test_phonemize_hebrew_manual():
    base = Path(__file__).parent / "phonemize_test_tables"
    check_file(base / "basic1.csv")
    # check_file(base / "dictionary.csv")
    # check_file(base / "advanced.csv", warn_only=True)
