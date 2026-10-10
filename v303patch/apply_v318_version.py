from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
if "versionCode 60" not in s or "versionName '3.0.17'" not in s:
    raise SystemExit("v3.0.17 version anchors missing")
s=s.replace("versionCode 60","versionCode 62",1)
s=s.replace("versionName '3.0.17'","versionName '3.0.18'",1)
p.write_text(s,encoding="utf-8")
print("v3.0.18 history action label version applied")
