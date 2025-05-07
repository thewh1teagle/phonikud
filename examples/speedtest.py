import time
from mishkal import phonemize

input_text = "אִישׁ לֹא טָרַח בְּֽמֶשֶׁךְ יוֹתֵר מֵחֹ֫ודֶשׁ לְֽהָכִין אֶת הַמַּעֲרָכוֹת הַשּׁוֹנוֹת לַקָּטַסְטְרוֹפָה הַהֲמוֹנִית שֶׁעֲלוּלָה לְֽהִתְרַחֵשׁ כָּאן."

start_time = time.time()
for _ in range(20):
    phonemized_text = phonemize(input_text)
end_time = time.time()

# Calculate results
elapsed_time = end_time - start_time
avg_time = elapsed_time / 20

print(f"⏱️ Total: {elapsed_time:.6f}s | Avg: {avg_time:.6f}s per sentence")
