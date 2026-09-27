from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

FEEDBACK_EMAIL = 'songseung88@hanmail.net'
PRIVACY_POLICY_URL = 'https://songseung88-sys.github.io/yak-alimi/privacy-policy.html'

# Activate the feedback email while leaving the separate developer-support URL untouched.
build = ROOT / 'app/build.gradle'
s = build.read_text(encoding='utf-8')
lines = s.splitlines()
found = False
for i, line in enumerate(lines):
    if 'buildConfigField' in line and 'FEEDBACK_EMAIL' in line:
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = indent + 'buildConfigField "String", "FEEDBACK_EMAIL", "\\\"' + FEEDBACK_EMAIL + '\\\""'
        found = True
        break
if not found:
    raise SystemExit('FEEDBACK_EMAIL buildConfigField missing')
build.write_text('\n'.join(lines) + '\n', encoding='utf-8')

# Open the public privacy policy in the browser. Keep the in-app policy text as a fallback
# for devices that cannot open an external link.
main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')
anchor = '    private static final int WARNING = Color.rgb(180,75,40);\n'
if anchor not in s:
    raise SystemExit('MainActivity constant anchor missing')
s = s.replace(anchor, anchor + '    private static final String PRIVACY_POLICY_URL = "' + PRIVACY_POLICY_URL + '";\n', 1)

old = '''    private void showPrivacyPolicy(){\n        new AlertDialog.Builder(this).setTitle(I18n.t(this,"privacy_policy"))\n                .setMessage(I18n.t(this,"privacy_policy_text"))\n                .setPositiveButton(android.R.string.ok,null).show();\n    }'''
new = '''    private void showPrivacyPolicy(){\n        try{\n            startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(PRIVACY_POLICY_URL)));\n        }catch(Exception e){\n            new AlertDialog.Builder(this).setTitle(I18n.t(this,"privacy_policy"))\n                    .setMessage(I18n.t(this,"privacy_policy_text"))\n                    .setPositiveButton(android.R.string.ok,null).show();\n        }\n    }'''
if old not in s:
    raise SystemExit('showPrivacyPolicy block missing')
s = s.replace(old, new, 1)
main.write_text(s, encoding='utf-8')

print('V3.0.3 release links patch applied')
