from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 54" not in s or "versionName '3.0.14'" not in s:
    raise SystemExit("v3.0.14 version anchors missing")
s=s.replace("versionCode 54","versionCode 56",1)
s=s.replace("versionName '3.0.14'","versionName '3.0.15'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.15 product-id correction version applied")
