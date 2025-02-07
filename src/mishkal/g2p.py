"""
See https://ipa-reader.com/
"""

from .rules import RULES_MAP, REGEX_RULES, REPLACE_MAP
from mishkal import expand
import re
from mishkal import normalize

def apply_regex(text: str) -> str:
    for rule in  REGEX_RULES:    
        if re.search(rule['src'], text):  # Check if there is a match
            print(f"[regex]: {rule['src']} | {rule['dst']} | {rule['reason']}")
            print(f"[regex] before: {text}")
            new_text = re.sub(rule['src'], rule['dst'], text)
            print(f"[regex] after: {new_text}\n")
            text = new_text  # Apply the change only after previewing
    return text

def g2p(text: str) -> str:    
    text = expand.expand(text)
    # normalize
    text = normalize.normailze(text)
    # Split text into words based on whitespace
    words = text.split()    
    
    result = []
    for word in words:
        word = word.strip()
        
        # handle .regex
        word = apply_regex(word)
        
    
        # handle .replace
        for src, dst in REPLACE_MAP.items():
            word = word.replace(src, dst)
        
        i = 0
        word_result = []
        
        while i < len(word):
            matched = False
            
            # Try all possible substring lengths from longest to shortest
            for length in range(len(word), 0, -1):
                if i + length <= len(word) and word[i:i+length] in RULES_MAP:
                    print(f'Match on {word[i:i+length]} => {RULES_MAP[word[i:i+length]]}')
                    word_result.append(RULES_MAP[word[i:i+length]])
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
