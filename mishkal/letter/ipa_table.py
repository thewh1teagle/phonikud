from ..lexicon.symbols import LetterSymbol
from ..lexicon.letters import Letters

PHONEME_TABLE = {
    # Letters
    Letters.ALEF: 'ʔ',
    Letters.BET: 'v',
    Letters.GIMEL: 'ɡ',
    Letters.DALET: 'd',
    Letters.HEY: 'h',
    Letters.VAV: 'v',
    Letters.ZAYIN: 'z',
    Letters.CHET: 'χ',
    Letters.TET: 't',
    Letters.YOD: 'j',
    Letters.KAF: 'k',
    Letters.LAMED: 'l',
    Letters.MEM: 'm',
    Letters.NUN: 'n',
    Letters.SAMECH: 's',
    Letters.AYIN: 'ʕ',
    Letters.PEY: 'p',
    Letters.TZADI: 'ts',
    Letters.QOF: 'k',
    Letters.RESH: 'ʁ',
    Letters.SHIN: 'ʃ',
    Letters.TAV: 't',
    
    # Final.value letters
    Letters.FINAL_KAF: 'x',
    Letters.FINAL_PEY: 'f',
    Letters.FINAL_TZADI: 'ts',
    Letters.FINAL_NUN: 'n',
    Letters.FINAL_MEM: 'm',
    
    # Symbols
    LetterSymbol.sheva: 'ʔ',  # SHEVA
    LetterSymbol.hataf_segol: 'ə',  # HATAF SEGOL
    LetterSymbol.hataf_patah: 'ə',  # HATAF PATAH
    LetterSymbol.hataf_qamats: 'ə',  # HATAF QAMATS
    LetterSymbol.hiriq: 'i',  # HIRIQ
    LetterSymbol.tsere: 'e',  # TSERE
    LetterSymbol.segol: 'ɛ',  # SEGOL
    LetterSymbol.patah: 'a',  # PATAH
    LetterSymbol.qamats: 'ɑ',  # QAMATS
    LetterSymbol.holam: 'o',  # HOLAM
    LetterSymbol.holam_haser_for_vav: 'o',  # HOLAM HASER FOR VAV
    LetterSymbol.qubuts: 'u',  # QUBUTS
    LetterSymbol.qamats_qatan: 'ɔ',  # QAMATS QATAN
    
    LetterSymbol.dagesh_or_mapiq: '',  # Handled in core
    LetterSymbol.shin_dot: '',  # Handled in core
    LetterSymbol.sin_dot: '',  # Handled in core
    LetterSymbol.geresh: '',  # Handled in core
    LetterSymbol.geresh_en: '',  # Handled in core
    
    
}

