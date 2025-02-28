from mishkal import phonemize, vocab


def test_phonemize_hebrew():
    with_stress = phonemize("שָׁלוֹם", preserve_stress=True)
    without_stress = phonemize("שָׁלוֹם", preserve_stress=False)
    assert without_stress == "ʃalom" and vocab.STRESS in with_stress
