from pathlib import Path
from .chars import IPA_SYMBOLS
import re
from mishkal import normalize

RULES_PATH = Path(__file__).parent / 'rules'

RULES_MAP = {}
REGEX_MAP = {}
REPLACE_MAP = {}

def read_rules():
    files = RULES_PATH.glob('**/*.txt')
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
                
                
                
                if line.startswith('.regex'):
                    line = normalize.normailze(line, normalize_beged_kefet=False)
                    parts = line.split()
                    replace_value = parts[-1]
                    replace_value = replace_value.replace(r'$1', r'\1')
                    REGEX_MAP[parts[1]] = replace_value
                    continue
                line = normalize.normailze(line)
                
                
                if line.startswith('.replace'):
                    parts = line.split()
                    src, dst = parts[1].lower(), parts[2].lower()
                    if src.startswith('0x'):
                        src = chr(int(src, base=16))
                    if dst.startswith('0x'):
                        dst = chr(int(dst, base=16))
                    if dst == 'empty':
                        dst = ''
                        breakpoint()
                    REPLACE_MAP[src] = dst
                
                parts = line.split()
                if len(parts) != 2:
                    # TODO
                    # print(f'Skipping {line}')
                    continue
                # TODO
                # for c in parts[1]:
                #     if c not in IPA_SYMBOLS:
                #         print(c)
                RULES_MAP[parts[0]] = parts[1]
    print(REGEX_MAP)
read_rules()