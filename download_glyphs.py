"""
Download Maya syllabary images from Wikimedia Commons → glyphs/ + Google Drive.
Strategy: resolve URLs via MW API, then use wget (--wait=5 --random-wait)
which is the standard polite approach Wikimedia expects.
Phase 2: upload all local files to Drive.
Safe to restart — skips existing local files and Drive files.
"""
import sys, os, re, json, time
sys.path.insert(0, '/data/data/com.termux/files/usr/lib/python3.13/site-packages')

import requests
from urllib.parse import urlparse, unquote
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE     = '/storage/self/primary/PY_Projects/Macehualtlahtol/Mayaihcuilolliztli'
GLYPHS   = os.path.join(BASE, 'glyphs')
DATA     = os.path.join(BASE, 'data')
LOG      = os.path.join(BASE, 'download_glyphs.log')
URLFILE  = os.path.join(DATA, 'wikimedia_urls.txt')   # wget input file
TOKEN    = '/storage/self/primary/PY_Projects/Financial_Analysis_App/python/token.json'
PARENT_FOLDER_ID  = '1DKYYGfo523ZMu9N0cNdM0biUybgfUXlk'
DRIVE_FOLDER_NAME = 'Maya Syllabary Glyphs'

os.makedirs(GLYPHS, exist_ok=True)
os.makedirs(DATA,   exist_ok=True)

# Tee to log file
import builtins
_log = open(LOG, 'a', buffering=1)
_orig = builtins.print
def print(*a, **kw):
    _orig(*a, **kw)
    _orig(*a, **{**kw, 'file': _log, 'flush': True})
builtins.print = print

# ── Google Drive ───────────────────────────────────────────────────────────────
creds = Credentials.from_authorized_user_file(TOKEN)
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
drive = build('drive', 'v3', credentials=creds)

def get_or_create_folder(name, parent_id):
    q = (f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
         f"and '{parent_id}' in parents and trashed=false")
    res = drive.files().list(q=q, fields='files(id)').execute()
    if res['files']:
        return res['files'][0]['id']
    meta = {'name': name, 'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]}
    return drive.files().create(body=meta, fields='id').execute()['id']

drive_folder_id = get_or_create_folder(DRIVE_FOLDER_NAME, PARENT_FOLDER_ID)
print(f"Drive folder: https://drive.google.com/drive/folders/{drive_folder_id}")

# ── MediaWiki API ──────────────────────────────────────────────────────────────
MW_API  = 'https://commons.wikimedia.org/w/api.php'
SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'MayaihcuilolliztliBot/1.0 (educational; non-commercial)'})

def mw_get(params):
    for attempt in range(5):
        try:
            r = SESSION.get(MW_API, params=params, timeout=30)
            if r.status_code == 429:
                wait = int(r.headers.get('Retry-After', 2 ** attempt * 5))
                print(f"  MW API 429, waiting {wait}s…")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"  MW API error ({attempt+1}): {e}")
            time.sleep(2 ** attempt * 2)
    raise RuntimeError("MW API max retries")

def get_category_files(cat):
    files, cont = [], None
    while True:
        p = {'action':'query','list':'categorymembers','cmtitle':f'Category:{cat}',
             'cmtype':'file','cmlimit':'500','format':'json'}
        if cont: p['cmcontinue'] = cont
        d = mw_get(p)
        files.extend(d['query']['categorymembers'])
        cont = d.get('continue', {}).get('cmcontinue')
        if not cont: break
    return files

def get_image_urls_batch(titles):
    p = {'action':'query','titles':'|'.join(titles),
         'prop':'imageinfo','iiprop':'url','format':'json'}
    d = mw_get(p)
    result = {}
    for page in d['query']['pages'].values():
        if 'imageinfo' in page:
            result[page['title']] = page['imageinfo'][0]['url']
    return result

# ── CV key helpers ─────────────────────────────────────────────────────────────
def cv_key_from_title(title):
    name = re.sub(r'^File:', '', title).strip()
    name = re.sub(r'\.[a-zA-Z]{2,4}$', '', name).strip()
    for pat in [r'^Maya\s+Syllabary\s+', r'^Lettre\s+', r'^Glyphe\s+Maya\s+',
                r'^Glyphe\s+', r'^Signe\s+Maya\s+']:
        name = re.sub(pat, '', name, flags=re.IGNORECASE).strip()
    name = re.sub(r'\s+Syllabogramm?e.*$', '', name, flags=re.IGNORECASE).strip()
    variant_tag = ''
    m = re.search(r'\s+(pfx|sfx|prefix|suffix[e]?|bis|ter|\d+)$', name, re.IGNORECASE)
    if m:
        tag = m.group(1).lower().replace('suffixe','suf').replace('suffix','suf').replace('prefix','pfx')
        variant_tag = '_' + tag
        name = name[:m.start()].strip()
    base_key = name.lower().strip()
    return (base_key, base_key + variant_tag) if base_key else (None, None)

def safe_fname(variant_key, ext):
    return variant_key.replace("'", '_prime_').replace(' ', '_') + ext

# ── Build download plan ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("PHASE 1 — Resolving Wikimedia URLs")
print(f"{'='*60}")

titles_all = [f['title'] for f in get_category_files('Maya_Syllabaries')]
print(f"Found {len(titles_all)} files in category.")

all_urls = {}
for i in range(0, len(titles_all), 50):
    all_urls.update(get_image_urls_batch(titles_all[i:i+50]))
    time.sleep(0.5)
print(f"Resolved {len(all_urls)} image URLs.\n")

# Build plan
plan = []
for title in titles_all:
    url = all_urls.get(title)
    if not url:
        plan.append({'title': title, 'skip': 'no_url'})
        continue
    base_key, variant_key = cv_key_from_title(title)
    if not base_key:
        plan.append({'title': title, 'url': url, 'skip': 'no_key'})
        continue
    path = unquote(urlparse(url).path)
    ext  = os.path.splitext(path)[1].lower() or '.jpg'
    # Strip any query string that crept into ext
    ext  = ext.split('?')[0]
    fname = safe_fname(variant_key, ext)
    plan.append({'title': title, 'url': url, 'base_key': base_key,
                 'variant_key': variant_key, 'fname': fname,
                 'local': os.path.join(GLYPHS, fname), 'skip': None})

# ── Phase 1: requests-based download (subprocess/pipe fails on PRoot/Android) ──
print(f"{'='*60}")
print("PHASE 1 — Downloading via requests (5s between files)")
print(f"{'='*60}")

to_download = [p for p in plan if not p['skip'] and not os.path.exists(p['local'])]
print(f"Need to download: {len(to_download)} files "
      f"(already have {sum(1 for p in plan if not p['skip'] and os.path.exists(p['local']))})")

def dl(url, local):
    for attempt in range(5):
        try:
            r = SESSION.get(url, stream=True, timeout=60)
            if r.status_code == 429:
                wait = int(r.headers.get('Retry-After', 2 ** attempt * 10))
                print(f"  429 on download, waiting {wait}s…")
                time.sleep(wait)
                continue
            if r.status_code == 200:
                with open(local, 'wb') as fh:
                    for chunk in r.iter_content(65536):
                        fh.write(chunk)
                return True
            print(f"  HTTP {r.status_code}")
            return False
        except Exception as e:
            print(f"  Error ({attempt+1}): {e}")
            time.sleep(2 ** attempt * 3)
    return False

if to_download:
    print(f"Downloading {len(to_download)} files (5s between each)…")
    for idx, p in enumerate(to_download, 1):
        local = p['local']
        if os.path.exists(local):
            print(f"[{idx:3}/{len(to_download)}] EXISTS  {p['fname']}")
            continue
        ok = dl(p['url'], local)
        if ok and os.path.exists(local) and os.path.getsize(local) > 0:
            sz = os.path.getsize(local) // 1024
            print(f"[{idx:3}/{len(to_download)}] DL OK   {p['fname']}  ({sz} KB)")
        else:
            if os.path.exists(local):
                os.remove(local)
            print(f"[{idx:3}/{len(to_download)}] DL FAIL {p['fname']}")
        time.sleep(5)

print(f"\nPhase 1 done. Files on disk: {len(list(os.listdir(GLYPHS)))}")

# ── Phase 2: Upload all local files to Drive ───────────────────────────────────
print(f"\n{'='*60}")
print("PHASE 2 — Uploading to Google Drive")
print(f"{'='*60}")

# Fetch existing Drive files in one call
print("Fetching existing Drive files…")
existing_in_drive = set()
page_token = None
while True:
    res = drive.files().list(
        q=f"'{drive_folder_id}' in parents and trashed=false",
        fields='nextPageToken, files(name)', pageSize=1000,
        pageToken=page_token
    ).execute()
    for f in res.get('files', []):
        existing_in_drive.add(f['name'])
    page_token = res.get('nextPageToken')
    if not page_token: break
print(f"Already in Drive: {len(existing_in_drive)} files\n")

mappings   = {}
up_ok = up_skip = up_fail = 0

for item in plan:
    if item['skip'] or not item.get('fname'):
        continue
    local = item['local']
    fname = item['fname']
    if not os.path.exists(local):
        continue
    base_key    = item['base_key']
    variant_key = item['variant_key']
    drive_id    = None

    if fname in existing_in_drive:
        # Get the ID for mappings
        res = drive.files().list(
            q=f"name='{fname}' and '{drive_folder_id}' in parents and trashed=false",
            fields='files(id)'
        ).execute()
        drive_id = res['files'][0]['id'] if res['files'] else None
        print(f"  Drive EXISTS  {fname}")
        up_skip += 1
    else:
        try:
            ext  = os.path.splitext(fname)[1].lower()
            mime = ('image/svg+xml' if ext == '.svg' else
                    'image/png'     if ext == '.png' else 'image/jpeg')
            media    = MediaFileUpload(local, mimetype=mime)
            meta     = {'name': fname, 'parents': [drive_folder_id]}
            drive_id = drive.files().create(body=meta, media_body=media,
                                            fields='id').execute()['id']
            print(f"  Drive UP      {fname}  → {drive_id}")
            up_ok += 1
        except Exception as e:
            print(f"  Drive FAIL    {fname}: {e}")
            up_fail += 1

    entry = {'variant_key': variant_key, 'local_file': fname,
             'drive_id': drive_id, 'wikimedia_title': item['title'], 'url': item['url']}
    mappings.setdefault(base_key, []).append(entry)

# ── Save mappings.json ─────────────────────────────────────────────────────────
out = os.path.join(DATA, 'mappings.json')
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(mappings, fh, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print("ALL DONE")
print(f"  Unique CV keys : {len(mappings)}")
print(f"  Total variants : {sum(len(v) for v in mappings.values())}")
print(f"  Drive up/skip/fail: {up_ok}/{up_skip}/{up_fail}")
print(f"  mappings.json  : {out}")
print(f"  Drive folder   : https://drive.google.com/drive/folders/{drive_folder_id}")
print(f"{'='*60}")
_log.close()
