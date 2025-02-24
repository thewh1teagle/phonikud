"""
Convert time to words
TODO: fix zeros eg. 22:00
"""

import re

PATTERNS = [
    r"(\d{1,2})([apm]{2})",   # AM/PM format
    r"(\d{1,2}):(\d{2})"       # HH:MM format
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
        if period == 'am' and h == 12:
            h = 0
        elif period == 'pm' and h != 12:
            h += 12
        return f"{convert_to_word(h, 0)}"  # Defaulting to 0 minutes when only hour is provided

    return match.group(0)  # Return original text if the format is not recognized

def convert_to_word(h, m): 
    nums = ["אֶפֶס", "אֶחָד", "שְׁתַּיִם", "שָׁלוֹשׁ", "אַרְבַּע", 
            "חָמֵשׁ", "שֵׁשׁ", "שֶׁבַע", "שְׁמוֹנֶה", "תֵּשַׁע", 
            "עָשָׂר", "אַחַד עֶשְׂרֵה", "שְׁתַּיִם עֶשְׂרֵה", "שְׁלוֹשָׁה עֶשְׂרֵה", 
            "אַרְבַּע עֶשְׂרֵה", "חֲמֵשׁ עֶשְׂרֵה", "שֵׁשׁ עֶשְׂרֵה",  
            "שְׁבַע עֶשְׂרֵה", "שְׁמוֹנֶה עֶשְׂרֵה", "תְּשַׁע עֶשְׂרֵה",  
            "עֶשְׂרִים", "עֶשְׂרִים וְאֶחָד", "עֶשְׂרִים וּשְׁתַּיִם",  
            "עֶשְׂרִים וְשָׁלוֹשׁ", "עֶשְׂרִים וְאַרְבַּע",  
            "עֶשְׂרִים וְחָמֵשׁ", "עֶשְׂרִים וָשֵׁשׁ", "עֶשְׂרִים וְשֶׁבַע", 
            "עֶשְׂרִים וּשְׁמוֹנֶה", "עֶשְׂרִים וְתֵשַׁע"]
  
    if m == 0: 
        return f"{nums[h]} בְּדִיּוּק" 
  
    elif m == 1: 
        return f"דַּקָּה אַחַת אַחֲרֵי {nums[h]}" 
  
    elif m == 59: 
        return f"דַּקָּה אַחַת לִפְנֵי {nums[(h % 12) + 1]}" 
  
    elif m == 15: 
        return f"רֶבַע אַחֲרֵי {nums[h]}" 
  
    elif m == 30: 
        return f"חֵצִי אַחֲרֵי {nums[h]}" 
  
    elif m == 45: 
        return f"רֶבַע לִפְנֵי {nums[(h % 12) + 1]}" 
  
    elif m <= 30: 
        return f"{nums[m]} דַּקּוֹת אַחֲרֵי {nums[h]}" 
  
    elif m > 30: 
        return f"{nums[60 - m]} דַּקּוֹת לִפְנֵי {nums[(h % 12) + 1]}" 

def time_to_word(text: str):
    return re.sub('|'.join(PATTERNS), extract_time, text)
