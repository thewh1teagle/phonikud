"""
Add stress (Atma'a) diacritic using Mishkal
"""

from mishkal.syllables import add_stress

data = {"אוֹמֶרֶת": -2, "דֶרֶךְ": -2, "גִּימִיקִים": -3, "קוֹרֶה": -1, "רַדְיוֹ": -2}
data = {"עַצְמֵנוּ": -2}
for k, v in data.items():
    stressed = add_stress(k, v)
    print(stressed)
