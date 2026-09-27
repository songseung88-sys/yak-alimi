from pathlib import Path

root = Path('yak_alimi_v21_work')

def replace(path, old, new, count=1):
    p = root / path
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'marker not found in {path}: {old[:80]!r}')
    s = s.replace(old, new, count)
    p.write_text(s)

# App version: intentionally jump versionCode so Android can unmistakably treat this as newer.
replace('app/build.gradle', 'versionCode 3', 'versionCode 22')
replace('app/build.gradle', "versionName '2.1.0'", "versionName '2.2.0'")

# Launcher metadata.
replace('app/src/main/AndroidManifest.xml',
        'android:icon="@drawable/ic_launcher"\n        android:label',
        'android:icon="@drawable/ic_launcher"\n        android:roundIcon="@drawable/ic_launcher"\n        android:label')

# Notification status-bar icon must remain a monochrome notification glyph.
replace('app/src/main/java/com/yakalimi/app/NotificationHelper.java',
        'setSmallIcon(R.drawable.ic_launcher)',
        'setSmallIcon(R.drawable.ic_notification)', count=2)

# Persist normalized medicine fields during schema migration.
replace('app/src/main/java/com/yakalimi/app/MedicationStore.java',
'''    public static synchronized Medicine getMedicine(Context c, String id) {\n''',
'''    public static synchronized void normalizeAll(Context c) {\n        List<Medicine> meds = getMedicines(c);\n        for (Medicine m : meds) sanitize(m);\n        save(c, meds);\n    }\n\n    public static synchronized Medicine getMedicine(Context c, String id) {\n''')

# Add update/migration strings in all six languages.
replace('app/src/main/java/com/yakalimi/app/I18n.java',
'''        M.put("every_day",''',
'''        M.put("updated_title",new String[]{"업데이트 완료","Update complete","アップデート完了","更新完成","अपडेट पूरा","Actualización completada"});\n        M.put("updated_message",new String[]{"약 알리미 %s로 업데이트되었습니다.\\n기존 약과 복용 기록은 그대로 유지됩니다.","Medication Reminder was updated to %s.\\nYour medicines and dose records were kept.","お薬リマインダーを%sに更新しました。\\n登録済みの薬と服用記録はそのまま保持されています。","用药提醒已更新至%s。\\n已保存的药物和服药记录均已保留。","दवा रिमाइंडर %s में अपडेट हो गया है।\\nआपकी दवाएँ और खुराक रिकॉर्ड सुरक्षित हैं।","Recordatorio de medicación se actualizó a %s.\\nTus medicamentos y registros se conservaron."});\n        M.put("app_version",new String[]{"약 알리미 %s","Medication Reminder %s","お薬リマインダー %s","用药提醒 %s","दवा रिमाइंडर %s","Recordatorio de medicación %s"});\n        M.put("every_day",''')

# MainActivity: run migration before UI, show a one-time update notice, and expose app version.
replace('app/src/main/java/com/yakalimi/app/MainActivity.java',
'''    @Override public void onCreate(Bundle state) {\n        super.onCreate(state);\n        getWindow().setStatusBarColor(BG);''',
'''    @Override public void onCreate(Bundle state) {\n        super.onCreate(state);\n        AppMigration.run(this);\n        getWindow().setStatusBarColor(BG);''')
replace('app/src/main/java/com/yakalimi/app/MainActivity.java',
'''        AlarmScheduler.recoverTodaySecondaries(this);\n        showToday();\n    }\n\n    private void showLanguageSelection()''',
'''        AlarmScheduler.recoverTodaySecondaries(this);\n        showToday();\n        maybeShowUpdateNotice();\n    }\n\n    private void showLanguageSelection()''')
replace('app/src/main/java/com/yakalimi/app/MainActivity.java',
'''        Button add=primaryButton("＋  "+I18n.t(this,"add_medicine"));add.setOnClickListener(v->startNewMedicine());content.addView(add,matchWrap(dp(4),0));\n    }\n\n    private void startNewMedicine()''',
'''        Button add=primaryButton("＋  "+I18n.t(this,"add_medicine"));add.setOnClickListener(v->startNewMedicine());content.addView(add,matchWrap(dp(4),0));\n        TextView version=text(I18n.t(this,"app_version",AppMigration.currentVersionName(this)),14,MUTED,false);\n        version.setGravity(Gravity.CENTER);\n        version.setPadding(0,dp(22),0,dp(6));\n        content.addView(version);\n    }\n\n    private void startNewMedicine()''')
replace('app/src/main/java/com/yakalimi/app/MainActivity.java',
'''    private void requestNotificationPermission(){''',
'''    private void maybeShowUpdateNotice(){\n        if(!AppMigration.consumeUpdateNotice(this)) return;\n        new AlertDialog.Builder(this)\n                .setTitle(I18n.t(this,"updated_title"))\n                .setMessage(I18n.t(this,"updated_message",AppMigration.currentVersionName(this)))\n                .setPositiveButton(android.R.string.ok,null)\n                .show();\n    }\n\n    private void requestNotificationPermission(){''')

# New data-schema/version migration helper.
(root/'app/src/main/java/com/yakalimi/app/AppMigration.java').write_text(r'''package com.yakalimi.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;

public final class AppMigration {
    private static final String META_FILE = "yak_alimi_meta";
    private static final String PREF_FILE = "yak_alimi_prefs";
    private static final String UI_FILE = "yak_alimi_ui";
    private static final String KEY_DATA_VERSION = "data_version";
    private static final String KEY_LAST_VERSION_CODE = "last_version_code";
    private static final String KEY_UPDATE_NOTICE = "update_notice_pending";
    public static final int CURRENT_DATA_VERSION = 3;

    private AppMigration() {}

    private static SharedPreferences meta(Context c) {
        return c.getSharedPreferences(META_FILE, Context.MODE_PRIVATE);
    }

    public static void run(Context c) {
        SharedPreferences m = meta(c);
        long currentCode = currentVersionCode(c);
        long lastCode = m.getLong(KEY_LAST_VERSION_CODE, 0L);

        SharedPreferences old = c.getSharedPreferences(PREF_FILE, Context.MODE_PRIVATE);
        SharedPreferences ui = c.getSharedPreferences(UI_FILE, Context.MODE_PRIVATE);
        boolean hadExistingData = old.contains("medicines_json_v2")
                || old.contains("medicine_name")
                || old.contains("alarm_hour")
                || old.contains("stock_initialized")
                || ui.contains("language");

        int dataVersion = m.getInt(KEY_DATA_VERSION, 0);
        if (dataVersion < CURRENT_DATA_VERSION) {
            MedicationStore.normalizeAll(c);
            dataVersion = CURRENT_DATA_VERSION;
        }

        boolean updated = (lastCode > 0 && currentCode > lastCode)
                || (lastCode == 0 && hadExistingData);

        SharedPreferences.Editor e = m.edit()
                .putInt(KEY_DATA_VERSION, dataVersion)
                .putLong(KEY_LAST_VERSION_CODE, currentCode);
        if (updated) e.putBoolean(KEY_UPDATE_NOTICE, true);
        e.apply();
    }

    public static boolean consumeUpdateNotice(Context c) {
        SharedPreferences m = meta(c);
        boolean pending = m.getBoolean(KEY_UPDATE_NOTICE, false);
        if (pending) m.edit().putBoolean(KEY_UPDATE_NOTICE, false).apply();
        return pending;
    }

    public static String currentVersionName(Context c) {
        try {
            PackageInfo info = c.getPackageManager().getPackageInfo(c.getPackageName(), 0);
            return info.versionName == null ? "" : info.versionName;
        } catch (Exception e) {
            return "";
        }
    }

    private static long currentVersionCode(Context c) {
        try {
            PackageInfo info = c.getPackageManager().getPackageInfo(c.getPackageName(), 0);
            if (android.os.Build.VERSION.SDK_INT >= 28) return info.getLongVersionCode();
            return info.versionCode;
        } catch (Exception e) {
            return 0L;
        }
    }
}
''')

# Launcher icon: concept 3 (large white check + small mint capsule), with adaptive and monochrome variants.
drawable = root/'app/src/main/res/drawable'
(drawable/'ic_launcher.xml').write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#08AFC2" android:pathData="M19,5 H89 C98,5 103,10 103,19 V89 C103,98 98,103 89,103 H19 C10,103 5,98 5,89 V19 C5,10 10,5 19,5 Z"/>
    <path android:fillColor="#39DFC0" android:pathData="M5,19 C5,10 10,5 19,5 H75 C56,22 39,33 5,43 Z"/>
    <path android:fillColor="#009AD0" android:pathData="M5,73 C29,77 45,94 69,98 C83,101 95,96 103,88 V89 C103,98 98,103 89,103 H19 C10,103 5,98 5,89 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M24,53 C20.5,49.5 20.5,44 24,40.5 C27.5,37 33,37 36.5,40.5 L49,53 L73,29 C76.5,25.5 82,25.5 85.5,29 C89,32.5 89,38 85.5,41.5 L56,71 C52.5,74.5 47,74.5 43.5,71 Z"/>
    <path android:fillColor="#62E5D0" android:pathData="M64,66 L72,58 C75,55 80,55 83,58 L90,65 C93,68 93,73 90,76 L82,84 C79,87 74,87 71,84 L64,77 C61,74 61,69 64,66 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M64,76 L72,84 C75,87 80,87 83,84 L86,81 L71,66 L64,73 C63,74 63,75 64,76 Z"/>
</vector>
''')
(drawable/'ic_launcher_background.xml').write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#08AFC2" android:pathData="M0,0 H108 V108 H0 Z"/>
    <path android:fillColor="#39DFC0" android:pathData="M0,0 H76 C55,19 37,31 0,40 Z"/>
    <path android:fillColor="#009AD0" android:pathData="M0,72 C26,76 44,94 70,99 C84,102 97,96 108,86 V108 H0 Z"/>
</vector>
''')
(drawable/'ic_launcher_foreground.xml').write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFF" android:pathData="M24,53 C20.5,49.5 20.5,44 24,40.5 C27.5,37 33,37 36.5,40.5 L49,53 L73,29 C76.5,25.5 82,25.5 85.5,29 C89,32.5 89,38 85.5,41.5 L56,71 C52.5,74.5 47,74.5 43.5,71 Z"/>
    <path android:fillColor="#62E5D0" android:pathData="M64,66 L72,58 C75,55 80,55 83,58 L90,65 C93,68 93,73 90,76 L82,84 C79,87 74,87 71,84 L64,77 C61,74 61,69 64,66 Z"/>
    <path android:fillColor="#FFFFFF" android:pathData="M64,76 L72,84 C75,87 80,87 83,84 L86,81 L71,66 L64,73 C63,74 63,75 64,76 Z"/>
</vector>
''')
(drawable/'ic_launcher_monochrome.xml').write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFFFF" android:pathData="M24,53 C20.5,49.5 20.5,44 24,40.5 C27.5,37 33,37 36.5,40.5 L49,53 L73,29 C76.5,25.5 82,25.5 85.5,29 C89,32.5 89,38 85.5,41.5 L56,71 C52.5,74.5 47,74.5 43.5,71 Z"/>
    <path android:fillColor="#FFFFFFFF" android:pathData="M64,66 L72,58 C75,55 80,55 83,58 L90,65 C93,68 93,73 90,76 L82,84 C79,87 74,87 71,84 L64,77 C61,74 61,69 64,66 Z"/>
</vector>
''')
(drawable/'ic_notification.xml').write_text(r'''<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="24dp" android:height="24dp" android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFFFF" android:pathData="M3.4,11.6 C2.8,11 2.8,10 3.4,9.4 C4,8.8 5,8.8 5.6,9.4 L9,12.8 L15.8,6 C16.4,5.4 17.4,5.4 18,6 C18.6,6.6 18.6,7.6 18,8.2 L10.1,16.1 C9.5,16.7 8.5,16.7 7.9,16.1 Z"/>
    <path android:fillColor="#FFFFFFFF" android:pathData="M14.8,14.2 L16.5,12.5 C17.2,11.8 18.3,11.8 19,12.5 L21.5,15 C22.2,15.7 22.2,16.8 21.5,17.5 L19.8,19.2 C19.1,19.9 18,19.9 17.3,19.2 L14.8,16.7 C14.1,16 14.1,14.9 14.8,14.2 Z"/>
</vector>
''')
for qualifier, mono in [('drawable-anydpi-v26', False), ('drawable-anydpi-v33', True)]:
    d = root/'app/src/main/res'/qualifier
    d.mkdir(parents=True, exist_ok=True)
    extra = '\n    <monochrome android:drawable="@drawable/ic_launcher_monochrome" />' if mono else ''
    (d/'ic_launcher.xml').write_text(f'''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@drawable/ic_launcher_background" />\n    <foreground android:drawable="@drawable/ic_launcher_foreground" />{extra}\n</adaptive-icon>\n''')

print('V2.2 patch applied')
