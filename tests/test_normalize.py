from mishkal import normalize
from mishkal.utils import get_unicode_names


def test_dagesh_should_come_first():
    words = {
        "\u05d1\u05b9\u05bc": "\u05d1\u05bc\u05b9",  # flip dagesh (3) with holam (2)
        "בַּ": "בַּ",  # flip dagesh withp patah
        "בַּרִיא וֵחַזַק1": "בַּרִיא וֵחַזַק",  # should remove number
        "כֹּל": "כֹּל",  # order dagesh
    }
    for invalid, correct in words.items():
        assert invalid != correct  # Make sure it's really different
        assert normalize(invalid) == correct, (
            f"{correct, get_unicode_names(invalid)}, {get_unicode_names(correct)}"
        )
