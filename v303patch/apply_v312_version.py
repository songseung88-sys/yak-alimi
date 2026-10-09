from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 48" not in s or "versionName '3.0.11'" not in s:
    raise SystemExit("v3.0.11 version anchors missing")
s=s.replace("versionCode 48","versionCode 50",1)
s=s.replace("versionName '3.0.11'","versionName '3.0.12'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.12 version applied")
