from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
notification = root / "app/src/main/java/com/yakalimi/app/NotificationHelper.java"
build_gradle = root / "app/build.gradle"

text = notification.read_text(encoding="utf-8")

old_nid = '        int nid = AlarmScheduler.notificationId(m.id, slot);\n'
new_nid = '''        int baseNid = AlarmScheduler.notificationId(m.id, slot);\n        // Android may treat a second notify() with the same notification ID as an\n        // update and suppress a new full-screen launch. Give repeat reminders a\n        // fresh notification identity and dismiss the previous primary alert.\n        int nid = second ? secondaryNotificationId(baseNid) : baseNid;\n        if (second) c.getSystemService(NotificationManager.class).cancel(baseNid);\n'''
if old_nid not in text:
    raise SystemExit("Notification ID anchor not found")
text = text.replace(old_nid, new_nid, 1)

old_cancel = '''    public static void cancelDose(Context c, String medId, String slot) {\n        c.getSystemService(NotificationManager.class).cancel(AlarmScheduler.notificationId(medId, slot));\n    }\n'''
new_cancel = '''    private static int secondaryNotificationId(int primaryId) {\n        // Primary IDs occupy 10000..59999. Keep repeat IDs in a separate range.\n        return primaryId + 100000;\n    }\n\n    public static void cancelDose(Context c, String medId, String slot) {\n        NotificationManager nm = c.getSystemService(NotificationManager.class);\n        int primaryId = AlarmScheduler.notificationId(medId, slot);\n        nm.cancel(primaryId);\n        nm.cancel(secondaryNotificationId(primaryId));\n    }\n'''
if old_cancel not in text:
    raise SystemExit("cancelDose anchor not found")
text = text.replace(old_cancel, new_cancel, 1)

notification.write_text(text, encoding="utf-8")

build = build_gradle.read_text(encoding="utf-8")
if "versionCode 34" not in build or "versionName '3.0.4'" not in build:
    raise SystemExit("Expected v3.0.4 version anchors not found")
build = build.replace("versionCode 34", "versionCode 36", 1)
build = build.replace("versionName '3.0.4'", "versionName '3.0.5'", 1)
build_gradle.write_text(build, encoding="utf-8")

print("V3.0.5 repeat full-screen reminder patch applied")
