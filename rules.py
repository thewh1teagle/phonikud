from pathlib import Path
from chars import IPA_SYMBOLS
import re

RULES_PATH = Path(__file__).parent / 'rules'

def read_rules():
    files = RULES_PATH.glob('**/*.txt')
    rules = {}
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                # clean comment from line
                line = re.sub(r"#.*", "", line).strip()
                parts = line.split()
                if len(parts) != 2:
                    print(f'Skipping {line}')
                    continue
                # TODO
                # for c in parts[1]:
                #     if c not in IPA_SYMBOLS:
                #         print(c)
                rules[parts[0]] = parts[1]
    return rules
                
RULES_MAP = read_rules()             