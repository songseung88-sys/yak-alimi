from pathlib import Path

root=Path('yak_alimi_v21_work')/'app/src/main/java/com/yakalimi/app'
for name in ['Medicine.java','MedicationStore.java']:
    p=root/name
    print('===== '+name+' =====')
    print(p.read_text(encoding='utf-8'))
