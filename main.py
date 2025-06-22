from collections import defaultdict, Counter
import json
import re
from tqdm import tqdm

def get_words(text):
    return re.findall(r'[\u0590-\u05EA]+', text)

word_to_phoneme = {}
word_freq = Counter()

with open('knesset_phonemes_v1.txt', encoding='utf-8') as fp:
    lines = fp.readlines()
    
for line in tqdm(lines, desc="Processing lines"):
    line = line.strip()
    if not line or '\t' not in line:
        continue
    text, phonemes = line.split('\t')
    words = get_words(text)
    phoneme_list = phonemes.split('|')

    if len(words) != len(phoneme_list):
        continue  # misaligned

    for word, phoneme in zip(words, phoneme_list):
        phoneme = phoneme.strip()
        if word not in word_to_phoneme:
            word_to_phoneme[word] = phoneme  # just store first seen
        word_freq[word] += 1

# Sort by frequency
sorted_items = sorted(word_to_phoneme.items(), key=lambda item: word_freq[item[0]], reverse=True)

# Save
with open("word_phoneme.json", "w", encoding="utf-8") as f:
    json.dump(dict(sorted_items), f, ensure_ascii=False, indent=2)
