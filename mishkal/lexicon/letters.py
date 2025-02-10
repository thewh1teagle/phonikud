"""
Alef - Taf and END letters
"""
class Letters:
    ALEF = '\u05D0'
    BET = '\u05D1'
    GIMEL = '\u05d2'
    DALET = '\u05d3'
    HEY = '\u05d4'
    VAV = '\u05d5'
    ZAYIN = '\u05d6'
    CHET = '\u05d7'
    TET = '\u05d8'
    YOD = '\u05d9'
    KAF = '\u05db'
    LAMED = '\u05dc'
    MEM = '\u05de'
    NUN = '\u05e0'
    SAMECH = '\u05e1'
    AYIN = '\u05e2'
    PEY = '\u05e4'
    TZADI = '\u05e6'
    QOF = '\u05e7'
    RESH = '\u05e8'
    SHIN = '\u05e9'
    TAV = '\u05ea'
    
    # Finals
    FINAL_KAF = '\u05DA'
    FINAL_MEM = '\u05dd'
    FINAL_NUN = '\u05DF'
    FINAL_PEY = '\u05E3'
    FINAL_TZADI = '\u05E5'

    @classmethod
    def values(cls) -> list[str]:
        # TODO: get rid of this
        return [value for name, value in cls.__dict__.items() if not name.startswith('__') and not callable(value) and not isinstance(value, classmethod)]

chars = [c for c in Letters.values()]