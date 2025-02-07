from mishkal.rules import RULES_MAP
from mishkal.utils import get_diacritized_letters

DAGESH = chr(0x05BC)


def test_dagesh_in_end_of_rules():
    failed_cases = []
    print('h!!!!!!!!!!!!!i')
    for key, value in RULES_MAP.items():
        letters = get_diacritized_letters(key)
        for letter in letters:
            if DAGESH in letter and letter[-1] != DAGESH:
                failed_cases.append(key)
    assert not failed_cases, f"Keys failing the DAGESH rule: {failed_cases}"

test_dagesh_in_end_of_rules()