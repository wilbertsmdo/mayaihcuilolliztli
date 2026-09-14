"""
renderer_linear.py — Composite Maya syllabogram glyphs into a left-to-right strip.

Public API:
    render(signs, captions=True) → PIL.Image
    render_word(word, captions=True) → PIL.Image   (convenience wrapper)
"""

import os, json
from PIL import Image, ImageDraw

BASE   = os.path.dirname(os.path.abspath(__file__))
GLYPHS = os.path.join(BASE, 'glyphs')

GLYPH_H       = 150              # uniform glyph height (px)
GAP           = 14               # horizontal gap between glyphs
PAD           = 18               # outer padding
CAPTION_H     = 22               # space below glyphs for labels
BG            = (255, 255, 255)  # white canvas
APPROX_COLOR  = (210, 140, 30)   # amber border: sign is a fallback approximation
MISSING_COLOR = (180, 180, 180)  # gray placeholder: no sign found at all

with open(os.path.join(BASE, 'data', 'mappings.json')) as _f:
    _MAPPINGS = json.load(_f)


def _pick_file(key: str):
    """
    Select the best local JPG file for a sign key.
    Priority: exact variant name → _1 variant → any non-pfx/sfx → any JPG.
    Returns filename string or None.
    """
    variants = _MAPPINGS.get(key, [])
    jpg = [v for v in variants if v['local_file'].lower().endswith('.jpg')]
    if not jpg:
        return None
    for v in jpg:
        if v['variant_key'] == key:
            return v['local_file']
    for v in jpg:
        if v['variant_key'] == key + '_1':
            return v['local_file']
    skip = ('pfx', 'sfx', 'suf', 'prefix', 'suffix')
    for v in jpg:
        if not any(t in v['variant_key'] for t in skip):
            return v['local_file']
    return jpg[0]['local_file']


def _load(fname: str):
    path = os.path.join(GLYPHS, fname)
    if not os.path.exists(path):
        return None
    try:
        return Image.open(path).convert('RGBA')
    except Exception:
        return None


def _scale(img: Image.Image, h: int) -> Image.Image:
    w = max(1, int(img.width * h / img.height))
    return img.resize((w, h), Image.LANCZOS)


def _placeholder(size=GLYPH_H) -> Image.Image:
    img = Image.new('RGBA', (size, size), (*MISSING_COLOR, 255))
    d = ImageDraw.Draw(img)
    d.text((size // 2 - 6, size // 2 - 10), '?', fill=(60, 60, 60))
    return img


def render(signs, captions=True) -> Image.Image:
    """
    Render a list of Sign(key, exact) objects into a horizontal glyph strip.

    Amber border = fallback sign (syllabary gap, nearest available used).
    Gray square  = completely unknown sign (no image available).

    Args:
        signs:    list[Sign] from phoneme_mapper.map_word()
        captions: draw romanized key below each glyph

    Returns: PIL Image (RGB)
    """
    cells = []
    for sign in signs:
        fname = _pick_file(sign.key)
        img = _load(fname) if fname else None
        if img is None:
            img = _placeholder()
        else:
            img = _scale(img, GLYPH_H)
        cells.append((img, sign))

    if not cells:
        return Image.new('RGB', (200, GLYPH_H + PAD * 2), BG)

    total_w = PAD * 2 + sum(c[0].width for c in cells) + GAP * (len(cells) - 1)
    total_h = PAD * 2 + GLYPH_H + (CAPTION_H if captions else 0)
    canvas = Image.new('RGB', (total_w, total_h), BG)
    draw   = ImageDraw.Draw(canvas)

    x = PAD
    for img, sign in cells:
        y = PAD + (GLYPH_H - img.height) // 2

        # White backing so JPG white backgrounds blend into canvas
        draw.rectangle([x, PAD, x + img.width - 1, PAD + GLYPH_H - 1], fill=BG)
        canvas.paste(img, (x, y), img)

        # Amber border for inexact (fallback) signs
        if not sign.exact:
            draw.rectangle(
                [x - 2, PAD - 2, x + img.width + 1, PAD + GLYPH_H + 1],
                outline=APPROX_COLOR, width=2
            )

        if captions:
            label = sign.key
            bbox  = draw.textbbox((0, 0), label)
            lw    = bbox[2] - bbox[0]
            lx    = x + (img.width - lw) // 2
            draw.text((lx, PAD + GLYPH_H + 5), label, fill=(80, 60, 40))

        x += img.width + GAP

    return canvas


def render_word(word: str, captions=True) -> Image.Image:
    """Syllabify → map → render in one call."""
    from syllabifier_es import syllabify
    from phoneme_mapper import map_word
    return render(map_word(syllabify(word)), captions=captions)
