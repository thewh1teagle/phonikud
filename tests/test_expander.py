from mishkal.expander import Expander
from mishkal.utils import remove_nikud


def test_numbers():
    expander = Expander()
    text = expander.expand_text("35")
    assert "שלושים" in remove_nikud(text)
