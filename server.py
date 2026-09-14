"""
app.py — Flask web interface for Mayaihcuilolliztli.

Run:
    python app.py
Then open http://localhost:5000 in your browser.
"""

import sys, os, io, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, render_template_string
from syllabifier_es import syllabify
from phoneme_mapper import map_word
from renderer_linear import render

app = Flask(__name__)

_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mayaihcuilolliztli</title>
  <style>
    body { font-family: sans-serif; max-width: 820px; margin: 40px auto; padding: 0 16px; background: #fdf9f0; color: #2a1f0e; }
    h1   { margin-bottom: 2px; font-size: 1.8em; }
    .sub { color: #777; margin-top: 0 0 28px 0; font-size: 0.95em; }
    form { display: flex; gap: 8px; margin: 24px 0; }
    input[type=text] {
      flex: 1; padding: 11px 14px; font-size: 1.1em;
      border: 1px solid #c8bfaf; border-radius: 5px; background: #fff;
    }
    button {
      padding: 11px 22px; font-size: 1em; cursor: pointer;
      background: #5a3e1b; color: #fff; border: none; border-radius: 5px;
    }
    button:hover { background: #7a5628; }
    .result { margin-top: 4px; }
    .meta   { font-size: 0.92em; color: #555; margin-bottom: 12px; line-height: 1.7; }
    img     { border: 1px solid #ddd4c0; border-radius: 5px; max-width: 100%; }
    .note   { font-size: 0.82em; color: #999; margin-top: 8px; }
  </style>
</head>
<body>
  <h1>Mayaihcuilolliztli</h1>
  <p class="sub">Spanish &rarr; Classic Maya syllabary</p>

  <form method="post">
    <input type="text" name="word" value="{{ word }}"
           placeholder="chocolate" autofocus autocomplete="off">
    <button type="submit">Transliterate</button>
  </form>

  {% if img_b64 %}
  <div class="result">
    <div class="meta">
      <b>Syllables:</b> {{ syllables }}<br>
      <b>Signs:</b> {{ sign_keys }}
    </div>
    <img src="data:image/png;base64,{{ img_b64 }}" alt="Maya glyphs for {{ word }}">
    {% if note %}
    <p class="note">* Approximation &mdash; no exact sign in syllabary: {{ note }}</p>
    {% endif %}
  </div>
  {% endif %}
</body>
</html>"""


@app.route('/', methods=['GET', 'POST'])
def index():
    word = img_b64 = syllables_str = sign_keys_str = note = ''

    if request.method == 'POST':
        word = request.form.get('word', '').strip()
        if word:
            syllables = syllabify(word)
            signs     = map_word(syllables)

            syllables_str  = ' · '.join(syllables)
            sign_keys_str  = ' + '.join(s.key if s.exact else f'{s.key}*' for s in signs)
            note           = ', '.join(sorted(set(s.key for s in signs if not s.exact)))

            buf = io.BytesIO()
            render(signs, captions=True).save(buf, format='PNG')
            img_b64 = base64.b64encode(buf.getvalue()).decode()

    return render_template_string(
        _HTML,
        word=word, img_b64=img_b64,
        syllables=syllables_str, sign_keys=sign_keys_str, note=note,
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
