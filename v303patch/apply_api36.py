"""Update the restored production project for Android 16 (API 36)."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

def replace_once(path, old, new):
    source = path.read_text(encoding='utf-8')
    if source.count(old) != 1:
        raise SystemExit(f'Expected one API 36 anchor in {path}: {old!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')

replace_once(root / 'build.gradle', "version '8.7.3'", "version '8.10.1'")
app = root / 'app/build.gradle'
replace_once(app, 'compileSdk 35', 'compileSdk 36')
replace_once(app, 'targetSdk 35', 'targetSdk 36')
replace_once(app, 'versionCode 33', 'versionCode 34')
replace_once(app, "versionName '3.0.3'", "versionName '3.0.4'")

# MainActivity and the fullscreen reminder already apply system-bar insets and
# register a platform back callback, so no opt-out or UI copy changes are needed.
print('Android API 36, AGP 8.10.1, app version 3.0.4 (34) applied')
