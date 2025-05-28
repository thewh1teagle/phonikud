"""
uv pip install gradio
uv run gradio examples/editor.py
"""

from phonikud import phonemize, lexicon
from phonikud.utils import remove_nikud
import gradio as gr
from phonikud_onnx import Phonikud
from pathlib import Path


default_text = """
הַדַּיָּיג נִצְמָד לְדֹופֶן הַסִּירָה בִּזְמַן הַסְּעָרָה.  
הִסְבַּרְתִּי לָהּ אֶת הַכֹּל, וְאָמַרְתִּי בְּדִיּוּק מָה קָרָה.
הַיְּלָדִים אָהֲבוּ בִּמְיֻוחָד אֶת הַסִּיפּוּרִים הַלָּלוּ שֶׁהַמּוֹרָה הִקְרִיאָה.
""".strip()


def on_phonikud_toggle(use_phonikud):
    if not use_phonikud:
        return default_text
    return remove_nikud(default_text)


css = """
    .input textarea {
        font-size: 22px;
        padding: 15px;
        height: 200px;
    }

    .phonemes {
        background: var(--input-background-fill);
        
    }
    .phonemes {
        padding: 5px;
        min-height: 50px;    
    }
"""

theme = gr.themes.Soft(font=[gr.themes.GoogleFont("Noto Sans Hebrew")])

phonikud = None
model_path = Path("./phonikud-1.0.int8.onnx")
if model_path.exists():
    phonikud = Phonikud(str(model_path))


def on_submit(text: str, schema: str, use_phonikud: bool) -> str:
    diacritized = (
        phonikud.add_diacritics(
            text, mark_matres_lectionis=lexicon.NIKUD_HASER_DIACRITIC
        )
        if phonikud and use_phonikud
        else text
    )
    phonemes = phonemize(
        diacritized, predict_stress=True, schema=schema, predict_shva_nah=False
    )
    if use_phonikud:
        return f"<div dir='rtl' style='font-size: 22px;'>{diacritized.strip()}</div><br><div dir='ltr' style='font-size: 22px;'>{phonemes.strip()}</div>"
    else:
        return f"<div dir='ltr' style='font-size: 22px;'>{phonemes.strip()}</div>"


with gr.Blocks(theme=theme, css=css) as demo:
    text_input = gr.Textbox(
        value=remove_nikud(default_text),
        label="Text",
        rtl=True,
        elem_classes=["input"],
        lines=7,
    )

    with gr.Row():
        schema_dropdown = gr.Dropdown(
            choices=["modern", "plain"], value="plain", label="Phoneme Schema"
        )
        use_phonikud_checkbox = gr.Checkbox(
            value=True, label="Use Phonikud (add diacritics)"
        )

    submit_button = gr.Button("Create")
    output_box = gr.Markdown(label="Phonemes + Diacritics", elem_classes=["phonemes"])
    use_phonikud_checkbox.change(
        fn=lambda use_phonikud: (
            on_phonikud_toggle(use_phonikud),  # Update text_input
            on_submit(
                on_phonikud_toggle(use_phonikud), schema_dropdown.value, use_phonikud
            ),  # Update output_box
        ),
        inputs=use_phonikud_checkbox,
        outputs=[text_input, output_box],  # Update both text input and output box
    )

    submit_button.click(
        fn=on_submit,
        inputs=[text_input, schema_dropdown, use_phonikud_checkbox],
        outputs=output_box,
    )

    gr.Markdown("""
        <p style='text-align: center;'><a href='https://github.com/thewh1teagle/phonikud' target='_blank'>Phonikud on Github</a></p>
    """)

if __name__ == "__main__":
    demo.launch()
