"""
Every possible symbols to letters in Hebrew
"""

class LetterSymbol:
    sheva = '\u05B0' # SHEVA
    hataf_segol = '\u05B1' # HATAF SEGOL
    hataf_patah = '\u05B2' # HATAF PATAH
    hataf_qamats = '\u05B3' # HATAF QAMATS
    hiriq = '\u05B4' # HIRIQ
    tsere = '\u05B5' # TSERE
    segol = '\u05B6' # SEGOL
    patah = '\u05B7' # PATAH
    qamats = '\u05B8' # QAMATS
    holam = '\u05B9' # HOLAM
    holam_haser_for_vav = '\u05BA' # HOLAM HASER FOR VAV
    qubuts = '\u05BB' # QUBUTS
    dagesh_or_mapiq = '\u05BC' # DAGESH OR MAPIQ
    shin_dot = '\u05C1' # SHIN DOT
    sin_dot = '\u05C2' # SIN DOT
    qamats_qatan = '\u05C7' # QAMATS QATAN
    
    geresh = '\u05F3' # HEBREW GERESH
    geresh_en = "'" # ENGLISH GERESH

    @classmethod
    def values(cls) -> list[str]:
        # TODO: get rid of this
        return [value for name, value in cls.__dict__.items() if not name.startswith('__') and not callable(value) and not isinstance(value, classmethod)]


chars = [c for c in LetterSymbol.values()]