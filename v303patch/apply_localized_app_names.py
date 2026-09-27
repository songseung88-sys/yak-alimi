from pathlib import Path
import html
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
RES = ROOT / 'app/src/main/res'
MANIFEST = ROOT / 'app/src/main/AndroidManifest.xml'

NAMES = {
    'values': 'Medication Reminder',          # default / fallback
    'values-ko': '약 알리미',
    'values-en': 'Medication Reminder',
    'values-ja': 'お薬リマインダー',
    'values-zh-rCN': '用药提醒',
    'values-hi': 'दवा रिमाइंडर',
    'values-es': 'Recordatorio de medicación',
}


def set_string(resource_dir: str, name: str, value: str):
    path = RES / resource_dir / 'strings.xml'
    path.parent.mkdir(parents=True, exist_ok=True)
    escaped = html.escape(value, quote=False)
    entry = f'<string name="{name}">{escaped}</string>'

    if not path.exists():
        path.write_text('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    ' + entry + '\n</resources>\n', encoding='utf-8')
        return

    s = path.read_text(encoding='utf-8')
    pattern = re.compile(r'<string\s+name=["\']' + re.escape(name) + r'["\'][^>]*>.*?</string>', re.S)
    if pattern.search(s):
        s = pattern.sub(entry, s, count=1)
    elif '</resources>' in s:
        s = s.replace('</resources>', '    ' + entry + '\n</resources>', 1)
    else:
        raise SystemExit(f'Invalid resources XML: {path}')
    path.write_text(s, encoding='utf-8')


# Ensure the launcher/application label is backed by a translatable string resource.
manifest = MANIFEST.read_text(encoding='utf-8')
match = re.search(r'<application\b[^>]*>', manifest, re.S)
if not match:
    raise SystemExit('No <application> tag found in AndroidManifest.xml')
tag = match.group(0)
if re.search(r'android:label\s*=\s*"[^"]*"', tag):
    new_tag = re.sub(r'android:label\s*=\s*"[^"]*"', 'android:label="@string/app_name"', tag, count=1)
else:
    new_tag = tag[:-1] + '\n        android:label="@string/app_name">'
manifest = manifest[:match.start()] + new_tag + manifest[match.end():]
MANIFEST.write_text(manifest, encoding='utf-8')

for resource_dir, localized_name in NAMES.items():
    set_string(resource_dir, 'app_name', localized_name)

print('Localized launcher app names applied:')
for resource_dir, localized_name in NAMES.items():
    print(f'  {resource_dir}: {localized_name}')
