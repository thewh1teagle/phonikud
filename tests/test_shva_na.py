from phonikud.utils import mark_vocal_shva, normalize
import pandas as pd
from phonikud import lexicon
from pathlib import Path

BASE_PATH = Path(__file__).parent


def test_vocal_shva():
    df = pd.read_csv(BASE_PATH / "./shva_test_tables/words.csv")
    for row in df.itertuples():
        src_word = row.word
        dst_word = src_word.replace(lexicon.VOCAL_SHVA_DIACRITIC, "")
        dst_word = mark_vocal_shva(dst_word)

        # Normalize
        src_word = normalize(src_word)
        dst_word = normalize(dst_word)

        assert dst_word == src_word
