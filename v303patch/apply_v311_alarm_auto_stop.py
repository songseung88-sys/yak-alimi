from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_file = root / "app/src/main/java/com/yakalimi/app/FullScreenAlarmActivity.java"
build_file = root / "app/build.gradle"

text = java_file.read_text(encoding="utf-8")

# Full-screen alarm sound/vibration is intentionally looping so it is hard to miss,
# but it must not run forever when the user does not interact.
if "import android.os.Handler;" not in text:
    text = text.replace(
        "import android.os.Bundle;\n",
        "import android.os.Bundle;\nimport android.os.Handler;\nimport android.os.Looper;\n",
        1,
    )

old_fields = '''    private Ringtone ringtone;
    private Vibrator vibrator;
    private final List<AlarmScheduler.DueDose> visibleDoses = new ArrayList<>();
    private long groupTime = 0L;
'''
new_fields = '''    private static final long ALERT_AUTO_STOP_MS = 2L * 60L * 1000L;

    private Ringtone ringtone;
    private Vibrator vibrator;
    private final Handler alertHandler = new Handler(Looper.getMainLooper());
    private final Runnable autoStopAlert = this::stopAlert;
    private final List<AlarmScheduler.DueDose> visibleDoses = new ArrayList<>();
    private long groupTime = 0L;
'''
if old_fields not in text:
    raise SystemExit("FullScreenAlarmActivity fields anchor not found")
text = text.replace(old_fields, new_fields, 1)

old_restart = '''    private void restartAlert(){stopAlert();startAlert();}
'''
new_restart = '''    private void restartAlert(){
        stopAlert();
        startAlert();
        alertHandler.postDelayed(autoStopAlert, ALERT_AUTO_STOP_MS);
    }
'''
if old_restart not in text:
    raise SystemExit("restartAlert anchor not found")
text = text.replace(old_restart, new_restart, 1)

old_stop = '''    private void stopAlert(){
        try{if(ringtone!=null&&ringtone.isPlaying())ringtone.stop();}catch(Exception ignored){}
        ringtone=null;
        try{if(vibrator!=null)vibrator.cancel();}catch(Exception ignored){}
        vibrator=null;
    }
'''
new_stop = '''    private void stopAlert(){
        alertHandler.removeCallbacks(autoStopAlert);
        try{if(ringtone!=null&&ringtone.isPlaying())ringtone.stop();}catch(Exception ignored){}
        ringtone=null;
        try{if(vibrator!=null)vibrator.cancel();}catch(Exception ignored){}
        vibrator=null;
    }
'''
if old_stop not in text:
    raise SystemExit("stopAlert anchor not found")
text = text.replace(old_stop, new_stop, 1)

java_file.write_text(text, encoding="utf-8")

build = build_file.read_text(encoding="utf-8")
if "versionCode 46" not in build or "versionName '3.0.10'" not in build:
    raise SystemExit("Expected v3.0.10 version anchors not found")
build = build.replace("versionCode 46", "versionCode 48", 1)
build = build.replace("versionName '3.0.10'", "versionName '3.0.11'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.11 two-minute alarm auto-stop patch applied")
