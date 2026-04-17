from phonikud.expander.time_to_word import time_to_word
from phonikud.utils import remove_nikud


def test_exact_hours():
    # 10:00 -> "עשר" (hours[10] = "עֵ֫שֵׂר")
    assert "עשר" in remove_nikud(time_to_word("10:00"))
    # 00:00 -> "שתים עשרה" (0 -> 12)
    assert "שתים עשרה" in remove_nikud(time_to_word("00:00"))


def test_minutes_single_digit():
    # 10:05 -> "עשר וחמש דקות"
    # hours[10] + " ו" + hours[5] + " דקות"
    result = remove_nikud(time_to_word("10:05"))
    assert "עשר וחמש דקות" in result


def test_minutes_two_special():
    # 10:02 -> "עשר ושתי דקות" (uses 'shtey')
    result = remove_nikud(time_to_word("10:02"))
    assert "עשר ושתי דקות" in result


def test_minutes_teens():
    # 10:15 -> "עשר וחמש עשרה דקות"
    # ten_to_twenty[15-10 = 5] -> "חֲמֵשׁ עֶשְׂרֵה"
    result = remove_nikud(time_to_word("10:15"))
    assert "עשר וחמש עשרה דקות" in result


def test_minutes_tens():
    # 10:20 -> "עשר ועשרים דקות"
    # tens[2] -> "עֶשְׂרִים"
    result = remove_nikud(time_to_word("10:20"))
    assert "עשר ועשרים דקות" in result


def test_minutes_complex():
    # 10:35 -> "עשר ושלושים וחמש דקות"
    # tens[3] (30) + units[5] (5)
    result = remove_nikud(time_to_word("10:35"))
    assert "עשר ושלושים וחמש דקות" in result


def test_am_pm_formats():
    # 10am -> 10:00
    assert "עשר" in remove_nikud(time_to_word("10am"))

    # 1pm -> 13:00 -> (13-12=1) -> 1:00 -> "אחת"
    # hours[1] = "אַחַת"
    assert "אחת" in remove_nikud(time_to_word("1pm"))

    # 12am -> 0:00 -> 12:00 -> "שתים עשרה"
    assert "שתים עשרה" in remove_nikud(time_to_word("12am"))

    # 12pm -> 12:00 -> "שתים עשרה"
    assert "שתים עשרה" in remove_nikud(time_to_word("12pm"))


def test_embedded_text():
    text = "Meeting at 10:30 today"
    expanded = remove_nikud(time_to_word(text))
    assert "Meeting at עשר ושלושים דקות today" in expanded
