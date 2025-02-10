from .lexicon.symbols import LetterSymbol
from .lexicon.letters import Letters
import ast
from pathlib import Path
from functools import lru_cache

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
    Letters.KAF: 'x',
    Letters.LAMED: 'l',
    Letters.MEM: 'm',
    Letters.NUN: 'n',
    Letters.SAMECH: 's',
    Letters.AYIN: 'ʕ',
    Letters.PEY: 'f',
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
    LetterSymbol.hataf_segol: 'e',  # HATAF SEGOL
    LetterSymbol.hataf_patah: 'a',  # HATAF PATAH
    LetterSymbol.hataf_qamats: 'o',  # HATAF QAMATS
    LetterSymbol.qamats: 'a',  # QAMATS
    LetterSymbol.qamats_qatan: 'o',  # QAMATS QATAN
    LetterSymbol.patah: 'a',  # PATAH
    
    LetterSymbol.hiriq: 'i',  # HIRIQ
    LetterSymbol.tsere: 'e',  # TSERE
    LetterSymbol.segol: 'e',  # SEGOL
    LetterSymbol.holam: 'o',  # HOLAM
    LetterSymbol.holam_haser_for_vav: 'o',  # HOLAM HASER FOR VAV
    LetterSymbol.qubuts: 'u',  # QUBUTS
    
    
    LetterSymbol.sheva: '',  # Handled in core
    LetterSymbol.dagesh_or_mapiq: '',  # Handled in core
    LetterSymbol.shin_dot: '',  # Handled in core
    LetterSymbol.sin_dot: '',  # Handled in core
    LetterSymbol.geresh: '',  # Handled in core
    LetterSymbol.geresh_en: '',  # Handled in core
}

@lru_cache
def get_possible_phonemes():
    phonemes = set(PHONEME_TABLE.values())
    phonemize_path = Path(__file__).parent / 'phonemize.py'

    with open(phonemize_path, 'r') as file:
        file_content = file.read()


    tree = ast.parse(file_content)

    class FuncCallVisit(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'add_phonemes':
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Constant):
                        phonemes.add(first_arg.s)  # Collect string arguments
            # Continue traversing the AST
            self.generic_visit(node)

    visitor = FuncCallVisit()
    visitor.visit(tree)
    
    phonemes = sorted([i for i in phonemes if i])
    return phonemes
