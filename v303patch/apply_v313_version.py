from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 50" not in s or "versionName '3.0.12'" not in s:
    raise SystemExit("v3.0.12 version anchors missing")
s=s.replace("versionCode 50","versionCode 52",1)
s=s.replace("versionName '3.0.12'","versionName '3.0.13'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.13 support-card billing version applied")
