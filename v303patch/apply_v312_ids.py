from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
s=p.read_text(encoding="utf-8")
anchor='        buildConfigField "String", "PREMIUM_PRODUCT_ID", "\\"premium_unlock\\""
'
if anchor not in s: raise SystemExit("anchor missing")
s=s.replace(anchor,anchor+'        buildConfigField "String", "SUPPORT_COFFEE_PRODUCT_ID", "\\"support_coffee_5000\\""
'+'        buildConfigField "String", "SUPPORT_MEAL_PRODUCT_ID", "\\"support_meal_10000\\""
',1)
p.write_text(s,encoding="utf-8")
print("v312 product ids applied")
