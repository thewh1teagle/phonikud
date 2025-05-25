"""
Add stress (Hat'ama) diacritic using Kolani
"""

from kolani.syllables import add_stress

data = {"אוֹמֶרֶת": -2, "דֶרֶךְ": -2,
        "גִּימִיקִים": -3, "קוֹרֶה": -1, "רַדְיוֹ": -2}
data = {"רֵפוֹרְמוֹת": -2}
for k, v in data.items():
    stressed = add_stress(k, v)
    print(stressed)
