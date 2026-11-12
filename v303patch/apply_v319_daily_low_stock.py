"""v3.0.19: remind about low stock once a day at a scheduled dose time.

The original threshold-crossing notification is preserved. A per-medicine,
per-local-calendar-day marker prevents a second stock notice on the same day
(and avoids notifying on repeat/snooze alarms).
"""
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "yak_alimi_v21_work")
java = ROOT / "app/src/main/java/com/yakalimi/app"
action_path = java / "ActionReceiver.java"
alarm_path = java / "AlarmReceiver.java"
notification_path = java / "NotificationHelper.java"
build_path = ROOT / "app/build.gradle"

def replace_once(content, old, new, label):
    found = content.count(old)
    if found != 1:
        raise SystemExit(f"{label}: expected one occurrence, found {found}")
    return content.replace(old, new, 1)

action = action_path.read_text(encoding="utf-8")
action = replace_once(
    action,
    "import android.content.Intent;\n",
    "import android.content.Intent;\nimport android.content.SharedPreferences;\n",
    "ActionReceiver SharedPreferences import",
)
old_notice = "            NotificationHelper.showLowStock(context, MedicationStore.getMedicine(context, medId));"
action = replace_once(
    action, old_notice,
    "            maybeWarnLowStockAtDose(context, medId);",
    "Existing threshold-crossing low-stock alert",
)
new_method = """
    // Only one low-stock notification per medication per local calendar day.
    // This also deduplicates the legacy threshold-crossing notice.
    public static void maybeWarnLowStockAtDose(Context context, String medId) {
        Medicine m = MedicationStore.getMedicine(context, medId);
        if (m == null || !m.stockInitialized || m.inventory > m.threshold) return;

        SharedPreferences prefs = context.getSharedPreferences(
                "daily_low_stock_v1", Context.MODE_PRIVATE);
        String key = "med_" + medId;
        String today = LocalDate.now().toString();
        synchronized (ActionReceiver.class) {
            if (today.equals(prefs.getString(key, ""))) return;
            // Synchronous write prevents overlapping broadcasts double-posting.
            if (!prefs.edit().putString(key, today).commit()) return;
        }
        NotificationHelper.showLowStock(context, m);
    }
"""
if "maybeWarnLowStockAtDose" not in action:
    raise SystemExit("Threshold-crossing replacement missing")
if action.count("public static void maybeWarnLowStockAtDose("):
    raise SystemExit("Daily low-stock method already exists")
pos = action.rfind("\n}")
if pos < 0:
    raise SystemExit("ActionReceiver closing brace not found")
action = action[:pos] + "\n" + new_method + action[pos:]
action_path.write_text(action, encoding="utf-8")

alarm = alarm_path.read_text(encoding="utf-8")
alarm = replace_once(
    alarm,
    """        for (AlarmScheduler.DueDose d : due) {
            if (!d.secondary) AlarmScheduler.scheduleNextPrimary(context, d.medicine, d.slot);
            AlarmScheduler.scheduleNextSecondaryAligned(context, d.medicine.id, d.slot);
        }
""",
    """        for (AlarmScheduler.DueDose d : due) {
            if (!d.secondary) {
                // Run only on scheduled primary doses, never a repeat alarm.
                ActionReceiver.maybeWarnLowStockAtDose(context, d.medicine.id);
                AlarmScheduler.scheduleNextPrimary(context, d.medicine, d.slot);
            }
            AlarmScheduler.scheduleNextSecondaryAligned(context, d.medicine.id, d.slot);
        }
""",
    "Grouped alarm receiver primary-only stock reminder",
)
alarm_path.write_text(alarm, encoding="utf-8")

notification = notification_path.read_text(encoding="utf-8")
# Re-posting the same ID is often treated as a quiet update. Cancel the old
# stock notification first, so the next day's alert is a fresh notification.
notification = replace_once(
    notification,
    """        c.getSystemService(NotificationManager.class).notify(62000 + Math.abs(m.id.hashCode() % 1000), b.build());""",
    """        NotificationManager manager = c.getSystemService(NotificationManager.class);
        int notificationId = 62000 + Math.abs(m.id.hashCode() % 1000);
        manager.cancel(notificationId);
        manager.notify(notificationId, b.build());""",
    "Fresh daily stock notification",
)
notification_path.write_text(notification, encoding="utf-8")

build = build_path.read_text(encoding="utf-8")
build = replace_once(build, "versionCode 62", "versionCode 64", "production version code")
build = replace_once(build, "versionName '3.0.18'", "versionName '3.0.19'", "production version name")
build_path.write_text(build, encoding="utf-8")

assert "m.inventory > m.threshold" in action
assert 'LocalDate.now().toString()' in action
assert 'if (!d.secondary)' in alarm
assert 'ActionReceiver.maybeWarnLowStockAtDose(context, d.medicine.id)' in alarm
assert "showDoseGroup(context, due, scheduledAt)" in alarm
print("v3.0.19 daily low-stock patch applied (once/medicine/day, primary reminder only)")
