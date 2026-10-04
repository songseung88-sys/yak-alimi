from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_dir = root / "app/src/main/java/com/yakalimi/app"
main_file = java_dir / "MainActivity.java"
store_file = java_dir / "MedicationStore.java"
scheduler_file = java_dir / "AlarmScheduler.java"
build_file = root / "app/build.gradle"

# --- MedicationStore: persist a repeat interval per medicine. ---
store = store_file.read_text(encoding="utf-8")
old_store = '''    public static int snoozeMinutes(Context c) { return p(c).getInt("snooze_minutes_v2", 60); }
    public static void setSnoozeMinutes(Context c, int v) { p(c).edit().putInt("snooze_minutes_v2", Math.max(5, v)).apply(); }
'''
new_store = '''    public static int snoozeMinutes(Context c) { return p(c).getInt("snooze_minutes_v2", 60); }
    public static void setSnoozeMinutes(Context c, int v) { p(c).edit().putInt("snooze_minutes_v2", Math.max(5, v)).apply(); }

    private static String medicineSnoozeKey(String medId) { return "snooze_minutes_med_v3_" + medId; }

    public static int snoozeMinutes(Context c, String medId) {
        if (medId == null || medId.isEmpty()) return 60;
        SharedPreferences sp = p(c);
        String key = medicineSnoozeKey(medId);
        if (sp.contains(key)) return Math.max(5, sp.getInt(key, 60));
        // Existing medicines inherit the previous app-wide interval once, so an
        // upgrade does not unexpectedly change the user's reminder timing.
        return Math.max(5, snoozeMinutes(c));
    }

    public static void setSnoozeMinutes(Context c, String medId, int v) {
        if (medId == null || medId.isEmpty()) return;
        p(c).edit().putInt(medicineSnoozeKey(medId), Math.max(5, v)).apply();
    }

    public static void clearSnoozeMinutes(Context c, String medId) {
        if (medId == null || medId.isEmpty()) return;
        p(c).edit().remove(medicineSnoozeKey(medId)).apply();
    }
'''
if old_store not in store:
    raise SystemExit("MedicationStore snooze anchor not found")
store = store.replace(old_store, new_store, 1)
store_file.write_text(store, encoding="utf-8")

# --- AlarmScheduler: use each medicine's own interval. ---
scheduler = scheduler_file.read_text(encoding="utf-8")
count = scheduler.count('MedicationStore.snoozeMinutes(c)')
if count < 2:
    raise SystemExit(f"Expected at least 2 global snooze calls in AlarmScheduler, found {count}")
scheduler = scheduler.replace('MedicationStore.snoozeMinutes(c)', 'MedicationStore.snoozeMinutes(c, medId)')
scheduler_file.write_text(scheduler, encoding="utf-8")

# --- MainActivity: move interval control from global settings into each medicine editor. ---
main = main_file.read_text(encoding="utf-8")

old_field = '    private boolean draftIconManual = false;\n    private LocalDate draftReceivedDate = LocalDate.now();\n'
new_field = '    private boolean draftIconManual = false;\n    private int draftRepeatMinutes = 60;\n    private LocalDate draftReceivedDate = LocalDate.now();\n'
if old_field not in main:
    raise SystemExit("draft field anchor not found")
main = main.replace(old_field, new_field, 1)

old_global_row = '        addSettingRow(group,"♢",I18n.t(this,"snooze"),formatRepeatInterval(MedicationStore.snoozeMinutes(this)),v->editSnooze());\n'
if old_global_row not in main:
    raise SystemExit("global repeat row anchor not found")
main = main.replace(old_global_row, '', 1)

old_new = '        draft=new Medicine();draft.name=I18n.t(this,"medicine_name_hint");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;draftIconType=MedicationIconStore.CAPSULE;draftIconManual=false;navigateTo("editor");\n'
new_new = '        draft=new Medicine();draft.name=I18n.t(this,"medicine_name_hint");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;draftIconType=MedicationIconStore.CAPSULE;draftIconManual=false;draftRepeatMinutes=60;navigateTo("editor");\n'
if old_new not in main:
    raise SystemExit("startNewMedicine anchor not found")
main = main.replace(old_new, new_new, 1)

old_edit_start = '    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;draftIconType=MedicationIconStore.get(this,id);draftIconManual=true;navigateTo("editor");}\n'
new_edit_start = '    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;draftIconType=MedicationIconStore.get(this,id);draftIconManual=true;draftRepeatMinutes=MedicationStore.snoozeMinutes(this,id);navigateTo("editor");}\n'
if old_edit_start not in main:
    raise SystemExit("startEditMedicine anchor not found")
main = main.replace(old_edit_start, new_edit_start, 1)

old_editor_row = '        addSettingRow(g,"◉",I18n.t(this,"alert_mode"),I18n.modeLabel(this,draft.alertMode),v->editDraftAlertMode());\n        addSettingRow(g,"▦",I18n.t(this,"days"),TimeUtil.daysLabel(this,draft.daysMask),v->editDraftDays());\n'
new_editor_row = '        addSettingRow(g,"◉",I18n.t(this,"alert_mode"),I18n.modeLabel(this,draft.alertMode),v->editDraftAlertMode());\n        addSettingRow(g,"♢",I18n.t(this,"snooze"),formatRepeatInterval(draftRepeatMinutes),v->editDraftRepeatInterval());\n        addSettingRow(g,"▦",I18n.t(this,"days"),TimeUtil.daysLabel(this,draft.daysMask),v->editDraftDays());\n'
if old_editor_row not in main:
    raise SystemExit("medicine editor alert row anchor not found")
main = main.replace(old_editor_row, new_editor_row, 1)

old_commit_new = '        if(draftIsNew){draft.inventory=0;draft.stockInitialized=false;MedicationStore.addMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);if(draftInitialCount>0)MedicationStore.addStock(this,draft.id,draftReceivedDate,draftInitialCount);ActionReceiver.maybeWarnLowStock(this,draft.id);Medicine saved=MedicationStore.getMedicine(this,draft.id);for(String slot:saved.times)AlarmScheduler.scheduleNextPrimary(this,saved,slot);Toast.makeText(this,I18n.t(this,"med_registered"),Toast.LENGTH_SHORT).show();}\n'
new_commit_new = '        if(draftIsNew){draft.inventory=0;draft.stockInitialized=false;MedicationStore.addMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);MedicationStore.setSnoozeMinutes(this,draft.id,draftRepeatMinutes);if(draftInitialCount>0)MedicationStore.addStock(this,draft.id,draftReceivedDate,draftInitialCount);ActionReceiver.maybeWarnLowStock(this,draft.id);Medicine saved=MedicationStore.getMedicine(this,draft.id);for(String slot:saved.times)AlarmScheduler.scheduleNextPrimary(this,saved,slot);Toast.makeText(this,I18n.t(this,"med_registered"),Toast.LENGTH_SHORT).show();}\n'
if old_commit_new not in main:
    raise SystemExit("new medicine commit anchor not found")
main = main.replace(old_commit_new, new_commit_new, 1)

old_commit_edit = '        else {Medicine old=MedicationStore.getMedicine(this,draft.id);if(old!=null)AlarmScheduler.cancelMedicine(this,old);MedicationStore.updateMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);Medicine saved=MedicationStore.getMedicine(this,draft.id);for(String slot:saved.times)AlarmScheduler.scheduleNextPrimary(this,saved,slot);Toast.makeText(this,I18n.t(this,"med_saved"),Toast.LENGTH_SHORT).show();}\n        goHomeAndClearHistory();\n'
new_commit_edit = '        else {Medicine old=MedicationStore.getMedicine(this,draft.id);if(old!=null)AlarmScheduler.cancelMedicine(this,old);MedicationStore.updateMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);MedicationStore.setSnoozeMinutes(this,draft.id,draftRepeatMinutes);Medicine saved=MedicationStore.getMedicine(this,draft.id);for(String slot:saved.times)AlarmScheduler.scheduleNextPrimary(this,saved,slot);Toast.makeText(this,I18n.t(this,"med_saved"),Toast.LENGTH_SHORT).show();}\n        AlarmScheduler.rescheduleSecondaryReminders(this);\n        goHomeAndClearHistory();\n'
if old_commit_edit not in main:
    raise SystemExit("edit medicine commit anchor not found")
main = main.replace(old_commit_edit, new_commit_edit, 1)

old_delete = 'MedicationStore.deleteMedicine(this,draft.id);MedicationIconStore.delete(this,draft.id);goHomeAndClearHistory();'
new_delete = 'MedicationStore.deleteMedicine(this,draft.id);MedicationStore.clearSnoozeMinutes(this,draft.id);MedicationIconStore.delete(this,draft.id);goHomeAndClearHistory();'
if old_delete not in main:
    raise SystemExit("delete medicine anchor not found")
main = main.replace(old_delete, new_delete, 1)

old_methods = '''    private void saveRepeatInterval(int minutes){
        MedicationStore.setSnoozeMinutes(this,minutes);
        AlarmScheduler.rescheduleSecondaryReminders(this);
        showSettings();
    }
    private void editSnooze(){
        String[] opts={
                I18n.t(this,"repeat_every_minutes",30),
                I18n.t(this,"repeat_every_hours",1),
                I18n.t(this,"repeat_every_hours",2),
                I18n.t(this,"custom_interval")
        };
        int[] vals={30,60,120};
        new AlertDialog.Builder(this).setTitle(I18n.t(this,"snooze")).setItems(opts,(d,i)->{
            if(i<vals.length){saveRepeatInterval(vals[i]);return;}
            numberDialog(I18n.t(this,"custom_interval_title"),MedicationStore.snoozeMinutes(this),5,720,this::saveRepeatInterval);
        }).show();
    }
'''
new_methods = '''    private void editDraftRepeatInterval(){
        String[] opts={
                I18n.t(this,"repeat_every_minutes",30),
                I18n.t(this,"repeat_every_hours",1),
                I18n.t(this,"repeat_every_hours",2),
                I18n.t(this,"custom_interval")
        };
        int[] vals={30,60,120};
        new AlertDialog.Builder(this).setTitle(I18n.t(this,"snooze")).setItems(opts,(d,i)->{
            if(i<vals.length){draftRepeatMinutes=vals[i];showMedicineEditor();return;}
            numberDialog(I18n.t(this,"custom_interval_title"),draftRepeatMinutes,5,720,v->{draftRepeatMinutes=v;showMedicineEditor();});
        }).show();
    }
'''
if old_methods not in main:
    raise SystemExit("global repeat editor methods anchor not found")
main = main.replace(old_methods, new_methods, 1)
main_file.write_text(main, encoding="utf-8")

# --- Version bump. ---
build = build_file.read_text(encoding="utf-8")
if "versionCode 42" not in build or "versionName '3.0.8'" not in build:
    raise SystemExit("Expected v3.0.8 version anchors not found")
build = build.replace("versionCode 42", "versionCode 44", 1)
build = build.replace("versionName '3.0.8'", "versionName '3.0.9'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.9 per-medicine repeat interval patch applied")
