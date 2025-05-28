"""
Convert time to words
TODO: fix zeros eg. 22:00
"""

import re

PATTERNS = [
    r"(\d{1,2})([apm]{2})",  # AM/PM format
    r"(\d{1,2}):(\d{2})",  # HH:MM format
]


def extract_time(match):
    """
    Extract hour and minute from a string in HH:MM or AM/PM format
    and return as integers.
    """
    time_str = match.group(0).lower().strip()

    # Check for HH:MM format
    match = re.match(r"(\d{1,2}):(\d{2})", time_str)
    if match:
        h = int(match.group(1))
        m = int(match.group(2))
        return f"{convert_to_word(h, m)}"

    # Check for AM/PM format
    match = re.match(r"(\d{1,2})([apm]{2})", time_str)
    if match:
        h = int(match.group(1))
        period = match.group(2)

        # Normalize to 24-hour format
        if period == "am" and h == 12:
            h = 0
        elif period == "pm" and h != 12:
            h += 12
        return f"{convert_to_word(h, 0)}"  # Defaulting to 0 minutes when only hour is provided

    return match.group(0)  # Return original text if the format is not recognized


def convert_to_word(h, m):
    hours = [
        "אֶפֶס",
        "אַחַת",
        "שְׁנַיִם",  # Will be replaced with "שֵׁנִי" when needed
        "שָׁלוֹשׁ",
        "אַ֫רְבַּע",
        "חָמֵשׁ",
        "שֵׁשׁ",
        "שֶׁ֫בַע",
        "שְׁמ֫וֹנֵה",
        "תֵּ֫שַׁע",
        "עֵ֫שֵׂר",
        "אַחַת עֶשְׂרֵה",
        "שְׁתֵּים עֶשְׂרֵה",
    ]

    tens = ["", "עֵשֵׂר", "עֶשְׂרִים", "שְׁלוֹשִׁים", "אַרְבָּעִים", "חֲמִשִּׁים"]

    ten_to_twenty = [
        "עֵ֫שֵׂר",
        "אַחַת עֶשְׂרֵה",
        "שְׁתֵּים עֶשְׂרֵה",
        "שְׁלוֹשׁ עֶשְׂרֵה",
        "אַרְבַּע עֶשְׂרֵה",
        "חֲמֵשׁ עֶשְׂרֵה",
        "שֵׁשׁ עֶשְׂרֵה",
        "שְׁבַע עֶשְׂרֵה",
        "שְׁמוֹנֶה עֶשְׂרֵה",
        "תְּשַׁע עֶשְׂרֵה",
    ]

    vocab = {"minutes": "דַּקּוֹת", "and": "וֵ", "shtey": "שְׁתֵּי"}

    # Convert 0 hours to 12 (midnight)
    if h == 0:
        h = 12

    elif h > 12:
        h -= 12

    if m == 0:
        return f"{hours[h]}"

    elif 1 <= m <= 9:
        minute_word = (
            vocab["shtey"] if m == 2 else hours[m]
        )  # Replace "שניים" with "שני"
        return f"{hours[h]} {vocab['and']}{minute_word} {vocab['minutes']}"

    elif 10 <= m <= 19:
        return f"{hours[h]} {vocab['and']}{ten_to_twenty[m - 10]} {vocab['minutes']}"

    else:
        tens_part = f"{vocab['and']}{tens[m // 10]}"
        units_part = f"{vocab['and']}{hours[m % 10]}" if m % 10 != 0 else ""
        return f"{hours[h]} {tens_part} {units_part} {vocab['minutes']}".strip()


def time_to_word(text: str):
    return re.sub("|".join(PATTERNS), extract_time, text)
