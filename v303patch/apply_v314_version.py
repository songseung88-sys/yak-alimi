from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 52" not in s or "versionName '3.0.13'" not in s:
    raise SystemExit("v3.0.13 version anchors missing")
s=s.replace("versionCode 52","versionCode 54",1)
s=s.replace("versionName '3.0.13'","versionName '3.0.14'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.14 Play product ID alignment version applied")
