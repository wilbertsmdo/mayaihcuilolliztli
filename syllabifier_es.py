"""
syllabifier_es.py — Rule-based Spanish syllabifier.

Rules:
  - Digraphs (ch, ll, rr) and context-sensitive clusters (qu, gu before e/i)
    are treated as single consonant tokens.
  - Diphthongs: weak+strong, strong+weak, or weak+weak where neither weak
    vowel carries an accent mark.
  - Triphthongs: weak+strong+weak (absorbed after diphthong detection).
  - Hiatus: strong+strong, or any vowel adjacent to an accented weak vowel
    (í, ú) → each vowel starts its own syllable.
  - Consonant distribution between nuclei:
      1 consonant  → goes with the following syllable
      2 consonants → split, unless they form an inseparable onset cluster
                     (bl br cl cr dr fl fr gl gr pl pr tr tl) → both go right
      3 consonants → last two go right if they form a cluster, else last one
      4+           → last two go right if cluster, else last one
"""

_STRONG      = set('aeoáéó')
_WEAK        = set('iuíú')
_VOWELS      = _STRONG | _WEAK
_ACC_WEAK    = set('íú')

# Onset clusters that cannot be split across a syllable boundary
_INSEP = {
    'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr',
    'gl', 'gr', 'pl', 'pr', 'tr', 'tl',
}


def _tokenize(word):
    """Split word into grapheme tokens. Digraphs become single tokens."""
    tokens = []
    i = 0
    w = word.lower()
    while i < len(w):
        two = w[i:i+2]
        if two == 'qu':
            tokens.append('qu')
            i += 2
        elif two == 'gu' and i + 2 < len(w) and w[i+2] in 'eiéí':
            # gu before e/i: u is silent → single consonant token
            tokens.append('gu')
            i += 2
        elif two in ('ch', 'll', 'rr'):
            tokens.append(two)
            i += 2
        elif w[i] == 'ü':
            tokens.append('u')   # gü → g + u (pronounced)
            i += 1
        else:
            tokens.append(w[i])
            i += 1
    return tokens


def _is_vowel(t):    return len(t) == 1 and t in _VOWELS
def _is_strong(t):   return len(t) == 1 and t in _STRONG
def _is_weak(t):     return len(t) == 1 and t in _WEAK
def _is_acc_weak(t): return len(t) == 1 and t in _ACC_WEAK


def _diphthong(t1, t2):
    """True if t1 and t2 belong in the same nucleus (form a diphthong)."""
    if not (_is_vowel(t1) and _is_vowel(t2)):
        return False
    if _is_acc_weak(t1) or _is_acc_weak(t2):
        return False   # accented weak vowel always breaks → hiatus
    if _is_strong(t1) and _is_strong(t2):
        return False   # strong + strong → hiatus
    return True        # weak+strong, strong+weak, weak+weak → diphthong


def _find_nuclei(tokens):
    """Return (start, end) spans of vowel nuclei, merging diphthongs/triphthongs."""
    result = []
    i, n = 0, len(tokens)
    while i < n:
        if not _is_vowel(tokens[i]):
            i += 1
            continue
        start = i
        i += 1
        # Extend for diphthong
        while i < n and _is_vowel(tokens[i]) and _diphthong(tokens[i-1], tokens[i]):
            i += 1
        # Extend for triphthong: weak + strong already consumed;
        # absorb a trailing unaccented weak vowel.
        if (i < n
                and _is_vowel(tokens[i])
                and i - start == 2
                and _is_weak(tokens[start])
                and _is_strong(tokens[start + 1])
                and _is_weak(tokens[i])
                and not _is_acc_weak(tokens[i])):
            i += 1
        result.append((start, i))
    return result


def syllabify(word):
    """
    Break a Spanish word into syllables.
    Returns a list of syllable strings (all lowercase).
    """
    if not word:
        return []

    w = word.lower()
    # Terminal 'y' after a vowel acts as the vowel 'i' (e.g. hay→hai, rey→rei)
    if w.endswith('y') and len(w) > 1 and w[-2] in _VOWELS:
        w = w[:-1] + 'i'

    tokens = _tokenize(w)
    nuclei = _find_nuclei(tokens)

    if not nuclei:
        return [''.join(tokens)]  # no vowels — return as-is

    starts = [0] * len(nuclei)

    for i in range(len(nuclei) - 1):
        n_end    = nuclei[i][1]
        n2_start = nuclei[i + 1][0]
        cons     = list(range(n_end, n2_start))
        nc       = len(cons)

        if nc == 0:
            starts[i + 1] = n2_start
        elif nc == 1:
            starts[i + 1] = cons[0]
        elif nc == 2:
            c1, c2 = tokens[cons[0]], tokens[cons[1]]
            # Inseparable cluster → both go with the following syllable
            starts[i + 1] = cons[0] if c1 + c2 in _INSEP else cons[1]
        elif nc == 3:
            c2, c3 = tokens[cons[1]], tokens[cons[2]]
            starts[i + 1] = cons[1] if c2 + c3 in _INSEP else cons[2]
        else:
            c3, c4 = tokens[cons[-2]], tokens[cons[-1]]
            starts[i + 1] = cons[-2] if c3 + c4 in _INSEP else cons[-1]

    syllables = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(tokens)
        syllables.append(''.join(tokens[start:end]))
    return syllables
