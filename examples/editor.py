"""
uv sync
uv pip install "gradio>=5.15.0"
uv run gradio examples/editor.py
"""

from mishkal import phonemize, normalize
import gradio as gr

default_text = """
כׇּ֫ל עֶ֫רֶב יָאִ֫יר (הַשֵּׁ֫ם הַמָּלֵ֫א וּמֽק֫וֹם הָעֲבוֹדָ֫ה שֶׁלּ֫וֹ שְׁמוּרִ֫ים בַּמַּעֲרֶ֫כֶת) רָ֫ץ 20 קִילוֹמֶ֫טֶר. ה֫וּא מֽסַפֵּ֫ר לִ֫י שֶׁזֶּ֫ה מֽנַקֶּ֫ה ל֫וֹ אֶ֫ת הָרֹ֫אשׁ אַחֲרֵ֫י הָעֲבוֹדָ֫ה, "שָׁעָ֫ה וָחֵ֫צִי בְּלִ֫י עֲבוֹדָ֫ה, אִשָּׁ֫ה וִילָדִ֫ים" כְּמ֫וֹ שֶׁה֫וּא מַגְדִּ֫יר זֹ֫את. אֲבָ֫ל אַחֲרֵ֫י הַמִּקְלַ֫חַת ה֫וּא מַתְחִ֫יל בּֽמָ֫ה שֶׁנִּתָּ֫ן לֽכַנּ֫וֹת הָעֲבוֹדָ֫ה הַשְּׁנִיָּ֫ה שֶׁלּ֫וֹ: לִמְצֹ֫א ל֫וֹ קוֹלֵ֫גוֹת חֲדָשׁ֫וֹת לָעֲבוֹדָ֫ה, כִּ֫י יָאִ֫יר ה֫וּא כַּנִּרְאֶ֫ה הַמֶּ֫לֶךְ שֶׁ֫ל "חָבֵ֫ר מֵבִ֫יא חָבֵ֫ר" בּֽיִשְׂרָאֵ֫ל.
""".strip()

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto")])


def on_submit(text: str, predict_stress, schema: str) -> str:
    return phonemize(text, predict_stress=predict_stress, schema=schema)


with gr.Blocks(theme=theme) as demo:
    text_input = gr.Textbox(
        value=default_text, label="Text", rtl=True, elem_classes=["input"], lines=5
    )

    schema_dropdown = gr.Dropdown(
        choices=["modern", "plain"], value="plain", label="Phoneme Schema"
    )
    predict_stress_checkbox = gr.Checkbox(value=False, label="Predict Stress")
    phonemes_output = gr.Textbox(label="Phonemes", lines=5)
    submit_button = gr.Button("Create")

    submit_button.click(
        fn=on_submit,
        inputs=[text_input, predict_stress_checkbox, schema_dropdown],
        outputs=[phonemes_output],
    )
    ## center markdown

    gr.Markdown("""
        <p style='text-align: center;'><a href='https://github.com/thewh1teagle/mishkal' target='_blank'>Mishkal on Github</a></p>
    """)

if __name__ == "__main__":
    demo.launch()
