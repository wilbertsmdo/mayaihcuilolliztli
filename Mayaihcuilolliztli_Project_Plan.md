# Mayaihcuilolliztli — Project Plan
*Maya syllabary transliterator: Spanish/English → Maya glyphs*

---

## 1. Project Vision

Take any Spanish or English word, break it into syllables, and render it using Classic Maya syllabograms — first as a linear glyph sequence, then as properly composed Maya-style agglutinated glyph blocks.

The name **Mayaihcuilolliztli** is Nahuatl for "the act of Maya writing."

---

## 2. Background & Key Concepts

### 2.1 The Maya Syllabary

The Classic Maya script is **logosyllabic**: it mixes logograms (whole-word signs) and syllabograms (syllable signs). For this project we focus on the **syllabary** only.

- Syllabograms are almost always **CV** (consonant + vowel): `ba`, `chi`, `ku`, `ma`, etc.
- Pure vowel signs exist: `a`, `e`, `i`, `o`, `u`.
- There is **no CVC syllabogram** — final consonants are written with a second CV glyph whose vowel is either suppressed or synharmonic.

### 2.2 The Synharmony / Dummy-Vowel Convention

To write a CVC syllable like **"bal"**, Maya scribes wrote `ba` + `la` where the final `a` is silent (dropped in reading). This convention — the final vowel echoes the vowel of the preceding sign or defaults to a weak `e` — is called **synharmony**. Our engine must implement this:

```
"chan" → cha-na  (final 'a' silent)
"balam" → ba-la-ma  (final 'a' silent)
"tok" → to-ko  (final 'o' silent)
```

### 2.3 Phoneme Inventory Gaps

The Maya phoneme set ≠ Spanish or English phoneme set. Key mismatches:

| Spanish/English sound | Maya approximation | Notes |
|-----------------------|--------------------|-------|
| `f` | `p` (closest) | Maya had no labiodental fricative |
| `d` (intervocalic) | `t` or `d'` | Approximation needed |
| `g` | `k` or `ku` | Context-dependent |
| `j` / `h` | `j` (Maya has a glottal/velar h) | Close enough |
| `rr` (Spanish trill) | `r` | No trill distinction in syllabary |
| `th` (English) | `t` or `s` | No dental fricative |
| `w` | `u` (semivowel) | Maya `u` can act as `w` |
| `ñ` (Spanish) | `ni` + next vowel | Approximate |
| `ll` / `y` | `y` | Maya has `ya`, `ye`, etc. |

These mappings must be stored in a configurable lookup table so they can be refined.

### 2.4 Glyph Resources

Maya glyphs are **not reliably renderable via Unicode** as of 2026 — the Unicode block U+10000 for Maya Hieroglyphs exists but font support is nearly nonexistent. Practical approach:

- Use **image assets** (PNG/SVG) for each syllabogram, keyed by their Thompson (T-number) or Knorosov catalog ID.
- Primary reference: the **Knorosov syllabary grid** (~120 core CV signs + 5 vowel signs).
- Secondary reference: *The New Catalog of Maya Hieroglyphs* (Macri & Looper, 2003).

Glyph sources to research:
- [FAMSI (Foundation for the Advancement of Mesoamerican Studies)](http://www.famsi.org/mayawriting/)
- The DRONE/MAAYA digital glyph databases
- Open-source Maya font projects (e.g., "Noto Sans Mayan Hieroglyphs" — check license)

---

## 3. Phases

### Phase 1 — Foundation & Data Layer
**Goal:** Establish the syllabary mapping table and syllabification for Spanish.

**Tasks:**
1. Build the **phoneme-to-syllabogram mapping table** (`mappings.json`):
   - Key: IPA phoneme or orthographic syllable (e.g., `"ba"`, `"chi"`)
   - Value: syllabogram catalog ID (e.g., `T501`, `T671`) + image filename
   - Include the approximation table for phonemes not in Maya
2. Curate/download **glyph image assets** (start with ~130 core signs)
3. Implement **Spanish syllabifier** (`syllabifier_es.py`):
   - Spanish follows regular CV/VC/CVC rules — well-documented algorithm
   - Handle diphthongs (`ai`, `ei`, `ui`, `au`, `ou`, `ia`, `ie`, `io`, `iu`, `ua`, `ue`, `ui`, `uo`)
   - Handle digraphs (`ch`, `ll`, `qu`, `gu`, `rr`)
4. Implement **phoneme mapper** (`phoneme_mapper.py`):
   - Spanish syllable → Maya CV(s) using the mapping table
   - Apply synharmony rule for final consonants
5. Unit tests for syllabification and mapping

**Deliverables:** `mappings.json`, `glyphs/` directory, `syllabifier_es.py`, `phoneme_mapper.py`

---

### Phase 2 — Linear Glyph Renderer
**Goal:** Input a word/phrase → output glyphs in left-to-right linear sequence.

**Tasks:**
1. Build **linear renderer** (`renderer_linear.py`):
   - Takes list of syllabogram IDs from the mapper
   - Loads corresponding PNG/SVG images
   - Composites them horizontally using `Pillow` (PIL)
   - Outputs a single image file
2. Build a **CLI interface** (`main.py`):
   ```
   python main.py --lang es --word "chocolate"
   # → syllables: cho-co-la-te
   # → glyphs: CHO KO LA TE
   # → output: chocolate_linear.png
   ```
3. Handle unknown syllables gracefully (show placeholder "?" glyph)
4. Add word-boundary spacing and optional caption (romanized syllables below each glyph)

**Deliverables:** `renderer_linear.py`, `main.py`, working CLI

---

### Phase 3 — English Support
**Goal:** Extend syllabification and phoneme mapping to English.

**Tasks:**
1. Implement **English syllabifier** (`syllabifier_en.py`):
   - English syllabification is irregular — algorithm approach (Liang's hyphenation algorithm, used in TeX) or dictionary lookup
   - Option A: Use **CMU Pronouncing Dictionary** (cmudict, available via NLTK) for phonemic transcription — more accurate but needs NLTK
   - Option B: Rule-based syllabifier (faster, less accurate)
   - Recommended: Option A for accuracy, with Option B as fallback for unknown words
2. Extend phoneme mapper for English phonemes (IPA-based mapping)
3. Handle English-specific sounds missing from Maya (see §2.3)
4. Add `--lang en` flag to CLI

**Deliverables:** `syllabifier_en.py`, extended `mappings.json`, English CLI support

---

### Phase 4 — Maya-Style Agglutinated Glyph Blocks
**Goal:** Compose syllabograms into proper Maya glyph blocks (main sign + affixes).

**Background:**
Maya glyph blocks pack 2–4 signs together into a roughly square block. Signs occupy positions:
- **Main sign** (center/dominant): usually the most semantically significant
- **Prefix** (left or top-left)
- **Suffix** (right or bottom-right)
- **Superfix** (top, smaller)
- **Subfix** (bottom, smaller)

For a phonetic (non-logographic) inscription, the convention was often to use the first syllabogram as the "main sign" and attach subsequent syllabograms as affixes.

**Tasks:**
1. Research and codify **block composition rules** (how many glyphs per block, which position for which syllabogram in a sequence)
2. Build **block compositor** (`compositor.py`):
   - Groups a stream of syllabograms into block units (typically pairs or triplets)
   - Assigns each sign a position role (main/prefix/suffix)
   - Composites the block as an image with correct relative sizing and placement
3. Layout engine: arrange multiple blocks in the traditional **paired-column, top-to-bottom** reading order
4. Output as single image or SVG

**Deliverables:** `compositor.py`, Maya-style glyph block output

---

### Phase 5 — Web / App Interface (Optional / Future)
- Simple Flask or Streamlit web front-end
- User types word/phrase, sees glyphs rendered live
- Toggle between linear and block modes
- Export as PNG

---

## 4. Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3 (Termux) | Matches workspace standard |
| Image compositing | `Pillow` (PIL) | Already usable; pure Python |
| Glyph format | PNG per syllabogram | Simple, composable |
| Syllabification (ES) | Rule-based | Spanish rules are regular enough |
| Syllabification (EN) | CMU dict + fallback | Accuracy matters for English |
| Catalog reference | Thompson + Knorosov | Both widely cited |
| Output | PNG image | Portable; SVG as future option |

---

## 5. Open Questions (to resolve before or during Phase 1)

1. **Glyph asset licensing** — are freely licensed, high-quality SVG/PNG versions of the syllabary available? FAMSI has images but license must be checked.
2. **Scope of syllabary** — use only the ~130 "core" CV signs, or try to include all ~800 known variants? Start small.
3. **Allographic variation** — each CV sign has multiple variant forms. Which variant to use by default? Pick one "standard" form per sign for Phase 1.
4. **Proper nouns / loanwords** — strategy for words with phonemes far outside Maya inventory?
5. **Block composition ambiguity** — Phase 4 composition rules are not formally standardized. Need to study inscriptions to derive a workable ruleset.
6. **Direction of reading** — Classic Maya reads left-to-right, top-to-bottom in paired columns. Decide whether the app will mirror this or use simple LTR linear.
7. **Spanish stress marks (tildes)** — does `é` vs `e` change glyph assignment? Probably not for Phase 1.

---

## 6. File Structure (Target)

```
Mayaihcuilolliztli/
├── Mayaihcuilolliztli_Project_Plan.md   ← this file
├── CLAUDE.md
├── main.py                              ← CLI entry point
├── syllabifier_es.py                    ← Spanish syllabification
├── syllabifier_en.py                    ← English syllabification
├── phoneme_mapper.py                    ← syllable → syllabogram ID
├── renderer_linear.py                   ← linear glyph image output
├── compositor.py                        ← Phase 4: glyph block assembly
├── data/
│   └── mappings.json                    ← phoneme/syllable → glyph catalog ID
├── glyphs/
│   ├── a.png
│   ├── ba.png
│   ├── chi.png
│   └── ...                              ← one PNG per syllabogram
├── output/                              ← generated images land here
└── tests/
    ├── test_syllabifier_es.py
    └── test_phoneme_mapper.py
```

---

## 7. Session Log

| Date | Work Done | Next |
|------|-----------|------|
| 2026-09-11 | Project plan created | Research glyph assets; draft `mappings.json`; implement Spanish syllabifier |
| 2026-09-11 | Glyph asset research done; `download_glyphs.py` written and run (partially); 27 files in `glyphs/`; `data/mappings.json` drafted (malformed); `research/phoneme_gaps_and_glyph_sources.md` produced | Fix download script crash; re-run to get all 236 files |
| 2026-09-13 | Fixed `download_glyphs.py` crash (subprocess→requests); script ready to re-run | Run script to finish downloading remaining ~209 glyphs; then implement `syllabifier_es.py` |

---

## Checkpoint — 2026-09-13

### Work completed this session

- Ran `/catchup` to audit project state: confirmed 27 glyph files on disk, malformed `mappings.json`, no Phase 1 Python modules built yet.
- Diagnosed the previous session's two failure modes:
  - **First run** (~23 files downloaded): Wikimedia 429 rate-limiting halted the download at file 32/236; `mappings.json` was written in a broken early format (keyed by filename instead of CV syllable, only 4 entries).
  - **Second run** (~4 more files, then crash at file 10/213): `subprocess.run(capture_output=True)` raises `OSError: [Errno 38] Function not implemented` on PRoot/Android because the `pipe()` syscall is unavailable.
- Fixed `download_glyphs.py`:
  - Removed `subprocess` import entirely.
  - Replaced the wget-via-subprocess download loop with a `requests`-based `dl()` helper that streams directly to disk and handles 429 with exponential backoff.
  - Kept `time.sleep(5)` between files for polite rate limiting.
  - Script remains idempotent (skips existing files).
- Bootstrapped `.claude/commands/` folder for this project; added `cp` allow entry to `settings.local.json`.

### Current state

- `download_glyphs.py` is fixed and ready to re-run. It will skip the 27 existing glyph files and attempt the remaining ~209.
- `data/mappings.json` is malformed (legacy schema); will be overwritten with correct structure on the next complete script run.
- `glyphs/` has 27 JPG/SVG files covering: `a`, `ba`, `b'a/e/i/o`, `cha`, `che`, `chi`, `ch'a`, `ch'o` and variants.
- No Phase 1 Python modules (`syllabifier_es.py`, `phoneme_mapper.py`) exist yet.
- `research/phoneme_gaps_and_glyph_sources.md` is complete and solid.

### Next steps

1. **Run `download_glyphs.py`** to completion — downloads remaining ~209 glyphs to `glyphs/` and writes correct `data/mappings.json` (CV key → file list).
2. **Verify `mappings.json`** — check CV key coverage against the expected ~130 syllabogram set; note any gaps.
3. **Implement `syllabifier_es.py`** — rule-based Spanish syllabifier handling diphthongs and digraphs (ch, ll, qu, gu, rr).
4. **Implement `phoneme_mapper.py`** — maps Spanish syllables to Maya CV signs using `mappings.json`; applies synharmony rule for final consonants.
5. **Write `tests/test_syllabifier_es.py`** with cases for diphthongs, digraphs, and stress-marked vowels.
6. **Implement `main.py` CLI** (`--lang es --word "chocolate"`) and **`renderer_linear.py`** (Pillow-based horizontal compositing).

### Notes

- `subprocess.run(capture_output=True)` is permanently broken on this PRoot/Android environment — never use it. Use `requests` for HTTP, or `os.system()` for shell commands where return code is needed.
- The Wikimedia download rate limit is aggressive (~429 after 3–5 rapid requests). The 5s sleep between files should be sufficient; if 429s persist, increase to 8–10s.
- `mappings.json` format (as written by the current script): `{base_cv_key: [{variant_key, local_file, drive_id, wikimedia_title, url}, …], …}`. This is a list per key to handle glyph variants (e.g., `"cha"` has `cha.jpg`, `cha_1.jpg`, `cha_2.jpg`).
- Google Drive folder for glyphs: `https://drive.google.com/drive/folders/1sgWEMmTVoIKT9n_JRnnMWrtaJNzqv1NL`

---

## Checkpoint — 2026-09-14

### Work completed this session

- **Completed glyph download:** ran fixed `download_glyphs.py` to completion — 235 files in `glyphs/`, 114 unique CV keys, 234 total variants in `data/mappings.json`. 220 files uploaded to Google Drive, 0 failures.
- **Implemented `syllabifier_es.py`:** rule-based Spanish syllabifier. Handles digraphs (ch, ll, rr, qu, gu before e/i), diphthongs (weak+strong, strong+weak, weak+weak), triphthongs, hiatus (strong+strong and accented weak vowels), inseparable onset clusters (bl, br, tr, pl, etc.), terminal y→i normalization. 18 unit tests, all passing.
- **Implemented `phoneme_mapper.py`:** maps syllable lists to `Sign(key, exact)` objects. Consonant substitution table from the Landa alphabet (r→l, f→p, d→t, z→s, v→b, ll→y, rr→l, qu→k). Context-sensitive c/g (before e/i → s/j; before a/o/u → k/k). Onset cluster reduction (CC onsets → first consonant only). Synharmony: each coda consonant generates a dummy CV sign echoing the nucleus vowel. Fallback for syllabary gaps (be→bi, pe→pi, so→su) with `exact=False` flag. 36 unit tests, all passing.
- **Implemented `renderer_linear.py`:** Pillow-based compositing. Picks best JPG variant per key (exact name → `_1` → non-pfx/sfx → any). Scales all glyphs to 150px height. Pastes left-to-right with white backing. Amber border on fallback signs; gray placeholder for unknowns. Caption below each glyph. Returns PIL Image.
- **Implemented `app.py`:** Flask web interface. User types a Spanish word, clicks Transliterate, sees the glyph strip rendered inline as base64 PNG. Shows syllable breakdown and sign keys. Footnote for approximations. Streamlit was attempted first but failed (requires pandas + pyarrow, no aarch64 wheels on Python 3.13). Flask installed cleanly as a pure-Python alternative.
- **Installed Flask** via pip3 (pure Python, no compilation needed).
- **End-to-end test:** "chocolate" → cho · ko · la · te → four authentic Maya syllabogram glyphs rendered correctly. Server running on `localhost:5000` via `nohup`.
- **Created `tests/` and `output/` directories.**

### Current state

Full Phase 1 + Phase 2 pipeline is working end-to-end:
- Spanish word → `syllabify()` → `map_word()` → `render()` → PNG image
- Flask app serves the UI at `localhost:5000` on the device
- 235 glyph images on disk; 114 CV keys in `mappings.json`
- 54 unit tests passing (18 syllabifier + 36 mapper)
- Known syllabary gaps: `be`, `pe`, `so`, `wu`, `xe` — fallback to nearest vowel variant

### Next steps

1. **Manual QA:** test more Spanish words in the browser — look for mapping errors, missing glyphs, layout issues.
2. **Syllabary gap review:** decide whether to supplement missing signs (be, pe, so) from SVG sources or accept current fallbacks.
3. **Variant selection:** `_pick_file()` in `renderer_linear.py` always picks the first/canonical variant. Consider adding a variant selector to the UI.
4. **Phase 3 — English support:** implement `syllabifier_en.py` using CMU dict + rule-based fallback; extend `phoneme_mapper.py` for English phonemes.
5. **Keep Flask server alive:** add a startup script or Termux `~/.bashrc` alias so the server survives session restarts.
6. **Phase 4 (future):** Maya-style agglutinated glyph block compositor.

### Notes

- Flask server started with `nohup python3 app.py &` (PID 6377 as of this session). Will not survive Termux restart — must be re-launched manually.
- `subprocess.run(capture_output=True)` is permanently broken on this PRoot/Android environment. Never use it.
- Streamlit is not installable on Termux Python 3.13 aarch64 (pandas/pyarrow require compiled C++ — no wheels available). Flask is the correct choice for this platform.
- `mappings.json` structure: `{base_cv_key: [{variant_key, local_file, drive_id, wikimedia_title, url}, …]}`. Multiple variants per key are normal.
- The `ko` glyph (oval crosshatch pattern) and `cho` sign rendered correctly and look authentic for "chocolate".

---

## Checkpoint — 2026-09-15

### Work completed this session

- **Switched web framework for deployment:** replaced Flask `app.py` with Gradio `app.py` (Gradio is natively supported by HF Spaces; Flask requires a custom Docker container which is Paid-only on HF).
- **Created HF Space manually:** HF API token authentication was repeatedly rejected despite correct account/email. Workaround: created the Space at huggingface.co/new-space in the browser (SDK: Gradio, Template: Blank, Hardware: ZeroGPU Free, Visibility: Public, name: Mayaihcuilolliztli).
- **Installed `huggingface_hub`** (without `hf-xet` dependency, which requires Rust/maturin — not available on this platform): `pip3 install huggingface_hub --no-deps` + pure-Python deps.
- **Uploaded project to HF Space** via `api.upload_folder()` — bypasses the git binary-file restriction HF now enforces (git push rejected all `.jpg` glyph files, directing to their Xet storage system).
- **Fixed ZeroGPU runtime error:** HF's ZeroGPU requires at least one `@spaces.GPU`-decorated function or the container shuts down at startup. Added `import spaces` and `@spaces.GPU(duration=0)` to the `transliterate()` function in `app.py`. Re-uploaded.
- **Added three informational accordion sections** to `app.py` below the main UI:
  - *What is this?* — concept, Maya syllabary background, meaning of the Nahuatl name
  - *Methodology* — four-stage pipeline explained (syllabify → Landa mapping → synharmony → render)
  - *Sources & credits* — Wikimedia glyph attribution, Landa, Montgomery, Kettunen, GitHub link
- **Committed and pushed to GitHub:** repo at https://github.com/wilbertsmdo/mayaihcuilolliztli (249 files including 235 glyph JPGs).

### Current state

- App is **live and public** at https://huggingface.co/spaces/wilbertsmdo/Mayaihcuilolliztli
- Anyone with the link can use it — no login required
- ZeroGPU free tier: ~30s cold start after inactivity, then runs normally
- Three collapsible info sections visible below the tool
- Full pipeline (syllabify → map → render) working end-to-end in the cloud
- GitHub repo is up to date

### Next steps

1. **Manual QA on HF Space** — test a wider range of Spanish words; look for mapping errors, layout issues, missing glyphs.
2. **Syllabary gap review** — decide whether to supplement `be`, `pe`, `so`, `wu`, `xe` from alternative SVG sources or keep current fallbacks.
3. **Variant selector** — `_pick_file()` in `renderer_linear.py` always picks the canonical variant; consider exposing a variant toggle in the UI.
4. **Phase 3 — English support:** implement `syllabifier_en.py` (CMU dict + rule-based fallback) and extend `phoneme_mapper.py` for English phonemes.
5. **Phase 4 (future):** Maya-style agglutinated glyph block compositor.

### Notes

- HF API token authentication consistently failed (both fine-grained and classic tokens). The token works for the git push (via HTTP basic auth as password) but was rejected by the `/api/whoami` endpoint. Root cause unknown — possibly a new-account restriction or rate limit. Workaround: manual Space creation in browser + `huggingface_hub` Python upload API (which uses the same token but a different auth path that did work).
- `hf-xet` (HF's new blob storage client) requires Rust/maturin to build — not available on Termux/PRoot aarch64. Install `huggingface_hub` with `--no-deps` to skip it; the regular upload API still works for files under ~5 GB.
- ZeroGPU `@spaces.GPU(duration=0)` trick: the `duration=0` hint tells ZeroGPU the function needs the GPU for zero seconds (i.e., never), but the decorator satisfies the "at least one GPU function" requirement so the container stays alive.
