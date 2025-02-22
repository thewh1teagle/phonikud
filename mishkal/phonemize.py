"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

Early rules:
1. Niqqud malle vowels
2. Dagesh (custom beged kefet)
3. Final letter without niqqud
4. Final Het gnuva
5. Geresh (Gimel, Ttadik, Zain)
6. Shva nax and na
Revised rules:
1. Consonants
2. Niqqud

Reference:
- https://hebrew-academy.org.il/2020/08/11/איך-הוגים-את-השווא-הנע
- https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
- https://en.wikipedia.org/wiki/Help:IPA/Hebrew
"""

from .vocab import LETTERS_NAMES_PHONEMES, Letter, Token
from mishkal import vocab, utils
from .expander import Expander
import unicodedata


class Phonemizer():
    def __init__(self):
        self.expander = Expander()
        
    def normalize(self, text: str) -> str:
        # Decompose text
        text = unicodedata.normalize('NFD', text)
        # Normalize niqqud
        for k, v in vocab.NIQQUD_NORMALIZE.items():
            text = text.replace(k, v)
        
        # Normalize letters
        for k, v in vocab.LETTERS_NORMALIZE.items():
            text = text.replace(k, v)
        
        # Keep only lexicon characters
        text = ''.join([c for c in text if c in vocab.SET_INPUT_CHARACTERS or c in vocab.SET_OUTPUT_CHARACTERS])
        return text
        
    def phonemize(self, text: str, preserve_punctuation = True, return_tokens = True) -> str | list[Token]:
        text = self.expander.expand_text(text)
        text = self.normalize(text)
        tokens: list[Token] = []
        word = ''
        index = 0
        
        while index < len(text):
            cur = text[index]
            
            # Collect word
            if cur in vocab.SET_LETTERS or cur in vocab.SET_NIQQUD or cur == "'":
                # Add to word
                word += cur
                index += 1
                continue
            # Phonemize word
            if len(word) > 0:
                
                # Phonemize word
                letters = utils.extract_letters(word)
                hebrew_tokens = self.phonemize_hebrew(letters)
                tokens.extend(hebrew_tokens)
                word = ''

            # Add punctuation
            if cur in vocab.SET_PUNCTUATION:
                if preserve_punctuation or cur == ' ':
                    tokens.append(Token(cur, cur))
                index += 1
            else:
                # Valid phoneme
                if cur in vocab.SET_OUTPUT_CHARACTERS:
                    tokens.append(Token(cur, cur))
                    index += 1
                else:
                    # Ignore
                    index += 1
                
        # Ensure the last accumulated word is phonemized
        if len(word) > 0:
            letters = utils.extract_letters(word)            
            hebrew_tokens = self.phonemize_hebrew(letters)
            tokens.extend(hebrew_tokens)
        
        if return_tokens:
            return tokens
        return ''.join([t.phonemes for t in tokens])
    
    def phonemize_hebrew(self, letters: list[Letter]) -> list[Token]:
        tokens: list[Token] = []
        i = 0
        while i < len(letters):
            cur = letters[i]
            prev = letters[i-1] if i > 0 else None
            next = letters[i+1] if i < len(letters)-1 else None
                        
            # early rules
            
            # Single letter name
            if not next and not prev and cur and not cur.symbols:
                token = Token(cur.as_str(), LETTERS_NAMES_PHONEMES.get(cur.letter_str, ''))
                tokens.append(token)
                i += 1
                continue
            
            # Vav vowel
            if not cur.symbols and next: # maybe with dagesh
                if next == 'ו':
                    phoneme = vocab.LETTERS_PHONEMES.get(cur.letter_str, '')
                    if '\u05BC' in next.symbols: # Dagesh
                        phoneme += vocab.VOWEL_U
                    elif '\u05B9' in next.symbols: # Holam
                        phoneme += vocab.VOWEL_O
                    elif '\u05BA' in next.symbols: # Holam haser for vav
                        phoneme += vocab.VOWEL_O
                    else:
                        phoneme += vocab.VOWEL_O # default
                    token = Token(cur.as_str() + next.as_str(), phoneme)
                    tokens.append(token)
                    i += 2
                    continue
            # Yod vowel
            if cur == 'י' and prev and not cur.symbols: # Yod without niqqud
                if not prev.symbols:
                    phoneme = vocab.VOWEL_I
                    token = Token(prev.as_str() + cur.as_str(), phoneme)
                    tokens.append(token)
                    i += 1
                    continue
                elif '\u05B4' in prev.symbols: # Hirik
                    phoneme = ''
                    token = Token(cur.as_str(), phoneme)
                    tokens.append(token)
                    i += 1
                    continue
            # Some final letters can be silent
            if not next and cur.letter_str in 'אהע' and not cur.symbols:
                phoneme = ''
                token = Token(cur.as_str(), phoneme)
                tokens.append(token)
                i += 1
                continue
            # Het gnuva
            if not next and cur == 'ח' and '\u05B7' in cur.symbols: # Patah
                phoneme = vocab.HET_GNUVA
                token = Token(cur.as_str(), phoneme)
                tokens.append(token)
                i += 1
                continue
            
            # Geresh
            if "'" in cur.symbols and cur.letter_str in ['ג', 'ז', 'צ']: 
                phoneme = (
                    vocab.GIMEL_OR_ZAIN_WITH_DAGESH if cur.letter_str in ['ג', 'ז'] 
                    else vocab.TSADIK_WITH_DAGESH
                )
                phoneme += ''.join([vocab.NIQQUD_PHONEMES.get(niqqud, '') for niqqud in cur.symbols])
                token = Token(cur.as_str() + (next.as_str() if next else ''), phoneme)
                tokens.append(token)
                i += 1
                continue  
            
            # Shva nax and na
            if '\u05B0' in cur.symbols:
                phoneme = vocab.LETTERS_PHONEMES.get(cur.letter_str, '')
                # First
                if not prev:
                    if cur.letter_str == 'ו':
                        phoneme += vocab.VOWEL_E
                    elif cur.letter_str in 'למנרי':
                        phoneme += vocab.VOWEL_E
                    elif next and next.letter_str in 'אהע': # Groni
                        phoneme += vocab.VOWEL_E
                # Middle
                else:
                    # After vav with dagesh nax
                    if prev and prev.letter_str == 'ו' and '\u05BC' in prev.symbols:
                        phoneme += '' 
                    # Double final shva(s) nax
                    elif i == len(letters) - 1 and prev and '\u05B0' in prev.symbols:
                        phoneme += ''
                    elif i == len(letters) - 1 and next and '\u05B0' in next.symbols:
                        phoneme += ''
                    # Double shva same letter
                    elif next and next.letter_str == cur.letter_str:
                        phoneme += vocab.VOWEL_E
                    # Double shva
                    elif next and '\u05B0' in next.symbols:
                        phoneme += ''
                    # Previous nax
                    elif tokens:
                        if '\u05B0' in prev.symbols and not tokens[-1].phonemes.endswith(vocab.VOWEL_E):
                            phoneme += vocab.VOWEL_E
                token = Token(cur.letter_str, phoneme)
                tokens.append(token)
                i += 1
                continue
                    
                
            # revised rules
            phoneme = vocab.LETTERS_PHONEMES.get(cur.letter_str, '')
            phoneme += ''.join([vocab.NIQQUD_PHONEMES.get(niqqud, '') for niqqud in cur.symbols])
            token = Token(cur.letter_str, phoneme)
            tokens.append(token)
            i += 1
        return tokens

