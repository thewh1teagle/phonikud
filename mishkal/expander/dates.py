from datetime import datetime
from .numbers import num_to_word

# Mapping of month names in Hebrew with diacritics (Gregorian months)
MONTHS = {
    1: 'יָנוּאָר',
    2: 'פֶבְרוּאָר',
    3: 'מֵרְץ',
    4: 'אֵפְרִיל',
    5: 'מַאי',
    6: 'יוּנִי',
    7: 'יוּלִי',
    8: 'אוֹגֻסְט',
    9: 'סֶפְּטֶמְבֶּר',
    10: 'אוֹקְטוֹבֶּר',
    11: 'נוֹבֶמְבֶּר',
    12: 'דֶּצֶמְבֶּר'
}

# Mapping of day names in Hebrew with diacritics
DAYS = {
    0: 'יוֹם רִאשׁוֹן',
    1: 'יוֹם שֵׁנִי',
    2: 'יוֹם שְׁלִישִׁי',
    3: 'יוֹם רֵבִיעִי',
    4: 'יוֹם חֲמִישִׁי',
    5: 'יוֹם שִׁישִׁי',
    6: 'יוֹם שַׁבָּת'
}

def date_to_word(word: str, include_day_name = False) -> str:
    """
    Converts a given date string in formats (YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD) to Hebrew date format with diacritics.
    Returns the original word if it's not a valid date.
    """
    separators = ['-', '.', '/']
    orders = [('%Y', '%m', '%d'), ('%d', '%m', '%Y')]
    date_formats = [sep.join(order) for order in orders for sep in separators]

    for date_format in date_formats:
        try:
            # Try parsing the word with each date format
            date_obj = datetime.strptime(word, date_format)
            
            
            # Get the Hebrew day name with diacritics
            day_name = DAYS[date_obj.weekday()]
            
            # Convert month to Hebrew name with diacritics
            month_name = MONTHS[date_obj.month]
            day = num_to_word(str(date_obj.day))
            year = num_to_word(str(date_obj.year))
        
            text = f"{day} בֵּ{month_name} {year}"
            if include_day_name:
                text = f'{day_name}, {text}'
            return text
        except ValueError:
            continue
    return word