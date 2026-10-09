from pathlib import Path
p=Path("yak_alimi_v21_work/app/build.gradle")
lines=p.read_text(encoding="utf-8").splitlines()
out=[]
done=False
for line in lines:
    out.append(line)
    if "PREMIUM_PRODUCT_ID" in line and not done:
        out.append('        buildConfigField "String", "SUPPORT_COFFEE_PRODUCT_ID", "\\"support_coffee_5000\\""')
        out.append('        buildConfigField "String", "SUPPORT_MEAL_PRODUCT_ID", "\\"support_meal_10000\\""')
        done=True
if not done:
    raise SystemExit("premium product id missing")
p.write_text("\n".join(out)+"\n",encoding="utf-8")
print("v312 product ids applied")
