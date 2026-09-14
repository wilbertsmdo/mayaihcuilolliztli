import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from syllabifier_es import syllabify
from phoneme_mapper import map_syllable, map_word, Sign


def keys(word):
    return [s.key for s in map_word(syllabify(word))]

def exact(word):
    return [s.exact for s in map_word(syllabify(word))]


class TestMapSyllable(unittest.TestCase):

    # ── Direct CV (all exact) ─────────────────────────────────────────────────
    def test_pure_cv(self):
        self.assertEqual(map_syllable('ma'), [Sign('ma', True)])
        self.assertEqual(map_syllable('la'), [Sign('la', True)])
        self.assertEqual(map_syllable('chi'), [Sign('chi', True)])

    def test_pure_vowel(self):
        self.assertEqual(map_syllable('a'), [Sign('a', True)])
        self.assertEqual(map_syllable('o'), [Sign('o', True)])

    # ── Consonant substitutions (Landa alphabet) ──────────────────────────────
    def test_r_to_l(self):
        self.assertEqual(map_syllable('ra'), [Sign('la', True)])
        self.assertEqual(map_syllable('ro'), [Sign('lo', True)])

    def test_f_to_p(self):
        self.assertEqual(map_syllable('fa'), [Sign('pa', True)])

    def test_d_to_t(self):
        self.assertEqual(map_syllable('da'), [Sign('ta', True)])

    def test_z_to_s(self):
        self.assertEqual(map_syllable('za'), [Sign('sa', True)])

    def test_v_to_b(self):
        self.assertEqual(map_syllable('va'), [Sign('ba', True)])

    def test_ll_to_y(self):
        self.assertEqual(map_syllable('lla'), [Sign('ya', True)])

    def test_rr_to_l(self):
        self.assertEqual(map_syllable('rra'), [Sign('la', True)])

    def test_qu_to_k(self):
        self.assertEqual(map_syllable('que'), [Sign('ke', True)])
        self.assertEqual(map_syllable('qui'), [Sign('ki', True)])

    # ── Context-sensitive consonants ──────────────────────────────────────────
    def test_c_before_front(self):
        # c before e/i → s
        self.assertEqual(map_syllable('ce')[0].key, 'se')
        self.assertEqual(map_syllable('ci')[0].key, 'si')

    def test_c_before_back(self):
        # c before a/o/u → k
        self.assertEqual(map_syllable('ca')[0].key, 'ka')
        self.assertEqual(map_syllable('co')[0].key, 'ko')

    def test_g_before_front(self):
        # g before e/i (soft g = /x/) → j
        self.assertEqual(map_syllable('ge')[0].key, 'je')
        self.assertEqual(map_syllable('gi')[0].key, 'ji')

    def test_g_before_back(self):
        # g before a/o/u (hard g) → k
        self.assertEqual(map_syllable('ga')[0].key, 'ka')
        self.assertEqual(map_syllable('go')[0].key, 'ko')

    # ── Onset cluster reduction (CC onset → first consonant only) ─────────────
    def test_cluster_br(self):
        # 'bro': onset=[b,r] → use b → bo
        self.assertEqual(map_syllable('bro'), [Sign('bo', True)])

    def test_cluster_tr(self):
        self.assertEqual(map_syllable('tra'), [Sign('ta', True)])

    def test_cluster_pl(self):
        self.assertEqual(map_syllable('pla'), [Sign('pa', True)])

    def test_cluster_fl(self):
        # f→p, so 'fla' → pa
        self.assertEqual(map_syllable('fla'), [Sign('pa', True)])

    # ── Diphthong splitting ───────────────────────────────────────────────────
    def test_diphthong_ie(self):
        # 'hie': onset=h, nucleus=i+e → hi, e
        result = map_syllable('hie')
        self.assertEqual(result[0], Sign('hi', True))
        self.assertEqual(result[1], Sign('e', True))

    def test_diphthong_ia(self):
        # 'via': onset=v→b, nucleus=i+a → bi, a
        result = map_syllable('via')
        self.assertEqual(result[0].key, 'bi')
        self.assertEqual(result[1], Sign('a', True))

    def test_diphthong_au(self):
        # 'cau': onset=c→k, nucleus=a+u → ka, u
        result = map_syllable('cau')
        self.assertEqual(result[0], Sign('ka', True))
        self.assertEqual(result[1], Sign('u', True))

    # ── Synharmony (coda consonant → dummy CV echoing nucleus vowel) ──────────
    def test_synharmony_r(self):
        # 'mar': onset=m, nucleus=a, coda=r→l, echo=a → ma + la
        self.assertEqual(map_syllable('mar'), [Sign('ma', True), Sign('la', True)])

    def test_synharmony_l(self):
        # 'bol': onset=b, nucleus=o, coda=l, echo=o → bo + lo
        self.assertEqual(map_syllable('bol'), [Sign('bo', True), Sign('lo', True)])

    def test_synharmony_n(self):
        # 'can': onset=c→k, nucleus=a, coda=n, echo=a → ka + na
        self.assertEqual(map_syllable('kan'), [Sign('ka', True), Sign('na', True)])

    def test_synharmony_accented(self):
        # 'zón': z→s, nucleus=ó→o, coda=n, echo=o → (so fallback) + no
        result = map_syllable('zón')
        # 'so' not in syllabary → fallback (not exact)
        self.assertFalse(result[0].exact)
        self.assertEqual(result[1], Sign('no', True))

    def test_double_coda(self):
        # 'cons': onset=c→k, nucleus=o, coda=[n,s], echo=o → ko + no + (so fallback)
        result = map_syllable('cons')
        self.assertEqual(result[0], Sign('ko', True))
        self.assertEqual(result[1], Sign('no', True))
        self.assertFalse(result[2].exact)   # 'so' not in syllabary


class TestMapWord(unittest.TestCase):

    def test_chocolate(self):
        # cho-co-la-te: all exact, no synharmony
        self.assertEqual(keys('chocolate'), ['cho', 'ko', 'la', 'te'])
        self.assertTrue(all(exact('chocolate')))

    def test_luna(self):
        self.assertEqual(keys('luna'), ['lu', 'na'])

    def test_casa(self):
        self.assertEqual(keys('casa'), ['ka', 'sa'])

    def test_arbol(self):
        # ár-bol → a (coda r→la) + bo (coda l→lo)
        self.assertEqual(keys('árbol'), ['a', 'la', 'bo', 'lo'])

    def test_libro(self):
        # li-bro → li + bo (cluster br → b)
        self.assertEqual(keys('libro'), ['li', 'bo'])

    def test_serpiente(self):
        # ser-pien-te → se+le (synharmony r) + pi+e+ne (diphthong+synharmony) + te
        result = keys('serpiente')
        self.assertEqual(result, ['se', 'le', 'pi', 'e', 'ne', 'te'])

    def test_corazon(self):
        # co-ra-zón → ko + la + (so~su, not exact) + no
        signs = map_word(syllabify('corazón'))
        self.assertEqual(signs[0], Sign('ko', True))
        self.assertEqual(signs[1], Sign('la', True))
        self.assertFalse(signs[2].exact)     # 'so' gap
        self.assertEqual(signs[3], Sign('no', True))

    def test_universidad(self):
        # u-ni-ver-si-dad
        result = keys('universidad')
        self.assertEqual(result[0], 'u')    # 'u' vowel sign
        self.assertEqual(result[1], 'ni')
        # ver: v→b, nucleus=e ('be' gap → fallback 'bi'), coda r→l echo e → le
        signs = map_word(syllabify('universidad'))
        self.assertFalse(signs[2].exact)   # 'be' not in syllabary → fallback
        self.assertEqual(result[3], 'le')
        self.assertEqual(result[4], 'si')
        # dad: ta + ta (d→t, coda d→t echo a)
        self.assertEqual(result[5], 'ta')
        self.assertEqual(result[6], 'ta')

    def test_gloria(self):
        # glo-ria: glo→ko (g hard +l cluster→g→k, onset cluster→k) + lo(synharm l?)
        # Wait: 'glo' onset=['g','l'], nucleus=['o']. g before o → k. cluster → use first='g'→k.
        # So 'glo' → ko. 'ria' → onset=['r']→l, nucleus=['i','a'] → li + a.
        result = keys('gloria')
        self.assertEqual(result[0], 'ko')
        self.assertEqual(result[1], 'li')
        self.assertEqual(result[2], 'a')

    def test_empty(self):
        self.assertEqual(map_word([]), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
