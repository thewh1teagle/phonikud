"""
The actual letters phonemization happens here.
Phonemes generated based on rules.

1. Vav vowels in index + 1
2. Yod vowels
3. Alef shketa (After Kamatz)
4. Dagesh (Bet, Kaf, Kaf sofit, Fey, Fey Sofit), Sin, Shin dots
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
from .phoneme_table import PHONEME_TABLE
import unicodedata
from mishkal import config

class Phonemizer():

    def phonemize_letters(self, letters: list[Letter]) -> list[Phoneme]:
        phonemes: list[Phoneme] = []
        index = 0
        current_word_str = ''.join(i.as_str_with_niqqud() for i in letters)
        
        
        while index < len(letters):
            current_letter = letters[index]
            current_phoneme = Phoneme(phonemes='', word=current_word_str, letter=current_letter, reasons=[])
            
            next_letter = letters[index + 1] if index + 1 < len(letters) else None
            previous_letter = letters[index - 1] if index - 1 >= 0 else None
            
            # No way to have oo in Hebrew
            if index > 0 and phonemes[-1].phonemes.endswith('o') and current_letter.as_str() == Letters.VAV:
                current_phoneme.add_phonemes('', 'No way to have oo in Hebrew')    
                current_phoneme.mark_ready()
            
            # Vav in middle
            if (
                index > 0 
                and current_letter.as_str() == Letters.VAV  # Vav
                and (not previous_letter.plain_niqqud()) # No previous niqqud
                and not current_phoneme.is_ready()
            ): 
                
                # Vav with no niqqud
                if not current_letter.get_symbols():
                    # Vav soft last
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
                
            
            # Yod in middle as vowel        
            if (
                index > 0 and current_letter.as_str() == Letters.YOD
                and current_letter.is_silent()
            ):
                if not previous_letter.plain_niqqud(): # No previous niqqud
                    current_phoneme.add_phonemes('i', 'Yod in middle with no previous niqqud')
                    current_phoneme.mark_ready()
                elif previous_letter.contains_any_symbol([LetterSymbol.hiriq]):
                    current_phoneme.add_phonemes('', 'Yod with previous hirik')
                    current_phoneme.mark_ready()
                # One before last
                elif index == len(letters) - 2:
                    if (
                        next_letter and next_letter.as_str() == Letters.VAV 
                        # Keep j if next is vav with dagesh
                        and LetterSymbol.dagesh_or_mapiq not in next_letter.symbols
                    ):
                        current_phoneme.add_phonemes('', 'Silent yod before last with next vav')
                        current_phoneme.mark_ready()

            # Alef with previous Kamatz sound without niqqud
            if current_letter.as_str() == Letters.ALEF and not current_letter.plain_niqqud():
                if previous_letter and previous_letter.contains_patah_like_sound():
                    current_phoneme.add_phonemes('', 'Silent alef without niqqud after Kamatz like sound')
                    current_phoneme.mark_ready()
                elif index == len(letters) - 2: # two before end
                    current_phoneme.add_phonemes('', 'Silent alef without niqqud before end')
                    current_phoneme.mark_ready()
                elif index == len(letters) - 1: # two before end
                    current_phoneme.add_phonemes('', 'Silent alef without niqqud in end')
                    current_phoneme.mark_ready()
            # Alef with Kamatz like niqqud
            if current_letter.as_str() == Letters.ALEF and current_letter.contains_patah_like_sound():
                current_phoneme.add_phonemes('', 'Alef already contains patah like sound. no need base letter')
                current_phoneme.mark_letter_ready()
                
                
            # Geresh (Gimel, Ttadik, Tsadik sofit, Zain)
            if current_letter.contains_any_symbol([LetterSymbol.geresh, LetterSymbol.geresh_en]):
                if current_letter.as_str()  == Letters.GIMEL:
                    current_phoneme.add_phonemes('dʒ', 'Geresh in gimel like girafa')
                    current_phoneme.mark_letter_ready()
                if current_letter.as_str() in [Letters.TZADI, Letters.FINAL_TZADI]:
                    current_phoneme.add_phonemes('tʃ', 'Geresh in Tsadi like chita')
                    current_phoneme.mark_letter_ready()
                if current_letter.as_str() == Letters.ZAYIN:
                    current_phoneme.add_phonemes('dʒ', 'Geresh in Zain like Zargon')
                    current_phoneme.mark_letter_ready()
                if current_letter.as_str() == Letters.TAV:
                    current_phoneme.add_phonemes('ta', 'Geresh in tav like Tamvin')
                    current_phoneme.mark_letter_ready()
                        
                    
            # Silent He in end with Kamaz / Patah before
            if current_letter.as_str() == Letters.HEY and index == len(letters) - 1 and previous_letter and previous_letter.contains_patah_like_sound():
                current_phoneme.add_phonemes('', 'Silent he')
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
                current_phoneme.add_phonemes('u', 'Vav with dagesh in start')
                current_phoneme.mark_ready()
            
            # Dagesh (Bet, Kaf, Kaf sofit, Fey, Fey Sofit), 
            if current_letter.contains_any_symbol([LetterSymbol.dagesh_or_mapiq]) and not current_phoneme.is_ready():
                if current_letter.as_str() == Letters.BET:
                    current_phoneme.add_phonemes('b', 'Bet')
                    current_phoneme.mark_letter_ready()
                    
                if current_letter.as_str() == Letters.KAF:
                    current_phoneme.add_phonemes('k', 'Kaf')
                    current_phoneme.mark_letter_ready()
                    
                if current_letter.as_str() == Letters.FINAL_KAF:
                    current_phoneme.add_phonemes('k', 'Kaf sofit')
                    current_phoneme.mark_letter_ready()
                    
                if current_letter.as_str() == Letters.PEY:
                    current_phoneme.add_phonemes('p', 'Pey')
                    current_phoneme.mark_letter_ready()
                    
                if current_letter.as_str() == Letters.FINAL_PEY:
                    current_phoneme.add_phonemes('p', 'Final pey')
                    current_phoneme.mark_letter_ready()
                
                
            # Het in end like Ko(ax)
            if current_letter.as_str() == Letters.CHET and current_letter.contains_any_symbol([LetterSymbol.patah]) and index == len(letters) - 1:
                current_phoneme.add_phonemes('ax', 'Word ends with chet with patah')
                current_phoneme.mark_ready()
                
                
            # Base letter
            if not current_phoneme.is_ready() and not current_phoneme.is_letter_ready():
                from_table = PHONEME_TABLE.get(current_letter.as_str(), '')
                current_phoneme.add_phonemes(from_table, f'got letter {current_letter.as_str()} from table')
                
            # Kamatz Katan (o)
            if current_letter.contains_patah_like_sound():
                # Hataf Kamatz
                if current_letter.contains_any_symbol([LetterSymbol.hataf_qamats]):
                    current_phoneme.add_phonemes('o', 'Hataf qmqts')
                    current_phoneme.mark_ready()
                if current_letter.contains_any_symbol([LetterSymbol.qamats]):
                    if next_letter and next_letter.niqqud_has_dagesh():
                        current_phoneme.add_phonemes('o', 'Qamats is katan if next has dagesh')
                        current_phoneme.mark_ready()
                    # TODO: before Shva nah
                        
                
            # Shva na and Shva nah
            # https://he.wikipedia.org/wiki/שווא#שווא_נע
            if current_letter.niqqud_is_shva() and not current_phoneme.is_ready():
                if not next_letter and not previous_letter:
                    current_phoneme.add_phonemes('e', 'Single letter with shva')
                    current_phoneme.mark_as_shva_na()
                    current_phoneme.mark_ready()

                if next_letter and next_letter.as_str() == current_letter.as_str():  # Ensure there's a previous and next letter
                    current_phoneme.add_phonemes('e', 'First shva before identical letter')
                    current_phoneme.mark_as_shva_na()
                    current_phoneme.mark_ready()
                
                # Two last letters has shva
                elif index == len(letters) - 1 or index == len(letters) - 2:
                    if len(letters) > 1 and current_letter.niqqud_is_shva() and letters[-2].niqqud_is_shva():
                        current_phoneme.add_phonemes('', 'Two shva in end nah both')
                        current_phoneme.mark_ready()
                
                # Contains only shva
                elif index == 0:
                    if (current_letter.as_str() in ['אבוילמנער']):
                        current_phoneme.add_phonemes('e', 'Not possible to pronunce אבוילמנער as shva nah')
                        current_phoneme.mark_ready()
                    else:
                        current_phoneme.add_phonemes('e', 'Shva in first letter without other diacritics')
                        current_phoneme.mark_as_shva_na()
                        current_phoneme.mark_ready()
                    
                elif next_letter and next_letter.niqqud_is_shva():
                    current_phoneme.add_phonemes('', 'First shva in sequence')
                    current_phoneme.mark_ready()
                    
                elif previous_letter.niqqud_is_shva():
                    current_phoneme.add_phonemes('e', 'Second shva in sequence')
                    current_phoneme.mark_as_shva_na()
                    current_phoneme.mark_ready()
                    
                elif current_letter.niqqud_has_dagesh():
                    current_phoneme.add_phonemes('e', 'Shva with dagesh')
                    current_phoneme.mark_as_shva_na()
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
        # print(phonemes)
        return phonemes
