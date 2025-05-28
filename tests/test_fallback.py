from phonikud import phonemize


def test_fallback():
    def fallback(text: str):
        return "world"

    assert phonemize("hello", fallback=fallback) == "world"


test_fallback()
