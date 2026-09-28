"""Show each registered medication or supplement in the home summary."""

from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
main = root / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
source = main.read_text(encoding='utf-8')

old_call = '            addNextDoseCard();\n            TextView mine=text(I18n.t(this,"my_medicines"),23,TEXT,true);'
new_call = '            if(meds.size()==1) addNextDoseCard();\n            else addMultiMedicineDoseCard(meds,today);\n            TextView mine=text(I18n.t(this,"my_medicines"),23,TEXT,true);'
if source.count(old_call) != 1:
    raise SystemExit('Home dose summary call not found exactly once')
source = source.replace(old_call, new_call, 1)

anchor = '    private void addNextDoseCard() {\n'
if source.count(anchor) != 1:
    raise SystemExit('Home dose summary method not found exactly once')
new_method = '''    private void addMultiMedicineDoseCard(List<Medicine> meds, LocalDate today) {
        LinearLayout summary=card();
        TextView title=text(I18n.t(this,"today_med_supplement"),23,TEXT,true);
        title.setPadding(0,0,0,dp(4));summary.addView(title);
        LocalTime now=LocalTime.now();
        for(int i=0;i<meds.size();i++) {
            Medicine medicine=meds.get(i);
            if(i>0) {
                View separator=new View(this);
                separator.setBackgroundColor(CARD_BORDER);
                summary.addView(separator,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(1)));
            }
            LinearLayout item=new LinearLayout(this);
            item.setOrientation(LinearLayout.VERTICAL);
            item.setPadding(0,dp(12),0,dp(12));
            TextView name=text("💊  "+medicine.name,21,TEXT,true);
            item.addView(name);
            String nextSlot=null;
            LocalTime nextTime=null;
            boolean scheduledToday=MedicationStore.isDayEnabled(medicine,today);
            if(scheduledToday) {
                for(String slot:medicine.times) {
                    if(MedicationStore.isTaken(this,medicine.id,today,slot)) continue;
                    LocalTime time=LocalTime.parse(slot);
                    if(nextTime==null || time.isBefore(nextTime)) {
                        nextSlot=slot;
                        nextTime=time;
                    }
                }
            }
            String state=!scheduledToday?I18n.t(this,"today_none"):
                    nextSlot==null?I18n.t(this,"calendar_all_done"):
                    I18n.t(this,nextTime.isBefore(now)?"dose_overdue":"next_dose");
            String description=nextSlot==null?state:TimeUtil.time(this,nextSlot)+" · "+state;
            TextView detail=text(description,17,nextSlot!=null && nextTime.isBefore(now)?WARNING:MUTED,false);
            detail.setPadding(0,dp(6),0,0);item.addView(detail);
            if(nextSlot!=null) {
                final String slotToRecord=nextSlot;
                Button done=primaryButton(I18n.t(this,"taken_button"));
                done.setTextSize(16);
                done.setMinHeight(dp(46));
                done.setOnClickListener(v->markTakenNow(medicine.id,slotToRecord));
                item.addView(done,matchWrap(dp(9),0));
            }
            summary.addView(item);
        }
        content.addView(summary,matchWrap(0,dp(12)));
    }

'''
source = source.replace(anchor, new_method + anchor, 1)
main.write_text(source, encoding='utf-8')

i18n = root / 'app/src/main/java/com/yakalimi/app/I18n.java'
translations = i18n.read_text(encoding='utf-8')
anchor = '        M.put("my_medicines",'
line = '        M.put("today_med_supplement",new String[]{"오늘의 약·영양제","Today’s medications & supplements","今日の薬・サプリメント","今天的药物与保健品","आज की दवाएँ और सप्लीमेंट","Medicamentos y suplementos de hoy"});\n'
if translations.count(anchor) != 1:
    raise SystemExit('Translation insertion point not found exactly once')
translations = translations.replace(anchor, line + anchor, 1)
i18n.write_text(translations, encoding='utf-8')

print('Multi-medication home summary applied')
