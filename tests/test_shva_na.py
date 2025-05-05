from mishkal.utils import mark_shva_na, normalize
import pandas as pd
from mishkal import lexicon
from pathlib import Path

BASE_PATH = Path(__file__).parent


def test_shva_na():
    df = pd.read_csv(BASE_PATH / "./shva_test_tables/words.csv")
    for row in df.itertuples():
        src_word = row.word
        dst_word = src_word.replace(lexicon.SHVA_NA_DIACRITIC, "")
        dst_word = mark_shva_na(dst_word)

        # Normalize
        src_word = normalize(src_word)
        dst_word = normalize(dst_word)

        assert dst_word == src_word
