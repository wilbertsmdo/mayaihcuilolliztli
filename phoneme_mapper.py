"""
phoneme_mapper.py — Maps Spanish syllables to Classic Maya syllabogram keys.

Based on the Landa alphabet (c. 1566) and Knorosov's syllabary documentation.

Public API:
    map_syllable(syl: str) → list[Sign]
    map_word(syllables: list[str]) → list[Sign]

Sign = namedtuple('Sign', ['key', 'exact'])
  key   — string key into data/mappings.json
  exact — True if the sign exists in the syllabary; False if a fallback was used
"""

import os, json, sys
from collections import namedtuple

sys.path.insert(0, os.path.dirname(__file__))
from syllabifier_es import _tokenize, _is_vowel, _VOWELS

Sign = namedtuple('Sign', ['key', 'exact'])

# ── Consonant onset map ───────────────────────────────────────────────────────
# Spanish grapheme → Maya consonant label.
# 'c' and 'g' are context-sensitive (see _onset_maya).
ONSET = {
    'b':  'b',
    'ch': 'ch',
    'd':  't',    # Landa: D → T (Maya has no voiced dental stop)
    'f':  'p',    # Landa: F → P (Maya has no labiodental fricative)
    'g':  'k',    # hard G (before a/o/u) → K; soft G handled contextually
    'gu': 'k',    # gu (silent u, before e/i) → K
    'h':  'h',    # Spanish H is silent; use Maya H sign
    'j':  'j',    # Spanish /x/ → Maya J
    'k':  'k',
    'l':  'l',
    'll': 'y',    # modern LL = /j/ → Y
    'm':  'm',
    'n':  'n',
    'ñ':  'n',    # palatal nasal → N (approximation for Phase 1)
    'p':  'p',
    'qu': 'k',    # qu = /k/ (u is silent)
    'r':  'l',    # Landa: R → L (Maya has no alveolar trill)
    'rr': 'l',
    's':  's',
    't':  't',
    'v':  'b',    # voiced labiodental → labial b
    'w':  'w',
    'x':  'x',    # Spanish X → Maya X (/ʃ/, approximation)
    'y':  'y',
    'z':  's',    # voiced sibilant → S
}

VOWEL_NORM = {
    'a': 'a', 'á': 'a',
    'e': 'e', 'é': 'e',
    'i': 'i', 'í': 'i',
    'o': 'o', 'ó': 'o',
    'u': 'u', 'ú': 'u',
}

# Fallback vowel order when the exact CV sign is missing from the syllabary
_VOWEL_FALLBACK = {
    'a': ['e', 'o', 'i', 'u'],
    'e': ['i', 'a', 'o', 'u'],
    'i': ['e', 'a', 'u', 'o'],
    'o': ['u', 'a', 'e', 'i'],
    'u': ['o', 'a', 'e', 'i'],
}

# ── Load known signs from mappings.json ───────────────────────────────────────
_KNOWN: set = set()

def _load_known(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'data', 'mappings.json')
    with open(path) as f:
        data = json.load(f)
    for k in data:
        # Accept only short, vowel-containing keys (filters out metadata entries)
        if len(k) <= 4 and any(c in _VOWELS for c in k):
            _KNOWN.add(k)

_load_known()


# ── Core helpers ──────────────────────────────────────────────────────────────
def _cv_key(consonant: str, vowel: str) -> Sign:
    """
    Build a Sign for the given Maya consonant + Spanish vowel.
    Falls back to the nearest available sign if the exact one is missing.
    """
    v = VOWEL_NORM.get(vowel, vowel)
    key = consonant + v if consonant else v
    if key in _KNOWN:
        return Sign(key, True)
    for alt in _VOWEL_FALLBACK.get(v, []):
        candidate = consonant + alt if consonant else alt
        if candidate in _KNOWN:
            return Sign(candidate, False)
    return Sign(key, False)   # no fallback found; renderer will show placeholder


def _onset_maya(onset_tokens: list, nucleus_tokens: list) -> str:
    """
    Resolve a list of Spanish onset consonant tokens to a single Maya consonant.

    For onset clusters (e.g. ['b','r'] in 'bro') only the first consonant is
    used — Maya syllabograms are CV, so CC onsets cannot be represented.
    Context-sensitive rules apply to 'c' and 'g'.
    """
    if not onset_tokens:
        return ''
    raw = onset_tokens[0]   # primary consonant of any cluster
    if raw == 'c':
        v = VOWEL_NORM.get(nucleus_tokens[0] if nucleus_tokens else '', '')
        return 's' if v in ('e', 'i') else 'k'
    if raw == 'g':
        v = VOWEL_NORM.get(nucleus_tokens[0] if nucleus_tokens else '', '')
        return 'j' if v in ('e', 'i') else 'k'
    return ONSET.get(raw, raw)


def _parse_syllable(syl: str):
    """
    Split a syllable string into (onset_tokens, nucleus_tokens, coda_tokens).
    Re-uses the digraph tokenizer from syllabifier_es.
    """
    tokens = _tokenize(syl)
    i = 0
    onset = []
    while i < len(tokens) and not _is_vowel(tokens[i]):
        onset.append(tokens[i])
        i += 1
    nucleus = []
    while i < len(tokens) and _is_vowel(tokens[i]):
        nucleus.append(tokens[i])
        i += 1
    coda = tokens[i:]
    return onset, nucleus, coda


# ── Public API ────────────────────────────────────────────────────────────────
def map_syllable(syl: str) -> list:
    """
    Map one Spanish syllable string to a list of Sign objects.

    Patterns:
      V        → [v_sign]
      CV       → [cv_sign]
      C+dipth  → [cv1_sign, v2_sign, ...]   (diphthong split)
      CVC      → [cv_sign, dummy_sign]       (synharmony: dummy echoes nucleus vowel)
      CVCC     → [cv_sign, dummy1, dummy2]
    """
    onset_toks, nucleus_toks, coda_toks = _parse_syllable(syl)
    if not nucleus_toks:
        return [Sign(f'?{syl}', False)]

    maya_onset = _onset_maya(onset_toks, nucleus_toks)
    signs = []

    # Onset + first nucleus vowel
    signs.append(_cv_key(maya_onset, nucleus_toks[0]))

    # Diphthong / triphthong tail → pure vowel signs
    for v in nucleus_toks[1:]:
        signs.append(_cv_key('', v))

    # Synharmony: each coda consonant → dummy CV sign.
    # The dummy vowel echoes the last nucleus vowel (synharmony rule).
    echo = nucleus_toks[-1]
    for coda_tok in coda_toks:
        maya_coda = ONSET.get(coda_tok, coda_tok)
        signs.append(_cv_key(maya_coda, echo))

    return signs


def map_word(syllables: list) -> list:
    """Map a list of syllables (from syllabifier_es.syllabify) to Maya Signs."""
    result = []
    for syl in syllables:
        result.extend(map_syllable(syl))
    return result
