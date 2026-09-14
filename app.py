"""
app.py — Gradio interface for Hugging Face Spaces.
For local use, run server.py instead (Flask, port 5000).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from syllabifier_es import syllabify
from phoneme_mapper import map_word
from renderer_linear import render


def transliterate(word):
    if not word or not word.strip():
        return None, ""
    w = word.strip()
    syllables = syllabify(w)
    signs     = map_word(syllables)
    img       = render(signs, captions=True)

    syl_str  = "Syllables: " + " · ".join(syllables)
    sign_str = "Signs: " + " + ".join(s.key if s.exact else f"{s.key}*" for s in signs)
    approx   = sorted(set(s.key for s in signs if not s.exact))
    note     = ("\n* Approximation (no exact sign in syllabary): " + ", ".join(approx)) if approx else ""

    return img, syl_str + "\n" + sign_str + note


with gr.Blocks(title="Mayaihcuilolliztli") as demo:
    gr.Markdown("# Mayaihcuilolliztli\n*Spanish → Classic Maya syllabary*")
    word_in  = gr.Textbox(label="Spanish word", placeholder="chocolate")
    btn      = gr.Button("Transliterate", variant="primary")
    img_out  = gr.Image(label="Maya glyphs", type="pil")
    info_out = gr.Textbox(label="Breakdown", lines=3)

    btn.click(transliterate, inputs=word_in, outputs=[img_out, info_out])
    word_in.submit(transliterate, inputs=word_in, outputs=[img_out, info_out])

demo.launch()
