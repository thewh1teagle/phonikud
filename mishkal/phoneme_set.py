"""
Return all phonemes used by mishkal
Both from table and by analyzing the code of the package
"""

import ast
import mishkal
import unicodedata
from functools import lru_cache
from pathlib import Path
from .phoneme_table import PHONEME_TABLE
from collections import defaultdict

def _get_phonemes_with_reasons():
    """
    Analyze phonemize.py with function calls to add_phonemes()
    """
    
    phonemes = []

    # Analyze phoneme_table.py
    phonemize_path = Path(mishkal.__file__).parent / 'phonemize.py'
    with open(phonemize_path, 'r') as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    class FuncCallVisit(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'add_phonemes':
                if node.args:
                    first_arg = node.args[0]
                    second_arg = node.args[1]
                    if isinstance(first_arg, ast.Str):
                        phonemes.append({'phoneme': str(first_arg.s), 'reason': second_arg.s})
                    else:
                        phonemes.append({'phoneme': '[DYNAMIC]', 'reason': f"mishkal/{phonemize_path.name} line {node.lineno}"})
            # Continue traversing the AST
            self.generic_visit(node)

    visitor = FuncCallVisit()
    visitor.visit(tree)
    return phonemes


@lru_cache
def get_phoneme_set():
    """
    Return all phonemes used in Mishkal package
    """
    
    phonemes = []
    # From table
    phonemes.extend([{'phoneme': value, 'reason': unicodedata.name(key).replace('HEBREW ', '')} for key, value in PHONEME_TABLE.items()])
    # From phonemize
    phonemes.extend(_get_phonemes_with_reasons())
    # One exception
    phonemes.extend([{'phoneme': '[SPACE]', 'reason': 'Space'}])    
    
    # Deduplicate
    deduplicated = defaultdict(list)
    for phoneme in phonemes:
        deduplicated[phoneme['phoneme'] if phoneme['phoneme'] else '[SILENT]'].append(phoneme['reason'])
    # Sort
    deduplicated = dict(sorted(deduplicated.items()))
    
    return deduplicated
