"""
uv sync
uv pip install "gradio>=5.15.0" phonikud-onnx
uv run gradio examples/editor.py
"""

from mishkal import phonemize
import gradio as gr
from phonikud_onnx import Phonikud
from pathlib import Path

default_text = """
הדייג נצמד לדופן הסירה בזמן הסערה.  
הסברתי לה את הכל, ואמרתי בדיוק מה קרה.
הילדים אהבו במיוחד את הסיפורים הללו שהמורה הקריאה.
""".strip()

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Roboto")])

phonikud = None
model_path = Path("./phonikud-1.0.int8.onnx")
if model_path.exists():
    phonikud = Phonikud(str(model_path))


def on_submit(
    text: str, predict_stress, schema: str, use_phonikud: bool
) -> tuple[str, str]:
    if phonikud and use_phonikud:
        text = phonikud.add_diacritics(text)
    phonemes = phonemize(
        text, predict_stress=predict_stress, schema=schema, predict_shva_nah=False
    )
    return text, phonemes


with gr.Blocks(theme=theme) as demo:
    text_input = gr.Textbox(
        value=default_text, label="Text", rtl=True, elem_classes=["input"], lines=5
    )

    with gr.Row():
        schema_dropdown = gr.Dropdown(
            choices=["modern", "plain"], value="plain", label="Phoneme Schema"
        )
        with gr.Column():
            predict_stress_checkbox = gr.Checkbox(value=True, label="Predict Stress")
            use_phonikud_checkbox = gr.Checkbox(
                value=True, label="Use Phonikud (add diacritics)"
            )
    submit_button = gr.Button("Create")
    phonemes_output = gr.Textbox(label="Phonemes", lines=5)

    submit_button.click(
        fn=on_submit,
        inputs=[
            text_input,
            predict_stress_checkbox,
            schema_dropdown,
            use_phonikud_checkbox,
        ],
        outputs=[text_input, phonemes_output],  # text_input ראשון — יעדכן את תיבת הקלט
    )
    ## center markdown

    gr.Markdown("""
        <p style='text-align: center;'><a href='https://github.com/thewh1teagle/mishkal' target='_blank'>Mishkal on Github</a></p>
    """)

if __name__ == "__main__":
    demo.launch()
