from pathlib import Path

root=Path('yak_alimi_v21_work')
main=root/'app/src/main/java/com/yakalimi/app/MainActivity.java'
i18n=root/'app/src/main/java/com/yakalimi/app/I18n.java'
for p in [main,i18n]:
    print('===== '+p.name+' =====')
    lines=p.read_text(encoding='utf-8').splitlines()
    for i,line in enumerate(lines,1):
        if any(k.lower() in line.lower() for k in ['feedback','email','mailto','opinion','의견','sendto']):
            lo=max(1,i-8); hi=min(len(lines),i+18)
            print(f'--- {lo}-{hi} around {i} ---')
            for j in range(lo,hi+1): print(f'{j:04d}: {lines[j-1]}')
