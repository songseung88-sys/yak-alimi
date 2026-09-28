from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_closedtest_work')

PROD_APP_ID = 'ca-app-pub-9117654406433976~4144682538'
PROD_BANNER_ID = 'ca-app-pub-9117654406433976/8659651777'
TEST_APP_ID = 'ca-app-pub-3940256099942544~3347511713'
TEST_BANNER_ID = 'ca-app-pub-3940256099942544/9214589741'

TEXT_EXTS = {'.xml', '.java', '.kt', '.gradle', '.properties', '.txt'}
counts = {PROD_APP_ID: 0, PROD_BANNER_ID: 0}

for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
        continue
    try:
        s = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    original = s
    c1 = s.count(PROD_APP_ID)
    c2 = s.count(PROD_BANNER_ID)
    if c1:
        s = s.replace(PROD_APP_ID, TEST_APP_ID)
        counts[PROD_APP_ID] += c1
    if c2:
        s = s.replace(PROD_BANNER_ID, TEST_BANNER_ID)
        counts[PROD_BANNER_ID] += c2
    if s != original:
        path.write_text(s, encoding='utf-8')

if counts[PROD_APP_ID] < 1 or counts[PROD_BANNER_ID] < 1:
    raise SystemExit('Production AdMob IDs were not found in closed-test working copy')

print('Closed-test AdMob IDs restored to Google test IDs')
