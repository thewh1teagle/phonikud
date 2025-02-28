
from mishkal import phonemize

text = """
sfd;kljasdf;lkjasdflkjsdf;lfjaksf'fajl;k23409740278423@#$@!4@!#%#^$#$%&$%^*%^*%$^=156465165 5156s1fd 321. as0f0 as321f3as21dfsaf 
asdfsafsafsd fasf asf dכגדכש דגכ ש
כד שכגשד כשד כדג 
dsf fd/j.lkj/kj['j;jpoiup9iu987755]
我喜欢学习新技术和挑战自己。
أنا أحب تعلم التقنيات الجديدة وتحدي نفسي.
Esdf$fsdADsf

"""

def test_invalid_input():
    print(phonemize(text))
    
    
test_invalid_input()
