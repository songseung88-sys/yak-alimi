from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
view = root / "app/src/main/java/com/yakalimi/app/MedicationIconView.java"
text = view.read_text(encoding="utf-8")
text = text.replace("setMinimumWidth(dp(36));", "setMinimumWidth((int)dp(36));")
text = text.replace("setMinimumHeight(dp(36));", "setMinimumHeight((int)dp(36));")
view.write_text(text, encoding="utf-8")
print("V3.0.6 medication icon compile fix applied")
