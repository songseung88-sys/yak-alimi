from pathlib import Path
p=Path("yak_alimi_v21_work/app/src/main/java/com/yakalimi/app/I18n.java")
s=p.read_text(encoding="utf-8")
old='''        M.put("history_mark_taken",new String[]{"먹었어요로 기록","Mark as taken","服用済みにする","标记为已服用","लिया हुआ दर्ज करें","Marcar como tomado"});'''
new='''        M.put("history_mark_taken",new String[]{"먹었어요","Taken","服用しました","已服用","ले लिया","Tomado"});'''
if old not in s:
    raise SystemExit("history_mark_taken anchor missing")
s=s.replace(old,new,1)
p.write_text(s,encoding="utf-8")
print("Simplified missed-dose action label to Taken")
