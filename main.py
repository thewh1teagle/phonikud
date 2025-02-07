from chars import LETTERS_MAP
from g2p import g2p

possible_letters = []
for value in LETTERS_MAP.values():
    possible_letters.extend(value)

# for letter in possible_letters:
#     if len(letter) == 1:
#         print(letter)


text = "3 פּוֹדְקַאסְט"
# # print(hex(ord(text[-1])))
# # print(hex(ord("וֹ"[0])))
print(g2p(text))

