"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

1. Vav vowels in index + 1
2. Yod vowels
3. Dagesh (Bet, Kaf, Kaf sofit, Fey, Fey Sofit), Sin, Shin dots
5. Het in end like Ko(ax)
6. Geresh (Gimel, Ttadik, Tsadik sofit, Zain)
7. Silent He in end with Kamaz / Patah before
8. Kamatz Gadol and Kamatz Katan (Kol VS Kala)
9. Shva Nah and Shva Na

All IPA declared only here with add_phonemes() and in phoneme_table.
"""

from mishkal.variants import Letter, Phoneme
from .lexicon.symbols import LetterSymbol
from .lexicon.letters import Letters
from .phonene_table import PHONEME_TABLE
import unicodedata

def phonemize_letters(letters: list[Letter]) -> list[Phoneme]:
    phonemes: list[Phoneme] = []
    index = 0
    current_word_str = ''.join(i.as_str_with_niqqud() for i in letters)
    
    
    while index < len(letters):
        current_phoneme = Phoneme(phonemes='', word=current_word_str, letter=letters, reasons=[])
        current_letter= letters[index]
        next_letter = letters[index + 1] if index + 1 < len(letters) else None
        previous_letter = letters[index - 1] if index - 1 >= 0 else None
        
        # Vav in middle
        if (
            index > 0 
            and current_letter.as_str() == Letters.VAV  # Vav
            and not previous_letter.plain_niqqud() # No previous niqqud
        ): 
            
            # Vav with no niqqud
            if not current_letter.get_symbols():
                if index == len(letters) - 1:
                    current_phoneme.add_phonemes('v', 'last soft vav without niqqud')    
                    current_phoneme.mark_ready()
                else:
                    current_phoneme.add_phonemes('o', 'Vav without niqqud')
                    current_phoneme.mark_ready()
            # Vav with Holam
            elif current_letter.contains_any_symbol([LetterSymbol.holam, LetterSymbol.holam_haser_for_vav]):
                current_phoneme.add_phonemes('o', 'Vav with Holam')
                current_phoneme.mark_ready()
            
            # Vav with dagesh
            elif current_letter.contains_any_symbol([LetterSymbol.dagesh_or_mapiq]):
                current_phoneme.add_phonemes('u', 'Vav with Dagesh')
                current_phoneme.mark_ready()

        # Vav vowel in start
        if (index == 0 and current_letter.as_str() == Letters.VAV):
            # Vav with dagesh in start as 'u'
            if current_letter.contains_any_symbol([LetterSymbol.dagesh_or_mapiq]):
                current_phoneme.add_phonemes('u', 'Vav with Dagesh')
                current_phoneme.mark_ready()
            
        
        # Yod in middle          
        if (index > 0 and current_letter.as_str() == Letters.YOD):
            if not previous_letter.plain_niqqud(): # No previous niqqud
                current_phoneme.add_phonemes('i', 'yod in middle with no previous niqqud')
                current_phoneme.mark_ready()
            elif previous_letter.contains_any_symbol([LetterSymbol.hiriq]):
                current_phoneme.add_phonemes('', 'yod with previous hirik')
                current_phoneme.mark_ready()
            # One before last
            elif index == len(letters) - 2:
                if next_letter and next_letter.as_str() == Letters.VAV:
                    current_phoneme.add_phonemes('', 'silent yod before last with next vav')
                    current_phoneme.mark_ready()

            
        # Geresh (Gimel, Ttadik, Tsadik sofit, Zain)
        if current_letter.contains_any_symbol([LetterSymbol.geresh, LetterSymbol.geresh_en]):
            if current_letter.as_str()  == Letters.GIMEL:
                current_phoneme.add_phonemes('d͡ʒ', 'Geresh in gimel like girafa')
                current_phoneme.mark_letter_ready()
            if current_letter.as_str() in [Letters.TZADI, Letters.FINAL_TZADI]:
                current_phoneme.add_phonemes('t͡ʃ', 'Geresh in Tsadi ike chita')
                current_phoneme.mark_letter_ready()
            if current_letter.as_str() == Letters.ZAYIN:
                current_phoneme.add_phonemes('ʒ', 'Geresh in Zain like Zargon')
                current_phoneme.mark_letter_ready()
                     
                
        # Silent He in end with Kamaz / Patah before
        if current_letter.as_str() == Letters.HEY and index == len(letters) - 1 and previous_letter and previous_letter.contains_patah_like_sound():
            current_phoneme.add_phonemes('', 'silent he')
            current_phoneme.mark_ready()
            

        # Sin dot
        if current_letter.contains_any_symbol([LetterSymbol.sin_dot]):
            current_phoneme.add_phonemes('s', 'Sin dot')
            current_phoneme.mark_letter_ready()
            
        # Shin dot
        if current_letter.contains_any_symbol([LetterSymbol.shin_dot]):
            current_phoneme.add_phonemes('ʃ', 'Shin dot')
            current_phoneme.mark_letter_ready()
            
        # Dagesh in Vav in start
        if current_letter.contains_all_symbol([LetterSymbol.dagesh_or_mapiq, Letters.VAV]) and index == 0:
            current_phoneme.add_phonemes('u', 'vav with dagesh in start')
            current_phoneme.mark_ready()
        
        # Dagesh (Bet, Kaf, Kaf sofit, Fey, Fey Sofit), 
        if current_letter.contains_any_symbol([LetterSymbol.dagesh_or_mapiq]) and not current_phoneme.is_ready():
            if current_letter.as_str() in [Letters.BET, Letters.KAF, Letters.FINAL_KAF, Letters.PEY, Letters.FINAL_PEY]:
                current_phoneme.add_phonemes({
                    Letters.BET: 'b',
                    Letters.KAF: 'k',
                    Letters.FINAL_KAF: 'k',
                    Letters.PEY: 'p',
                    Letters.FINAL_PEY: 'p',
                }[current_letter.as_str()], f'{current_letter.as_str()} with dagesh')
                current_phoneme.mark_letter_ready()            
            
        # Het in end like Ko(ax)
        if current_letter.as_str() == Letters.CHET and current_letter.contains_any_symbol([LetterSymbol.patah]) and index == len(letters) - 1:
            current_phoneme.add_phonemes('ax', 'word ends with chet with patah')
            current_phoneme.mark_ready()
            
            
        # Base letter
        if not current_phoneme.is_ready() and not current_phoneme.is_letter_ready():
            from_table = PHONEME_TABLE.get(current_letter.as_str(), '')
            current_phoneme.add_phonemes(from_table, f'got letter {current_letter.as_str()} from table')
            
        # Kamatz Gadol and Katan
        if current_letter.contains_patah_like_sound():
            if current_letter.contains_any_symbol([LetterSymbol.hataf_qamats]):
                current_phoneme.add_phonemes('o', 'Hataf segol')
                current_phoneme.mark_ready()
            
        # Shva na and Shva nah
        # https://he.wikipedia.org/wiki/שווא#שווא_נע
        if current_letter.niqqud_is_shva():
            if not next_letter and not previous_letter:
                current_phoneme.add_phonemes('e', 'single letter with shva')
                current_phoneme.mark_ready()

            if next_letter and next_letter.as_str() == current_letter.as_str():  # Ensure there's a previous and next letter
                current_phoneme.add_phonemes('e', 'first shva before identical letter')
                current_phoneme.mark_ready()
            
            # Two last letters has shva
            elif index == len(letters) - 1 or index == len(letters) - 2:
                if len(letters) > 1 and current_letter.niqqud_is_shva() and letters[-2].niqqud_is_shva():
                    current_phoneme.add_phonemes('', 'two shva in end nah both')
                    current_phoneme.mark_ready()
            
            # Contains only shva
            elif index == 0:
                current_phoneme.add_phonemes('e', 'shva in first letter without other diacritics')
                current_phoneme.mark_ready()
                
            elif next_letter and next_letter.niqqud_is_shva():
                current_phoneme.add_phonemes('', 'fiirst shva in sequence')
                current_phoneme.mark_ready()
                
            elif previous_letter.niqqud_is_shva():
                current_phoneme.add_phonemes('e', 'second shva in sequence')
                current_phoneme.mark_ready()
                
            # elif if previous_letter.is_large_vowel() and not previous_letter.is_stressed():
                # current_phoneme.add_phonemes('e', 'shva after large unstressed vowel')
            elif current_letter.niqqud_has_dagesh():
                current_phoneme.add_phonemes('e', 'shva with dagesh')
                current_phoneme.mark_ready()
            
            # Always handled
            current_phoneme.mark_ready()
            
        
        # Symbols
        if not current_phoneme.is_ready():
            for s in current_letter.get_symbols():
                from_table = PHONEME_TABLE.get(s, '')
                symbol_name = unicodedata.name(s, '?')
                current_phoneme.add_phonemes(from_table, f'got symbol {symbol_name} from table')
            
        phonemes.append(current_phoneme)
        index += 1
    print(phonemes)
    return phonemes
