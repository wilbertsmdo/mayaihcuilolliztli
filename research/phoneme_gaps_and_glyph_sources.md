# Mayaihcuilolliztli — Research Memo
**Phoneme Gaps & Glyph Image Sources**
Date: 2026-09-11

---

## Part 1 — Glyph Image Sources

### 1.1 PRIMARY SOURCE (recommended) — Wikimedia Commons "Maya Syllabaries"
- **URL:** https://commons.wikimedia.org/wiki/Category:Maya_glyphs (subcategory: Maya Syllabaries)
- **Files:** 236 JPG images
- **Naming convention:** `[CV] Syllabogramme.jpg` — e.g. `KA Syllabogramme.jpg`, `JI Syllabogramme.jpg`, `K'A Syllabogramme.jpg`
- **License:** Creative Commons Attribution-ShareAlike (CC-BY-SA)
- **Format:** JPG
- **Action:** Download programmatically via MediaWiki API; parse filenames to build `cv → filename` mapping

### 1.2 SECONDARY SOURCE — Wikimedia Commons "Maya glyphs in SVG"
- **URL:** https://commons.wikimedia.org/wiki/Category:Maya_glyphs_in_SVG
- **Files:** 100 SVG files
- **License:** CC-BY-SA
- **Notes:** SVG preferred for scaling; may cover logograms more than syllabograms — check overlap with syllabary files.

### 1.3 REFERENCE — Landa Alphabet images
- **URL:** https://commons.wikimedia.org/wiki/Category:Landa_alphabet
- **Files:** 30 images (the colonial-era Spanish-letter → Maya glyph mapping, c. 1566)
- **Notes:** Use to validate our phoneme approximation table against the historical source.

### 1.4 REFERENCE — mayadecipherment.com Syllabary Chart (Houston/Stuart/Zender)
- **URL:** https://mayadecipherment.com/wp-content/uploads/2013/09/maya-syllabary-v2.pdf
- **Size:** 608 KB PDF
- **Notes:** Best current scholarly syllabary grid. Cannot extract images programmatically (binary PDF). Download manually for human reference.

### 1.5 SUPPLEMENTARY — FAMSI Resources
- **URL:** https://www.famsi.org/mayawriting/
- **Notes:** T-Numbers catalog (Thompson numbering) and Inga Calvin's Maya Hieroglyphics Study Guide. All glyph images embedded in PDFs — not individually downloadable. Best used as reference.

### 1.6 FONT OPTION — Dafont.com "Mayan Glyphs"
- **URL:** https://www.dafont.com/mayan-glyphs.font
- **Notes:** TrueType dingbat font covering Thompson T719–T781. Limited scope, but renderable as text glyphs if needed.

### Recommended Strategy for Glyph Assets
1. Download all 236 files from Wikimedia "Maya Syllabaries" via MediaWiki API (no login required)
2. Parse filenames → build initial `data/mappings.json` (cv_key → filename)
3. Cross-reference against mayadecipherment.com PDF (manual check) to confirm coverage
4. For any gaps, check the SVG subcategory or extract from FAMSI PDFs

**MediaWiki API endpoint for bulk download:**
```
https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers
  &cmtitle=Category:Maya_Syllabaries&cmlimit=500&cmtype=file&format=json
```
Then for each file, fetch the direct image URL via `action=query&titles=File:XXX&prop=imageinfo&iiprop=url`.

---

## Part 2 — Classic Maya Phoneme Inventory

The Classic Maya syllabary covers:

**Vowels:** a, e, i, o, u
*(Long vowels VV existed but are not encoded separately for Phase 1)*

**Consonants:**

| Category | Sounds |
|----------|--------|
| Stops (plain) | p, t, k |
| Stops (ejective / glottalized) | p', t', k', b' |
| Affricates | tz, tz', ch, ch' |
| Fricatives | s, x (=/ʃ/), j (=/x/ or /h/) |
| Nasals | m, n |
| Laterals | l |
| Glides | w, y |
| Glottal stop | ' (ʼ) |

**Total CV grid cells:** ~130 (some cells have no attested sign)
**Commonly used syllabograms:** ~100 active signs

---

## Part 3 — Phoneme Gaps: Sounds Absent from Classic Maya

### 3.1 Historical Precedent — The Landa Alphabet (c. 1566)

Bishop Diego de Landa asked Maya scribes to draw the glyph for each Spanish letter sound (Relación de las cosas de Yucatán). The scribes used the CV syllabogram whose onset consonant best approximated the Spanish letter. This is the primary historical source for our approximation table.

**Landa's documented substitutions (Spanish letter → Maya sign):**

| Spanish Letter | Maya Sign Used | Notes |
|---------------|----------------|-------|
| A | a (pure vowel) | Direct |
| B | b' | Direct (glottalized) |
| C | ka | K onset |
| CH | ch | Direct |
| D | ta | T onset (no voiced stop) |
| E | e (pure vowel) | Direct |
| F | pa | P onset (no labiodental fricative) |
| G | ka | K onset (no voiced velar) |
| H | ha | J/H sign |
| I | i (pure vowel) | Direct |
| L | la | Direct |
| M | ma | Direct |
| N | na | Direct |
| O | o (pure vowel) | Direct |
| P | pa | Direct |
| R | la | L onset (no alveolar trill in Maya) |
| S | sa | Direct |
| T | ta | Direct |
| U | u (pure vowel / semivowel) | Direct |
| V | ua / b'a | U semivowel or b' |
| X | xa | x (=/ʃ/) |
| Y | ya | Direct |
| Z | sa | S onset |

*Source: Landa, D. de (c. 1566). Relación de las cosas de Yucatán. Manuscript.*

### 3.2 Full Phoneme Gap Table (Spanish + English)

| Sound | IPA | Absent from Maya? | Recommended Glyph Substitution | Rationale |
|-------|-----|-------------------|-------------------------------|-----------|
| F | /f/ | YES | **P** | Closest labial. Landa documented P for F. |
| V | /v/ | YES | **B'** or **U** (semivowel) | Voiced labiodental → glottalized labial, or U before vowel |
| D | /d/ | YES | **T** | Voiced dental → unvoiced T. Colonial texts confirm. |
| G (hard) | /g/ | YES | **K** | Voiced velar → unvoiced K. |
| G (soft, Esp.) | /x/ | NO | **J** (direct) | Spanish "ge/gi" = /x/ = Maya J sign |
| R | /r/ | YES | **L** | No alveolar trill. Landa documented R → L. Knorosov confirmed. |
| RR | /r:/ | YES | **L** | Same as R. |
| Ñ | /ɲ/ | YES | **NI** + following vowel (or **Y** before vowels) | Palatal nasal → N + I glide. "Ña" → ni-a; or treat as Y onset where Y signs exist. |
| LL (Español) | /ʎ/ or /j/ | PARTIAL | **Y** | In modern Spanish LL = /j/; Maya has Y onset directly (ya, ye, yi, yo, yu). |
| TH (Eng., voiceless) | /θ/ | YES | **T** | Dental fricative → T. |
| TH (Eng., voiced) | /ð/ | YES | **T** | Voiced dental fricative → T. |
| ZH | /ʒ/ | YES | **X** (Maya /ʃ/) | Closest palatal fricative. |
| Z (English) | /z/ | YES | **S** | Voiced sibilant → unvoiced S. |
| NG | /ŋ/ | YES | **N** + dummy **KA/KE** | Velar nasal: write N then dummy K+V for the final velar. |
| W | /w/ | NO | **W** (direct) | Maya has W onset: wa, we, wi, wo. |
| H (English) | /h/ | PARTIAL | **J** | Maya J covers both /x/ and /h/. Direct mapping. |
| SH | /ʃ/ | NO | **X** (direct) | Maya X = /ʃ/. |
| CH (English) | /tʃ/ | NO | **CH** (direct) | Maya has ch and ch' signs. |

### 3.3 Spanish-Specific Digraphs

| Digraph | Sound | Treatment |
|---------|-------|-----------|
| QU (before E/I) | /k/ | Map to **K** |
| GU (before E/I) | /g/ | Map to **K** (hard G approximation) |
| RR | /r:/ | Map to **L** |
| LL | /j/ | Map to **Y** |
| CH | /tʃ/ | Direct **CH** |

---

## Part 4 — Digital Humanities Precedents

| Project | Notes |
|---------|-------|
| **Text Database & Dictionary of Classical Maya** (Bonn University) | XML/TEI corpus. ALMAH tool for semi-automatic phonemic transliteration using numerical catalog IDs. English and Spanish output supported. |
| **Unicode Maya Hieroglyphs** (L2/23-020, 2023) | Effort to standardize ~1,000 signs in Unicode. As of 2026, font support still very limited. Confirms our choice to use image assets. |
| **ClassicMayan Portal** (classicmayan.org) | Working Paper 5: "A Digital Catalog of Maya Hieroglyphs" — numerical transliteration system. |
| **IDIOM** (Oxford Academic) | Digital research environment for Maya hieroglyphic text documentation and study. |

---

## Part 5 — Recommended Reference Downloads (manual)

1. **Kettunen & Helmke — Introduction to Maya Hieroglyphs (free PDF)**
   URL: https://www.wayeb.org/notes/wayeb_notes0026.pdf
   Contains: Full syllabic grid, sign lists, pronunciation guide. Standard workshop handbook since 2002.

2. **mayadecipherment.com Syllabary v2 (PDF)**
   URL: https://mayadecipherment.com/wp-content/uploads/2013/09/maya-syllabary-v2.pdf
   Contains: Current Houston/Stuart/Zender syllabary chart.

3. **FAMSI Inga Calvin Glyph Guide (PDF)**
   URL: https://www.famsi.org/mayawriting/calvin/glyph_guide.pdf
   Contains: Sign guide organized by category.

---

## Sources

- https://commons.wikimedia.org/wiki/Category:Maya_glyphs
- https://www.famsi.org/mayawriting/index.html
- https://www.omniglot.com/writing/mayan.htm
- https://www.britannica.com/topic/Maya-hieroglyphic-writing
- https://www.academia.edu/29008288/Origins_and_Development_of_the_Classic_Maya_Syllabary
- https://classicmayan.org/portal/doc/246
- https://dh2018.adho.org/en/achieving-machine-readable-mayan-text-via-unicode-blending-old-world-script-encoding-with-novel-digital-approaches/
- https://aclanthology.org/2022.lt4hala-1.16.pdf
- https://ankiweb.net/shared/info/1512794988
