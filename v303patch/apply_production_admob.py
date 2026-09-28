from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

TEST_APP_ID = 'ca-app-pub-3940256099942544~3347511713'
TEST_BANNER_ID = 'ca-app-pub-3940256099942544/9214589741'
PROD_APP_ID = 'ca-app-pub-9117654406433976~4144682538'
PROD_BANNER_ID = 'ca-app-pub-9117654406433976/8659651777'
FEEDBACK_ENDPOINT = 'https://script.google.com/macros/s/AKfycbyWScf0aMEkfCF5yJQpsEX_mW6t8UXBq3NTLHTK7h-evPGPQAeLBb9qmnwShpXjqOLGFw/exec'

TEXT_EXTS = {'.xml', '.java', '.kt', '.gradle', '.properties', '.txt'}

counts = {TEST_APP_ID: 0, TEST_BANNER_ID: 0}
changed_files = []
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
        continue
    try:
        s = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    original = s
    c1 = s.count(TEST_APP_ID)
    c2 = s.count(TEST_BANNER_ID)
    if c1:
        s = s.replace(TEST_APP_ID, PROD_APP_ID)
        counts[TEST_APP_ID] += c1
    if c2:
        s = s.replace(TEST_BANNER_ID, PROD_BANNER_ID)
        counts[TEST_BANNER_ID] += c2
    if s != original:
        path.write_text(s, encoding='utf-8')
        changed_files.append(str(path.relative_to(ROOT)))

if counts[TEST_APP_ID] < 1:
    raise SystemExit('Google test AdMob App ID not found in reconstructed project')
if counts[TEST_BANNER_ID] < 1:
    raise SystemExit('Google test banner ad unit ID not found in reconstructed project')

# Connect the deployed Apps Script receiver after the in-app feedback form patch has created
# the blank BuildConfig field. This setting is copied into the closed-test variant too.
build = ROOT / 'app/build.gradle'
s = build.read_text(encoding='utf-8')
old = 'buildConfigField "String", "FEEDBACK_ENDPOINT", "\\\"\\\""'
new = 'buildConfigField "String", "FEEDBACK_ENDPOINT", "\\\"' + FEEDBACK_ENDPOINT + '\\\""'
if old not in s:
    raise SystemExit('blank FEEDBACK_ENDPOINT BuildConfig field not found')
s = s.replace(old, new, 1)
build.write_text(s, encoding='utf-8')

print('Production AdMob IDs applied:')
print(f'  App ID replacements: {counts[TEST_APP_ID]}')
print(f'  Banner ID replacements: {counts[TEST_BANNER_ID]}')
print('Feedback endpoint connected')
for f in changed_files:
    print(f'  changed: {f}')
