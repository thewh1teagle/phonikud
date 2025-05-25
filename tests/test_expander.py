from kolani.expander import Expander
from kolani.utils import remove_nikud


def test_numbers():
    expander = Expander()
    text = expander.expand_text("35")
    assert "שלושים" in remove_nikud(text)
