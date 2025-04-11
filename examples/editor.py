"""
uv sync
uv pip install "gradio>=5.15.0"
uv run gradio examples/editor.py
"""

from mishkal import phonemize, normalize
import gradio as gr

default_text = """
כָּל עֶ֫רֶב יָאִ֫יר (הַשֵּׁ֫ם הַמָּלֵ֫א וּמֽק֫וֹם הָעֲבוֹדָ֫ה שֶׁלּ֫וֹ שְׁמוּרִ֫ים בַּמַּעֲרֶ֫כֶת) רָץ 20 קִילוֹמֶ֫טֶר. הוּא מֽסַפֵּ֫ר לִי שֶׁזֶּ֫ה מֽנַקֶּ֫ה לוֹ אֶת הָרֹ֫אשׁ אַחֲרֵ֫י הָעֲבוֹדָ֫ה, "שָׁעָ֫ה וָחֵ֫צִי בְּלִ֫י עֲבוֹדָ֫ה, אִשָּׁ֫ה וִילָדִ֫ים" כְּמ֫וֹ שֶׁה֫וּא מַגְדִּ֫יר זֹאת. אֲבָ֫ל אַחֲרֵ֫י הַמִּקְלַ֫חַת הוּא מַתְחִ֫יל בּֽמָ֫ה שֶׁנִּתָּ֫ן לֽכַנּ֫וֹת הָעֲבוֹדָ֫ה הַשְּׁנִיָּ֫ה שֶׁלּ֫וֹ: לִמְצֹ֫א לוֹ קוֹלֵ֫גוֹת חֲדָשׁ֫וֹת לָעֲבוֹדָ֫ה, כִּי יָאִ֫יר הוּא כַּנִּרְאֶ֫ה הַמֶּ֫לֶךְ שֶׁל "חָבֵ֫ר מֵבִ֫יא חָבֵ֫ר" בּֽיִשְׂרָאֵ֫ל.
דֻּגְמָא מַגְנִיבָה: [אנציקלופדיה](/ʔantsiklopˈedja/)
"""

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto")])


def on_submit_debug(text: str, predict_stress) -> str:
    phonemes = phonemize(text, preserve_punctuation=True, predict_stress=predict_stress)
    normalized_text = normalize(text)
    return phonemes + "\n\nNormalized:\n" + normalized_text


def on_submit(text: str, predict_stress) -> str:
    return phonemize(text, preserve_punctuation=False, predict_stress=predict_stress)


with gr.Blocks(theme=theme) as demo:
    text_input = gr.Textbox(
        value=default_text, label="Text", rtl=True, elem_classes=["input"]
    )
    debug_checkbox = gr.Checkbox(value=False, label="Enable Debug Mode")
    predict_stress_checkbox = gr.Checkbox(value=False, label="Predict Stress")
    phonemes_output = gr.Textbox(label="Phonemes")
    submit_button = gr.Button("Create")

    submit_button.click(
        fn=lambda text, debug, stress: on_submit_debug(text, stress) if debug else on_submit(text, stress),
        inputs=[text_input, debug_checkbox, predict_stress_checkbox],
        outputs=[phonemes_output],
    )


if __name__ == "__main__":
    demo.launch()
