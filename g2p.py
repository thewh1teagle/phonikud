from rules import RULES_MAP
import unicodedata
import num2words
import expand

def g2p(text: str) -> str:    
    # normalize
    text = unicodedata.normalize('NFC', text)
    text = expand.expand(text)
    result = []
    
    # Split text into words based on whitespace
    words = text.split()
    
    for word in words:
        word = word.strip()
        
        i = 0
        word_result = []
        
        while i < len(word):
            matched = False
            
            # Try all possible substring lengths from longest to shortest
            for length in range(len(word), 0, -1):
                if i + length <= len(word) and word[i:i+length] in RULES_MAP:
                    word_result.append(RULES_MAP[word[i:i+length]])
                    print(f'Match on {word[i:i+length]}')
                    i += length
                    matched = True
                    break
            
            if not matched:
                print(f'Not matched on {word[i]}')
                word_result.append(word[i])  # For characters not in the map
                i += 1
        
        result.append(''.join(word_result))
    
    # Join all the words back together
    return ' '.join(result)
