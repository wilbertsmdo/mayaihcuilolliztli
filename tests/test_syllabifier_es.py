import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from syllabifier_es import syllabify


class TestSyllabifyES(unittest.TestCase):

    def check(self, word, expected):
        self.assertEqual(syllabify(word), expected, f"'{word}'")

    # ── Simple CV ──────────────────────────────────────────────────────────────
    def test_simple_cv(self):
        self.check('casa',  ['ca', 'sa'])
        self.check('puma',  ['pu', 'ma'])
        self.check('mono',  ['mo', 'no'])

    # ── Digraph ch ────────────────────────────────────────────────────────────
    def test_digraph_ch(self):
        self.check('chocolate', ['cho', 'co', 'la', 'te'])
        self.check('chico',     ['chi', 'co'])
        self.check('mucho',     ['mu', 'cho'])

    # ── Digraph ll ────────────────────────────────────────────────────────────
    def test_digraph_ll(self):
        self.check('llave',    ['lla', 've'])
        self.check('estrella', ['es', 'tre', 'lla'])
        self.check('silla',    ['si', 'lla'])

    # ── Digraph rr ────────────────────────────────────────────────────────────
    def test_digraph_rr(self):
        self.check('perro',  ['pe', 'rro'])
        self.check('guerra', ['gue', 'rra'])

    # ── Digraph qu ────────────────────────────────────────────────────────────
    def test_digraph_qu(self):
        self.check('queso',    ['que', 'so'])
        self.check('tranquilo',['tran', 'qui', 'lo'])

    # ── Inseparable onset clusters ────────────────────────────────────────────
    def test_insep_clusters(self):
        self.check('libro',  ['li', 'bro'])
        self.check('blanco', ['blan', 'co'])
        self.check('plato',  ['pla', 'to'])
        self.check('tren',   ['tren'])
        self.check('flor',   ['flor'])
        self.check('gloria', ['glo', 'ria'])

    # ── Diphthongs ────────────────────────────────────────────────────────────
    def test_diphthong_weak_strong(self):
        self.check('ciudad', ['ciu', 'dad'])
        self.check('baile',  ['bai', 'le'])
        self.check('hielo',  ['hie', 'lo'])
        self.check('viaje',  ['via', 'je'])

    def test_diphthong_strong_weak(self):
        self.check('causa', ['cau', 'sa'])
        self.check('euro',  ['eu', 'ro'])
        self.check('deuda', ['deu', 'da'])

    def test_diphthong_weak_weak(self):
        self.check('ruido', ['rui', 'do'])
        self.check('cuidar',['cui', 'dar'])

    # ── Triphthongs ───────────────────────────────────────────────────────────
    def test_triphthong(self):
        self.check('buey', ['buei'])   # y → i normalization + triphthong
        self.check('miau', ['miau'])

    # ── Hiatus ────────────────────────────────────────────────────────────────
    def test_hiatus_strong_strong(self):
        self.check('poeta',   ['po', 'e', 'ta'])
        self.check('maestro', ['ma', 'es', 'tro'])
        self.check('aéreo',   ['a', 'é', 're', 'o'])

    def test_hiatus_accented_weak(self):
        self.check('país',    ['pa', 'ís'])
        self.check('María',   ['ma', 'rí', 'a'])
        self.check('baúl',    ['ba', 'úl'])

    # ── Accent marks on strong vowels (don't break diphthongs) ───────────────
    def test_accented_strong(self):
        self.check('también', ['tam', 'bién'])
        self.check('corazón', ['co', 'ra', 'zón'])
        self.check('árbol',   ['ár', 'bol'])

    # ── Terminal y → i ────────────────────────────────────────────────────────
    def test_terminal_y(self):
        self.check('hay', ['hai'])
        self.check('muy', ['mui'])
        self.check('rey', ['rei'])
        self.check('hoy', ['hoi'])

    # ── Complex multi-syllable ────────────────────────────────────────────────
    def test_complex(self):
        self.check('universidad', ['u', 'ni', 'ver', 'si', 'dad'])
        self.check('construcción', ['cons', 'truc', 'ción'])

    # ── Edge cases ────────────────────────────────────────────────────────────
    def test_single_syllable(self):
        self.check('sol', ['sol'])
        self.check('mar', ['mar'])
        self.check('pan', ['pan'])

    def test_single_vowel(self):
        self.check('a', ['a'])
        self.check('o', ['o'])

    def test_empty(self):
        self.check('', [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
