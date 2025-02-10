"""
Analyze phonemize.py -> add_phonemes() calls
and collect every phoneme used in Mishkal.

uv run examples/possible_phonemes.py
"""
import ast
from pathlib import Path
from mishkal.phonemize import PHONEME_TABLE

phonemes = set(PHONEME_TABLE.values())
phonemize_path = Path(__file__).parent / '../mishkal/phonemize.py'

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

# Print the collected phonemes
phonemes = sorted([i for i in phonemes if i])
print(', '.join(phonemes))