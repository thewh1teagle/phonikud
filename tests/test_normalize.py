from mishkal import normalize
from mishkal.expander.dictionary import Dictionary


def test_dagesh_should_come_first():
    words = {
        "\u05d0\u05b9\u05bc": "\u05d0\u05bc\u05b9",  # Flip dagesh (3) with holam (2)
        "בַּ": "בַּ",
        "גְּ": "גְּ",
        "בַּרִיא וֵחַזַק1": "בַּרִיא וֵחַזַק",  # should remove number
        "כֹּל": "כֹּל",
    }
    for invalid, correct in words.items():
        assert invalid != correct  # Make sure it's really different
        assert normalize(invalid) == correct
