class Diacritics:
    """    
    UTF-8 Hebrew table
    https://en.wikipedia.org/wiki/Unicode_and_HTML_for_the_Hebrew_alphabet#Compact_table
    We use U+05Bx U+05Cx U+05Fx

    Professional Nakdan
    https://nakdanpro.dicta.org.il/nikudedit
    Quick Nakdan
    https://nakdanlive.dicta.org.il
    """
    
    # From 0x05B0 to 0x05BF
    
    SHVA = '\u05B0' # Like d
    HATAF_SEGOL = '\u05B1' # Like de
    HATAF_PATAH = '\u05B2' # Like da
    HATAF_KAMATZ = '\u05B3' # Like da
    HIRIK = '\u05B4' # Like di
    TSERE = '\u05B5' # Like de
    SEGOL = '\u05B6' # Like de
    PATAH = '\u05B7' # Like da
    KAMATZ = '\u05B8' # Like da
    HOLAM = '\u05B9' # Like do
    VAV_HOLAM_HASER = '\u05BA' # Like vo
    KUBUTZ = '\u05BB' # Like vu
    DAGESH = '\u05BC' # Like in (b)et or (p)et
    
    # Not used
    METEG = '\u05BD' # Meteg
    MAKAF = '\u05BE' # Makaf
    
    # Not used
    RAFE = '\u05BF' # Like in vet rarely used. oppsite to Dagesh to mark it's vet not bet
    
    # From 0x05C0 to 0x05CF
    
    # Not used
    PUNCTUATION_PASEQ = '\u05C0'
    
    SHIN_DOT = '\u05C1' # Like shin
    SIN_DOT = '\u05C2' # like sin
    
    # Not used
    SOF_PASUK = '\u05C3'
    
    UPPER_DOT = '\u05C4'
    LOWER_DOT = '\u05C5'
    
    # Not used
    NUN_AFUKHA = '\u05C6'
    
    KAMATZ_KATAN = '\u05C7' # like da    
    
    # From 0x05F0 to 0x05FF
    YIDDISH_DOUBLE_VAV = '\u05F0' # like vav
    YIDDISH_VAV_YOD = '\u05F1' # like vi
    YIDDISH_YOD_YOD = '\u05F2' # like ii
    
    GERESH = '\u05F3' # like '
    GERSHAIM = '\u05F4' # like "
    