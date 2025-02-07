import num2words
import re
from .utils import remove_niqqud

def expand(text: str) -> str:
    result = []
    
    # Split text by spaces
    for word in text.split():
        word = word.strip()

        # Check if word contains digits and non-digits
        if any(char.isdigit() for char in word):
            # Find all digits and non-digits in the word using regex
            number_part = re.findall(r'\d+', word)
            non_number_part = re.findall(r'\D+', word)
            
            if number_part:
                number_text = num2words.num2words(number_part[0], lang='he')
                if number_text[0] == 'ו':
                    # if any word starts with ו replace with vav with shva ('וֵ')
                    number_text[0] = 'וֵ'
                # Combine the number words with the non-digit part (e.g., "$")
                
                result.append(number_text + ' ' + ''.join(non_number_part))
            else:
                result.append(word)  # if no number, just append the word as is
        else:
            result.append(word)  # if no digits, just append the word as is
    text = ' '.join(result)
    return text