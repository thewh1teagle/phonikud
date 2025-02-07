from pathlib import Path
import re
from mishkal import normalize
import tomllib

RULES_PATH = Path(__file__).parent / 'rules'

RULES_MAP = {}
REGEX_RULES = []
REPLACE_MAP = {}

def read_toml(path: str):
    with open(path, "rb") as f:
        data = tomllib.load(f)
    for regex_rule in data.get('regex', []):
        # Expand $1 $2 etc
        for i in range(10):
            regex_rule['dst'] = regex_rule['dst'].replace(f'${i}', rf'\{i}')
        REGEX_RULES.append(regex_rule)

def read_txt(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            # clean comment from line
            line = re.sub(r"#.*", "", line).strip()
            line = normalize.normailze(line)
            parts = line.split()
            src = parts[0]
            dst = ' '.join(parts[1:])
            RULES_MAP[src] = dst

def read_rules():
    files = RULES_PATH.glob('**/**')
    for file in files:
        if file.suffix == '.txt':
            read_txt(file)
        elif file.suffix == '.toml':
            read_toml(file)
    
read_rules()