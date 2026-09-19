"""
app.py — Gradio interface for Hugging Face Spaces.
For local use, run server.py instead (Flask, port 5000).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
import spaces
from syllabifier_es import syllabify
from phoneme_mapper import map_word
from renderer_linear import render


@spaces.GPU(duration=0)
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
    gr.Markdown(
        "# Mayaihcuilolliztli\n"
        "*Spanish → Classic Maya syllabary*\n\n"
        "Type any Spanish word and see it rendered in the glyphic script of the ancient Maya."
    )
    word_in  = gr.Textbox(label="Spanish word", placeholder="chocolate")
    btn      = gr.Button("Transliterate", variant="primary")
    img_out  = gr.Image(label="Maya glyphs", type="pil")
    info_out = gr.Textbox(label="Breakdown", lines=3)

    btn.click(transliterate, inputs=word_in, outputs=[img_out, info_out])
    word_in.submit(transliterate, inputs=word_in, outputs=[img_out, info_out])

    with gr.Accordion("What is this?", open=False):
        gr.Markdown("""
**Mayaihcuilolliztli** (from Nahuatl: *maya* + *ihcuilolliztli*, "the act of writing") is an
experimental tool that renders Spanish words using the **Classic Maya syllabary** — the
logosyllabic writing system used by Maya scribes from roughly 250–900 CE.

The Classic Maya script is a mixed system: some signs represent whole words (logograms),
others represent syllables of the form CV (consonant + vowel). This tool uses only the
syllabic signs, arranged in a linear sequence from left to right — a simplification of how
scribes actually composed glyphs into square blocks, but a readable introduction to the signs.

The name *Mayaihcuilolliztli* is Nahuatl, not Maya — a playful nod to the fact that Nahuatl
and Maya were both major Mesoamerican civilizations that never actually used each other's scripts.
        """)

    with gr.Accordion("Methodology", open=False):
        gr.Markdown("""
The pipeline has four stages:

1. **Spanish syllabification** — a rule-based algorithm that splits the input word into
   syllables, handling digraphs (ch, ll, rr, qu, gu), diphthongs, triphthongs, hiatus, and
   inseparable onset clusters (bl, tr, dr, etc.).

2. **Phoneme mapping (Landa alphabet)** — consonants are adapted using Diego de Landa's
   *Relación de las cosas de Yucatán* (c. 1566), the earliest attempt to map European sounds
   onto Maya signs. Substitutions include: r → l, f → p, d → t, z → s, v → b, ll → y,
   c/g before e/i → s/j, qu/gu → k. Onset clusters use only the first consonant (Maya
   syllabic writing cannot represent CC onsets).

3. **Synharmony** — when a syllable has a closing consonant (coda), Maya scribal convention
   requires a second, "dummy" CV sign whose vowel echoes the nucleus vowel. For example,
   Spanish *col* → **ko** + **lo** (the final *o* is understood to be silent by the reader).

4. **Rendering** — glyph images are composited with Pillow into a single PNG strip. Signs
   shown with an amber border are approximations: the syllabary has gaps (e.g., *be*, *pe*,
   *wu*) and the nearest available sign is substituted and marked with an asterisk.
        """)

    with gr.Accordion("Sources & credits", open=False):
        gr.Markdown("""
**Glyph images**
- Wikimedia Commons — Classic Maya syllabary images, various contributors (CC BY-SA / Public Domain).
  Full list: [commons.wikimedia.org/wiki/Category:Maya_syllabary](https://commons.wikimedia.org/wiki/Category:Maya_syllabary)

**Primary sources**
- Diego de Landa, *Relación de las cosas de Yucatán* (c. 1566) — the Landa alphabet
- John Montgomery, *Dictionary of Maya Hieroglyphs* (2002, Hippocrene Books)
- Simon Martin & Nikolai Grube, *Chronicle of the Maya Kings and Queens* (2000, Thames & Hudson)
- Harri Kettunen & Christophe Helmke, *Introduction to Maya Hieroglyphs* (2014, WAYEB)
- Marc Zender, "One Hundred and Fifty Years of Nahuatl Decipherment" (2008, PARI Journal)

**Tool**
- Built with Python · Pillow · Gradio
- Source code: [github.com/wilbertsmdo/mayaihcuilolliztli](https://github.com/wilbertsmdo/mayaihcuilolliztli)
        """)

demo.launch()
