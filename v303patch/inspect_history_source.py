from pathlib import Path
import re

root=Path('yak_alimi_v21_work')
main=root/'app/src/main/java/com/yakalimi/app/MainActivity.java'
i18n=root/'app/src/main/java/com/yakalimi/app/I18n.java'

s=main.read_text(encoding='utf-8')
print('===== MAIN HISTORY MATCHES =====')
lines=s.splitlines()
for i,line in enumerate(lines,1):
    if re.search(r'history|record|taken|dose', line, re.I):
        lo=max(1,i-8); hi=min(len(lines),i+18)
        print(f'--- lines {lo}-{hi} around {i} ---')
        for j in range(lo,hi+1):
            print(f'{j:04d}: {lines[j-1]}')

print('===== I18N HISTORY MATCHES =====')
for i,line in enumerate(i18n.read_text(encoding='utf-8').splitlines(),1):
    if re.search(r'history|record|taken|dose|기록|복용', line, re.I):
        print(f'{i:04d}: {line}')

print('===== OTHER JAVA STORAGE MATCHES =====')
for p in (root/'app/src/main/java/com/yakalimi/app').glob('*.java'):
    if p.name in {'MainActivity.java','I18n.java'}: continue
    t=p.read_text(encoding='utf-8')
    if re.search(r'history|record|taken|dose|log', t, re.I):
        print('###', p.name)
        for i,line in enumerate(t.splitlines(),1):
            if re.search(r'history|record|taken|dose|log', line, re.I):
                print(f'{i:04d}: {line}')
