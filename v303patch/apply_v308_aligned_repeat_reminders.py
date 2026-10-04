from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_dir = root / "app/src/main/java/com/yakalimi/app"
alarm_scheduler = java_dir / "AlarmScheduler.java"
alarm_receiver = java_dir / "AlarmReceiver.java"
notification_helper = java_dir / "NotificationHelper.java"
main_activity = java_dir / "MainActivity.java"
i18n_file = java_dir / "I18n.java"
build_file = root / "app/build.gradle"

# --- AlarmScheduler: align every repeat to the original dose time and keep scheduling until taken. ---
text = alarm_scheduler.read_text(encoding="utf-8")
if "import java.time.Duration;" not in text:
    text = text.replace("import java.time.LocalDate;\n", "import java.time.Duration;\nimport java.time.LocalDate;\n", 1)

old_recovery = '''    public static void recoverTodaySecondaries(Context c) {
        LocalDateTime now = LocalDateTime.now();
        LocalDate today = now.toLocalDate();
        for (Medicine m : MedicationStore.getMedicines(c)) {
            if (!MedicationStore.isDayEnabled(m, today)) continue;
            for (String slot : m.times) {
                if (MedicationStore.isTaken(c, m.id, today, slot)) continue;
                LocalDateTime primary = today.atTime(LocalTime.parse(slot));
                LocalDateTime secondary = primary.plusMinutes(MedicationStore.snoozeMinutes(c));
                if (now.isAfter(primary) && now.isBefore(secondary)) scheduleSecondaryAt(c, m.id, slot, secondary);
            }
        }
    }
'''
new_recovery = '''    public static void recoverTodaySecondaries(Context c) {
        LocalDateTime now = LocalDateTime.now();
        LocalDate today = now.toLocalDate();
        for (Medicine m : MedicationStore.getMedicines(c)) {
            if (!MedicationStore.isDayEnabled(m, today)) continue;
            for (String slot : m.times) {
                if (MedicationStore.isTaken(c, m.id, today, slot)) continue;
                LocalDateTime primary = today.atTime(LocalTime.parse(slot));
                if (now.isAfter(primary)) scheduleNextSecondaryAligned(c, m.id, slot);
            }
        }
    }
'''
if old_recovery not in text:
    raise SystemExit("recoverTodaySecondaries anchor not found")
text = text.replace(old_recovery, new_recovery, 1)

old_secondary = '''    public static void scheduleSecondaryFromNow(Context c, String medId, String slot) {
        scheduleSecondaryAt(c, medId, slot, LocalDateTime.now().plusMinutes(MedicationStore.snoozeMinutes(c)));
    }

    public static void scheduleSecondaryAt(Context c, String medId, String slot, LocalDateTime when) {
        schedule(c, requestCode(medId, slot, true), when, medId, slot, true);
    }
'''
new_secondary = '''    public static void scheduleSecondaryFromNow(Context c, String medId, String slot) {
        // Kept for compatibility with older call sites. Repeats are now anchored
        // to the original dose time rather than to the moment the previous alert fired.
        scheduleNextSecondaryAligned(c, medId, slot);
    }

    public static void scheduleNextSecondaryAligned(Context c, String medId, String slot) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime primary = now.toLocalDate().atTime(LocalTime.parse(slot));
        int interval = Math.max(5, MedicationStore.snoozeMinutes(c));
        long elapsed = Math.max(0L, Duration.between(primary, now).toMinutes());
        long step = (elapsed / interval) + 1L;
        LocalDateTime next = primary.plusMinutes(step * interval);

        // A dose belongs to its calendar day. Do not let a missed dose create an
        // endless chain into the next day, where the next day's own schedule takes over.
        if (!next.toLocalDate().equals(primary.toLocalDate())) return;

        int repeatIndex = (int)Math.max(1L, step);
        schedule(c, requestCode(medId, slot, true), next, medId, slot, true, repeatIndex);
    }

    public static void scheduleSecondaryAt(Context c, String medId, String slot, LocalDateTime when) {
        LocalDateTime primary = when.toLocalDate().atTime(LocalTime.parse(slot));
        int interval = Math.max(5, MedicationStore.snoozeMinutes(c));
        int repeatIndex = (int)Math.max(1L, Duration.between(primary, when).toMinutes() / interval);
        schedule(c, requestCode(medId, slot, true), when, medId, slot, true, repeatIndex);
    }

    public static void rescheduleSecondaryReminders(Context c) {
        for (Medicine m : MedicationStore.getMedicines(c)) {
            for (String slot : m.times) cancelSecondary(c, m.id, slot);
        }
        recoverTodaySecondaries(c);
    }
'''
if old_secondary not in text:
    raise SystemExit("secondary scheduling anchor not found")
text = text.replace(old_secondary, new_secondary, 1)

old_schedule = '''    private static void schedule(Context c, int req, LocalDateTime time, String medId, String slot, boolean secondary) {
        AlarmManager am = (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);
        long millis = time.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
        PendingIntent pi = pending(c, req, medId, slot, secondary);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && am.canScheduleExactAlarms()) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi);
        } else {
            am.setExact(AlarmManager.RTC_WAKEUP, millis, pi);
        }
    }

    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary) {
        Intent i = new Intent(c, AlarmReceiver.class)
                .putExtra("med_id", medId)
                .putExtra("slot", slot)
                .putExtra("secondary", secondary);
        return PendingIntent.getBroadcast(c, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
'''
new_schedule = '''    private static void schedule(Context c, int req, LocalDateTime time, String medId, String slot, boolean secondary) {
        schedule(c, req, time, medId, slot, secondary, 0);
    }

    private static void schedule(Context c, int req, LocalDateTime time, String medId, String slot, boolean secondary, int repeatIndex) {
        AlarmManager am = (AlarmManager)c.getSystemService(Context.ALARM_SERVICE);
        long millis = time.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
        PendingIntent pi = pending(c, req, medId, slot, secondary, repeatIndex);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && am.canScheduleExactAlarms()) {
            am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, millis, pi);
        } else {
            am.setExact(AlarmManager.RTC_WAKEUP, millis, pi);
        }
    }

    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary) {
        return pending(c, req, medId, slot, secondary, 0);
    }

    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary, int repeatIndex) {
        Intent i = new Intent(c, AlarmReceiver.class)
                .putExtra("med_id", medId)
                .putExtra("slot", slot)
                .putExtra("secondary", secondary)
                .putExtra("repeat_index", repeatIndex);
        return PendingIntent.getBroadcast(c, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
'''
if old_schedule not in text:
    raise SystemExit("schedule/pending anchor not found")
text = text.replace(old_schedule, new_schedule, 1)
alarm_scheduler.write_text(text, encoding="utf-8")

# --- AlarmReceiver: every repeat schedules the next aligned repeat. ---
text = alarm_receiver.read_text(encoding="utf-8")
text = text.replace('        boolean secondary = intent.getBooleanExtra("secondary", false);\n', '        boolean secondary = intent.getBooleanExtra("secondary", false);\n        int repeatIndex = intent.getIntExtra("repeat_index", 0);\n', 1)
old_receiver = '''        NotificationHelper.showDose(context, m, slot, secondary);
        if (!secondary) {
            AlarmScheduler.scheduleSecondaryFromNow(context, medId, slot);
            AlarmScheduler.scheduleNextPrimary(context, m, slot);
        }
'''
new_receiver = '''        NotificationHelper.showDose(context, m, slot, secondary, repeatIndex);
        if (!secondary) {
            AlarmScheduler.scheduleNextSecondaryAligned(context, medId, slot);
            AlarmScheduler.scheduleNextPrimary(context, m, slot);
        } else {
            // Keep repeating at times anchored to the original dose time until
            // the user records the dose.
            AlarmScheduler.scheduleNextSecondaryAligned(context, medId, slot);
        }
'''
if old_receiver not in text:
    raise SystemExit("AlarmReceiver show/schedule anchor not found")
text = text.replace(old_receiver, new_receiver, 1)
alarm_receiver.write_text(text, encoding="utf-8")

# --- NotificationHelper: alternate repeat notification IDs so every repeat is a fresh full-screen alert. ---
text = notification_helper.read_text(encoding="utf-8")
text = text.replace('    public static void showDose(Context c, Medicine m, String slot, boolean second) {\n', '    public static void showDose(Context c, Medicine m, String slot, boolean second, int repeatIndex) {\n', 1)
old_ids = '''        int baseNid = AlarmScheduler.notificationId(m.id, slot);
        // Android may treat a second notify() with the same notification ID as an
        // update and suppress a new full-screen launch. Give repeat reminders a
        // fresh notification identity and dismiss the previous primary alert.
        int nid = second ? secondaryNotificationId(baseNid) : baseNid;
        if (second) c.getSystemService(NotificationManager.class).cancel(baseNid);
'''
new_ids = '''        int baseNid = AlarmScheduler.notificationId(m.id, slot);
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        int nid = baseNid;
        if (second) {
            // Alternate between two repeat IDs. The previous repeat notification is
            // cancelled first, so Android sees each recurrence as a fresh alarm and
            // can launch the full-screen intent again.
            int repeatA = secondaryNotificationId(baseNid, 0);
            int repeatB = secondaryNotificationId(baseNid, 1);
            nm.cancel(baseNid);
            nm.cancel(repeatA);
            nm.cancel(repeatB);
            nid = secondaryNotificationId(baseNid, Math.abs(repeatIndex) % 2);
        }
'''
if old_ids not in text:
    raise SystemExit("Notification ID anchor not found")
text = text.replace(old_ids, new_ids, 1)
old_helper = '''    private static int secondaryNotificationId(int primaryId) {
        // Primary IDs occupy 10000..59999. Keep repeat IDs in a separate range.
        return primaryId + 100000;
    }

    public static void cancelDose(Context c, String medId, String slot) {
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        int primaryId = AlarmScheduler.notificationId(medId, slot);
        nm.cancel(primaryId);
        nm.cancel(secondaryNotificationId(primaryId));
    }
'''
new_helper = '''    private static int secondaryNotificationId(int primaryId, int variant) {
        // Primary IDs occupy 10000..59999. Repeat IDs use two separate ranges so
        // consecutive reminders never update the same currently-posted notification.
        return primaryId + 100000 + (variant == 0 ? 0 : 60000);
    }

    public static void cancelDose(Context c, String medId, String slot) {
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        int primaryId = AlarmScheduler.notificationId(medId, slot);
        nm.cancel(primaryId);
        nm.cancel(secondaryNotificationId(primaryId, 0));
        nm.cancel(secondaryNotificationId(primaryId, 1));
    }
'''
if old_helper not in text:
    raise SystemExit("secondaryNotificationId anchor not found")
text = text.replace(old_helper, new_helper, 1)
notification_helper.write_text(text, encoding="utf-8")

# --- Settings UI: user-selectable interval, default remains 60 min, with custom entry. ---
text = main_activity.read_text(encoding="utf-8")
old_row = '        addSettingRow(group,"♢",I18n.t(this,"snooze"),I18n.t(this,"minutes_later",MedicationStore.snoozeMinutes(this)),v->editSnooze());\n'
new_row = '        addSettingRow(group,"♢",I18n.t(this,"snooze"),formatRepeatInterval(MedicationStore.snoozeMinutes(this)),v->editSnooze());\n'
if old_row not in text:
    raise SystemExit("settings snooze row anchor not found")
text = text.replace(old_row, new_row, 1)
old_edit = '    private void editSnooze(){String[] opts={I18n.t(this,"minutes_later",30),I18n.t(this,"minutes_later",60),I18n.t(this,"minutes_later",120)};int[] vals={30,60,120};new AlertDialog.Builder(this).setTitle(I18n.t(this,"snooze")).setItems(opts,(d,i)->{MedicationStore.setSnoozeMinutes(this,vals[i]);showSettings();}).show();}\n'
new_edit = '''    private String formatRepeatInterval(int minutes){
        if(minutes%60==0) return I18n.t(this,"repeat_every_hours",minutes/60);
        return I18n.t(this,"repeat_every_minutes",minutes);
    }
    private void saveRepeatInterval(int minutes){
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
if old_edit not in text:
    raise SystemExit("editSnooze anchor not found")
text = text.replace(old_edit, new_edit, 1)
main_activity.write_text(text, encoding="utf-8")

# --- I18n labels in all six app languages. ---
i18n = i18n_file.read_text(encoding="utf-8")
old_snooze = '        M.put("snooze",new String[]{"재알림","Repeat reminder","再通知","再次提醒","दोबारा रिमाइंडर","Repetir aviso"});\n'
new_snooze = '        M.put("snooze",new String[]{"재알림 간격","Repeat interval","再通知の間隔","再次提醒间隔","दोबारा रिमाइंडर का अंतराल","Intervalo de repetición"});\n'
if old_snooze not in i18n:
    raise SystemExit("I18n snooze anchor not found")
i18n = i18n.replace(old_snooze, new_snooze, 1)
anchor = '        M.put("minutes_later",new String[]{"%d분 뒤","In %d min","%d分後","%d分钟后","%d मिनट बाद","En %d min"});\n'
if anchor not in i18n:
    raise SystemExit("I18n minutes_later anchor not found")
insert = anchor + '''        M.put("repeat_every_minutes",new String[]{"%d분마다","Every %d min","%d分ごと","每%d分钟","हर %d मिनट","Cada %d min"});
        M.put("repeat_every_hours",new String[]{"%d시간마다","Every %d hr","%d時間ごと","每%d小时","हर %d घंटे","Cada %d h"});
        M.put("custom_interval",new String[]{"직접 입력","Custom interval","自由に設定","自定义间隔","मनचाहा अंतराल","Intervalo personalizado"});
        M.put("custom_interval_title",new String[]{"재알림 간격(분)","Repeat interval (minutes)","再通知の間隔（分）","再次提醒间隔（分钟）","दोबारा रिमाइंडर अंतराल (मिनट)","Intervalo de repetición (minutos)"});
'''
i18n = i18n.replace(anchor, insert, 1)
i18n_file.write_text(i18n, encoding="utf-8")

# --- Version bump. ---
build = build_file.read_text(encoding="utf-8")
if "versionCode 40" not in build or "versionName '3.0.7'" not in build:
    raise SystemExit("Expected v3.0.7 version anchors not found")
build = build.replace("versionCode 40", "versionCode 42", 1)
build = build.replace("versionName '3.0.7'", "versionName '3.0.8'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.8 aligned repeating reminders patch applied")
