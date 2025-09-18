"""
Hebrew Phonemizer FST

FST-based implementation for Hebrew text to phoneme conversion.
Inspired by the rule-based approach in hebrew.py but implemented as a finite state transducer.

Installation:
brew install openfst
export CPLUS_INCLUDE_PATH="/opt/homebrew/include:$CPLUS_INCLUDE_PATH"
export LIBRARY_PATH="/opt/homebrew/lib:$LIBRARY_PATH"
uv pip install pynini

Test:
uv run pytest ./tests/test_phonemize_fst.py
"""

import pynini
from typing import Literal
from phonikud import lexicon
from phonikud.utils import (
    normalize,
    get_letters,
    mark_vocal_shva,
    add_milra_hatama,
    post_clean,
    sort_stress,
)
from phonikud.variants import Letter
import re


class PhonemizerFST:
    def __init__(self):
        self.consonant_fst = self._build_consonant_fst()
        self.vowel_fst = self._build_vowel_fst()
        self.special_rules_fst = self._build_special_rules_fst()
        self.stress_fst = self._build_stress_fst()

        # Compose all FSTs into a single phonemization FST
        self.fst = self._compose_fsts()

    def _build_consonant_fst(self) -> pynini.Fst:
        """Build FST for Hebrew consonant mappings"""
        consonant_rules = []

        # Basic consonant mappings
        for hebrew_char, ipa_phone in lexicon.LETTERS_PHONEMES.items():
            if ipa_phone:  # Skip empty mappings
                consonant_rules.append(pynini.cross(hebrew_char, ipa_phone))

        # Geresh mappings
        for hebrew_char, ipa_phone in lexicon.GERESH_PHONEMES.items():
            geresh_char = hebrew_char + "'"
            consonant_rules.append(pynini.cross(geresh_char, ipa_phone))

        return pynini.union(*consonant_rules) if consonant_rules else pynini.Fst()

    def _build_vowel_fst(self) -> pynini.Fst:
        """Build FST for nikud (vowel) mappings"""
        vowel_rules = []

        for nikud_char, ipa_phone in lexicon.NIKUD_PHONEMES.items():
            if (
                ipa_phone and ipa_phone != lexicon.STRESS_PHONEME
            ):  # Handle stress separately
                vowel_rules.append(pynini.cross(nikud_char, ipa_phone))

        return pynini.union(*vowel_rules) if vowel_rules else pynini.Fst()

    def _build_special_rules_fst(self) -> pynini.Fst:
        """Build FST for special Hebrew phonemization rules"""
        special_rules = []

        # Shva rules - basic mapping for now
        shva = "\u05b0"
        special_rules.append(pynini.cross(shva, ""))  # Silent shva by default

        # Vocal shva (with meteg)
        vocal_shva = shva + lexicon.VOCAL_SHVA_DIACRITIC
        special_rules.append(pynini.cross(vocal_shva, "e"))

        # Dagesh mappings (already in consonant mappings but add explicit rules)
        dagesh = "\u05bc"
        special_rules.append(pynini.cross(dagesh, ""))  # Dagesh itself is silent

        return pynini.union(*special_rules) if special_rules else pynini.Fst()

    def _build_stress_fst(self) -> pynini.Fst:
        """Build FST for stress placement"""
        stress_rules = []

        # Hatama (stress marker) to IPA stress
        stress_rules.append(
            pynini.cross(lexicon.HATAMA_DIACRITIC, lexicon.STRESS_PHONEME)
        )

        return pynini.union(*stress_rules) if stress_rules else pynini.Fst()

    def _compose_fsts(self) -> pynini.Fst:
        """Compose all FSTs into a single phonemization FST"""
        # Create a union of all rules
        all_rules = []

        # Add all individual FSTs
        if not self.consonant_fst.start() == pynini.NO_STATE_ID:
            all_rules.append(self.consonant_fst)
        if not self.vowel_fst.start() == pynini.NO_STATE_ID:
            all_rules.append(self.vowel_fst)
        if not self.special_rules_fst.start() == pynini.NO_STATE_ID:
            all_rules.append(self.special_rules_fst)
        if not self.stress_fst.start() == pynini.NO_STATE_ID:
            all_rules.append(self.stress_fst)

        if not all_rules:
            return pynini.Fst()

        # Create a union of all rules
        combined_fst = pynini.union(*all_rules)

        # Make it apply to any sequence of characters
        return pynini.closure(combined_fst)

    def phonemize(self, text: str) -> str:
        """
        Phonemize Hebrew text using FST.
        For now, we'll use a hybrid approach combining FST with some rule-based logic
        from the original implementation.
        """
        # Normalize input
        text = normalize(text)

        # Apply vocal shva and stress prediction (rule-based for now)
        text = mark_vocal_shva(text)
        text = add_milra_hatama(text)

        # Get letters
        letters = get_letters(text)
        if not letters:
            return ""

        # For now, use rule-based approach similar to hebrew.py
        # TODO: Replace with pure FST implementation
        phonemes = self._phonemize_letters_hybrid(letters)

        # Join phonemes and clean up
        result = "".join(phonemes)
        result = post_clean(result)

        return result

    def _phonemize_letters_hybrid(self, letters: list[Letter]) -> list[str]:
        """
        Hybrid phonemization using both FST and rule-based logic.
        This is a transitional implementation.
        """
        phonemes = []
        stress_positions = []  # Track where stress markers appear
        i = 0

        while i < len(letters):
            cur = letters[i]
            prev = letters[i - 1] if i > 0 else None
            next_letter = letters[i + 1] if i + 1 < len(letters) else None

            # Track if this letter has stress marker
            has_stress = lexicon.HATAMA_DIACRITIC in cur.all_diac

            # Get phonemes for current letter using rule-based logic for now
            letter_phonemes, skip_offset = self._letter_to_phonemes_hybrid(
                cur, prev, next_letter
            )

            # Track stress position relative to phonemes
            if has_stress:
                stress_positions.append(
                    len(phonemes)
                )  # Position before adding phonemes

            phonemes.extend(letter_phonemes)
            i += skip_offset + 1

        # Apply stress sorting at word level using the tracked positions
        phonemes = self._apply_stress_placement_with_positions(
            phonemes, stress_positions
        )

        return phonemes

    def _letter_to_phonemes_hybrid(
        self, cur: Letter, prev: Letter | None, next_letter: Letter | None
    ) -> tuple[list[str], int]:
        """
        Convert a single letter to phonemes using hybrid approach.
        Based on the logic from hebrew.py but simplified for FST compatibility.
        """
        cur_phonemes = []
        skip_offset = 0
        skip_consonants = False
        skip_diacritics = False

        # Handle special cases
        if lexicon.NIKUD_HASER_DIACRITIC in cur.all_diac:
            skip_consonants = True
            skip_diacritics = True

        # Alef handling - skip consonant if it's in the middle without diacritics
        elif cur.char == "א" and not cur.diac and prev:
            if next_letter and next_letter.char != "ו":
                skip_consonants = True

        # Yud handling (simplified)
        elif cur.char == "י" and not cur.diac and prev and next_letter:
            skip_consonants = True

        # Shin/Sin handling
        elif cur.char == "ש" and "\u05c2" in cur.diac:  # Sin
            cur_phonemes.append("s")
            skip_consonants = True

        # Vav handling (simplified)
        elif cur.char == "ו":
            vav_phonemes, vav_skip_offset = self._handle_vav_simple(
                cur, prev, next_letter
            )
            if vav_phonemes:
                cur_phonemes.extend(vav_phonemes)
                skip_consonants = True
                skip_diacritics = True  # Skip diacritics when vav produces vowel
                skip_offset = vav_skip_offset

        # Geresh handling
        elif "'" in cur.diac and cur.char in lexicon.GERESH_PHONEMES:
            cur_phonemes.append(lexicon.GERESH_PHONEMES.get(cur.char, ""))
            skip_consonants = True

        # Dagesh handling
        elif "\u05bc" in cur.diac and cur.char + "\u05bc" in lexicon.LETTERS_PHONEMES:
            cur_phonemes.append(lexicon.LETTERS_PHONEMES.get(cur.char + "\u05bc", ""))
            skip_consonants = True

        # Add consonant if not skipped
        if not skip_consonants:
            consonant = lexicon.LETTERS_PHONEMES.get(cur.char, "")
            if consonant:
                cur_phonemes.append(consonant)

        # Add vowels if not skipped
        if not skip_diacritics:
            for nikud in cur.all_diac:
                if nikud in lexicon.NIKUD_PHONEMES:
                    vowel = lexicon.NIKUD_PHONEMES[nikud]
                    if vowel and vowel != lexicon.STRESS_PHONEME:
                        # Skip vocal shva (meteg) if there are other vowels
                        if nikud == lexicon.VOCAL_SHVA_DIACRITIC:
                            other_vowels = [
                                lexicon.NIKUD_PHONEMES.get(n)
                                for n in cur.all_diac
                                if n in lexicon.NIKUD_PHONEMES
                                and n != lexicon.VOCAL_SHVA_DIACRITIC
                                and lexicon.NIKUD_PHONEMES.get(n)
                                not in [lexicon.STRESS_PHONEME, ""]
                            ]
                            if other_vowels:
                                continue  # Skip the vocal shva
                        cur_phonemes.append(vowel)

        # Handle stress (hatama) - but don't skip diacritics if only stress
        if lexicon.HATAMA_DIACRITIC in cur.all_diac:
            cur_phonemes.append(lexicon.STRESS_PHONEME)

        # Clean up empty phonemes
        cur_phonemes = [
            p for p in cur_phonemes if p and all(c in lexicon.SET_PHONEMES for c in p)
        ]

        return cur_phonemes, skip_offset

    def _handle_vav_simple(
        self, cur: Letter, prev: Letter | None, next_letter: Letter | None
    ) -> tuple[list[str], int]:
        """Simplified Vav handling based on hebrew.py logic"""
        # Check for double vav patterns first
        if next_letter and next_letter.char == "ו":
            diac = cur.diac + next_letter.diac
            if "\u05b9" in diac:  # Holam
                return ["vo"], 1
            if cur.diac == next_letter.diac:
                return ["vu"], 1
            if "\u05b4" in cur.diac:  # Hirik
                return ["vi"], 0
            if "\u05b0" in cur.diac and not next_letter.diac:  # Shva
                return ["v"], 0
            if re.search("[\u05b7\u05b8]", cur.diac):  # Patah/Kamatz
                return ["va"], 0
            if "\u05b5" in cur.diac or "\u05b6" in cur.diac:  # Tsere/Segol
                return ["ve"], 0
            return [], 0

        # Single vav patterns
        if re.search("[\u05b7\u05b8]", cur.diac):  # Patah/Kamatz
            return ["va"], 0
        elif "\u05b5" in cur.diac or "\u05b6" in cur.diac:  # Tsere/Segol
            return ["ve"], 0
        elif "\u05b9" in cur.diac:  # Holam
            return ["o"], 0
        elif "\u05bb" in cur.diac or "\u05bc" in cur.diac:  # Kubuts or Dagesh
            return ["u"], 0
        elif "\u05b0" in cur.diac and not prev:  # Shva at beginning
            return ["ve"], 0
        elif "\u05b4" in cur.diac:  # Hirik
            return ["vi"], 0
        elif next_letter and not cur.diac:  # No diacritics, not final
            return [], 0
        else:
            return ["v"], 0

    def _apply_stress_placement(self, phonemes: list[str]) -> list[str]:
        """
        Apply stress placement logic.
        The stress marker should be placed before the vowel in the stressed syllable.
        """
        if lexicon.STRESS_PHONEME not in "".join(phonemes):
            return phonemes

        # Remove all stress markers first
        clean_phonemes = [p for p in phonemes if p != lexicon.STRESS_PHONEME]

        # Find vowels
        vowels = "aeiou"

        # Find the last vowel (Hebrew is typically stressed on the last syllable)
        # or use the first vowel if there's only one
        vowel_positions = []
        for i, phoneme in enumerate(clean_phonemes):
            for j, char in enumerate(phoneme):
                if char in vowels:
                    vowel_positions.append((i, j))

        if not vowel_positions:
            return clean_phonemes

        # Use the last vowel position for stress (milra - final stress)
        stress_pos_i, stress_pos_j = vowel_positions[-1]

        # Insert stress before the vowel
        phoneme = clean_phonemes[stress_pos_i]
        if stress_pos_j > 0:
            # Stress goes in the middle of the phoneme
            new_phoneme = (
                phoneme[:stress_pos_j] + lexicon.STRESS_PHONEME + phoneme[stress_pos_j:]
            )
            clean_phonemes[stress_pos_i] = new_phoneme
        else:
            # Stress goes at the beginning of the phoneme
            clean_phonemes[stress_pos_i] = lexicon.STRESS_PHONEME + phoneme

        return clean_phonemes

    def _apply_stress_placement_with_positions(
        self, phonemes: list[str], stress_positions: list[int]
    ) -> list[str]:
        """
        Apply stress placement based on the original positions of stress markers in the input.
        """
        if not stress_positions:
            return phonemes

        # Remove all existing stress markers
        clean_phonemes = [p for p in phonemes if p != lexicon.STRESS_PHONEME]

        # Use the first stress position (if multiple, prefer the first one)
        stress_pos = stress_positions[0]

        # Find the next vowel after the stress position
        vowels = "aeiou"

        for i in range(stress_pos, len(clean_phonemes)):
            phoneme = clean_phonemes[i]
            for j, char in enumerate(phoneme):
                if char in vowels:
                    # Insert stress before this vowel
                    if j > 0:
                        new_phoneme = phoneme[:j] + lexicon.STRESS_PHONEME + phoneme[j:]
                        clean_phonemes[i] = new_phoneme
                    else:
                        clean_phonemes[i] = lexicon.STRESS_PHONEME + phoneme
                    return clean_phonemes

        # If no vowel found after stress position, use the last vowel
        return self._apply_stress_placement(clean_phonemes + [lexicon.STRESS_PHONEME])
