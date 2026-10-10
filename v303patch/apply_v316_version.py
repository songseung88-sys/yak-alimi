from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 56" not in s or "versionName '3.0.15'" not in s:
    raise SystemExit("v3.0.15 version anchors missing")
s=s.replace("versionCode 56","versionCode 58",1)
s=s.replace("versionName '3.0.15'","versionName '3.0.16'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.16 fresh Play pricing version applied")
