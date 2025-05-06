"""
uv sync
uv pip install "gradio>=5.15.0"
uv run gradio examples/editor.py
"""

from mishkal import phonemize
import gradio as gr

default_text = """כׇּל עֶ֫רֶב יָאִיר רָץ 20 קִילוֹמֶ֫טֶר. הוּא מֽסַפֵּר לִי שֶׁזֶּה מֽנַקֶּה לוֹ אֶת הָרֹאשׁ אַחֲרֵי הָעֲבוֹדָה, שָׁעָה וָחֵ֫צִי בְּלִי עֲבוֹדָה, אִשָּׁה וִילָדִים כְּמוֹ שֶׁהוּא מַגְדִּיר זֹאת. אֲבָל אַחֲרֵי הַמִּקְלַ֫חַת הוּא מַתְחִיל בּֽמָה שֶׁנִּתָּן לֽכַנּוֹת הָעֲבוֹדָה הַשְּׁנִיָּה שֶׁלּוֹ: לִמְצֹא לוֹ קוֹלֵ֫גוֹת חֲדָשׁוֹת לָעֲבוֹדָה, כִּי יָאִיר הוּא כַּנִּרְאֶה הַמֶּלֶךְ שֶׁל חָבֵר מֵבִיא חָבֵר בּֽיִשְׂרָאֵל.""".strip()

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto")])


def on_submit(text: str, predict_stress, schema: str) -> str:
    return phonemize(
        text, predict_stress=predict_stress, schema=schema, predict_shva_nah=False
    )


with gr.Blocks(theme=theme) as demo:
    text_input = gr.Textbox(
        value=default_text, label="Text", rtl=True, elem_classes=["input"], lines=5
    )

    schema_dropdown = gr.Dropdown(
        choices=["modern", "plain"], value="plain", label="Phoneme Schema"
    )
    predict_stress_checkbox = gr.Checkbox(value=True, label="Predict Stress")
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
