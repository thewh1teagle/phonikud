from transformers import AutoTokenizer, AutoModel
from transformers.models.bert.tokenization_bert_fast import BertTokenizerFast
import phonikud

model = AutoModel.from_pretrained("thewh1teagle/phonikud", trust_remote_code=True)
tokenizer: BertTokenizerFast = AutoTokenizer.from_pretrained("thewh1teagle/phonikud")
model.to("cpu")
model.eval()

text = "כמה אתה חושב שזה יעלה לי? אני מגיע לשם רק בערב.."
predicted = model.predict([text], tokenizer)[0]
# with diacritics
print(predicted)
# phonemes
phonemes = phonikud.phonemize(predicted)
print(phonemes)
