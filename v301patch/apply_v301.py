from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

def replace(path, old, new, count=None):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing expected text in {path}: {old[:80]!r}')
    s2 = s.replace(old, new, count if count is not None else -1)
    p.write_text(s2, encoding='utf-8')

replace('app/build.gradle', 'versionCode 30', 'versionCode 31', 1)
replace('app/build.gradle', "versionName '3.0.0'", "versionName '3.0.1'", 1)

old_priv = 'M.put("privacy_policy_text",new String[]{"약 이름, 복용 시간, 복용 기록과 재고 정보는 기기 안에 저장되며 약 알리미 서버로 전송되지 않습니다. 무료 버전은 광고 표시를 위해 Google Mobile Ads를, 프리미엄 구매 확인을 위해 Google Play Billing을 사용합니다. 복약 데이터는 광고 타겟팅 정보로 전달하지 않습니다.","Medicine names, schedules, dose records, and stock are stored on your device and are not sent to a Yak Alimi server. The free version uses Google Mobile Ads, and Premium purchase status uses Google Play Billing. Medication data is not passed to ads for targeting.","薬名、服用時刻、服用記録、在庫情報は端末内に保存され、薬アラームのサーバーには送信されません。無料版ではGoogle Mobile Ads、プレミアム購入確認ではGoogle Play Billingを使用します。服薬データは広告ターゲティングに渡しません。","药名、服药时间、服药记录和库存信息保存在设备本地，不会发送到本应用服务器。免费版使用 Google Mobile Ads，高级版购买状态使用 Google Play Billing。用药数据不会用于广告定向。","दवा के नाम, समय, रिकॉर्ड और स्टॉक आपके डिवाइस पर रहते हैं और ऐप के सर्वर पर नहीं भेजे जाते। मुफ़्त संस्करण Google Mobile Ads और प्रीमियम खरीद Google Play Billing का उपयोग करते हैं। दवा डेटा विज्ञापन टार्गेटिंग के लिए साझा नहीं किया जाता।","Los nombres, horarios, registros y existencias se guardan en el dispositivo y no se envían a un servidor de Yak Alimi. La versión gratuita usa Google Mobile Ads y Premium usa Google Play Billing. Los datos de medicación no se comparten para segmentar anuncios."});'
new_priv = 'M.put("privacy_policy_text",new String[]{"약 이름, 복용 시간, 복용 기록과 재고 정보는 사용자 기기에만 저장되며 약 알리미 서버로 전송되지 않습니다.","Medicine names, schedules, dose records, and stock are stored only on the user’s device and are not sent to a Yak Alimi server.","薬名、服用時刻、服用記録、在庫情報はユーザーの端末にのみ保存され、薬アラームのサーバーには送信されません。","药名、服药时间、服药记录和库存信息仅保存在用户设备上，不会发送到本应用服务器。","दवा के नाम, समय, रिकॉर्ड और स्टॉक केवल उपयोगकर्ता के डिवाइस पर संग्रहीत होते हैं और ऐप के सर्वर पर नहीं भेजे जाते।","Los nombres, horarios, registros y existencias se guardan únicamente en el dispositivo del usuario y no se envían a un servidor de Yak Alimi."});'
replace('app/src/main/java/com/yakalimi/app/I18n.java', old_priv, new_priv, 1)

appmig = ROOT / 'app/src/main/java/com/yakalimi/app/AppMigration.java'
s = appmig.read_text(encoding='utf-8')
s = s.replace('private static final String KEY_UPDATE_NOTICE = "update_notice_pending";\n    public static final int CURRENT_DATA_VERSION = 4;',
'''private static final String KEY_UPDATE_NOTICE = "update_notice_pending";\n    private static final String PERMISSION_HINT_FILE = "yak_alimi_permission_hints";\n    private static final String KEY_FULLSCREEN_HINT_HANDLED = "fullscreen_hint_handled";\n    public static final int CURRENT_DATA_VERSION = 5;''', 1)
s = s.replace('''        if (updated) e.putBoolean(KEY_UPDATE_NOTICE, true);\n        e.apply();''',
'''        if (updated) {\n            e.putBoolean(KEY_UPDATE_NOTICE, true);\n            if (lastCode > 0) {\n                c.getSharedPreferences(PERMISSION_HINT_FILE, Context.MODE_PRIVATE)\n                        .edit().putBoolean(KEY_FULLSCREEN_HINT_HANDLED, true).apply();\n            }\n        }\n        e.apply();''', 1)
insert_before = '    public static String currentVersionName(Context c) {'
methods = '''    public static boolean shouldShowFullScreenHint(Context c) {\n        return !c.getSharedPreferences(PERMISSION_HINT_FILE, Context.MODE_PRIVATE)\n                .getBoolean(KEY_FULLSCREEN_HINT_HANDLED, false);\n    }\n\n    public static void markFullScreenHintHandled(Context c) {\n        c.getSharedPreferences(PERMISSION_HINT_FILE, Context.MODE_PRIVATE)\n                .edit().putBoolean(KEY_FULLSCREEN_HINT_HANDLED, true).apply();\n    }\n\n'''
if insert_before not in s:
    raise SystemExit('AppMigration insert point missing')
s = s.replace(insert_before, methods + insert_before, 1)
appmig.write_text(s, encoding='utf-8')

main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')
s = s.replace('''        if(!NotificationHelper.canUseFullScreenIntent(this)) addWarning(I18n.t(this,"fullscreen_warning"),I18n.t(this,"allow_fullscreen"),v->requestFullScreenPermission());''',
'''        if(!NotificationHelper.canUseFullScreenIntent(this) && AppMigration.shouldShowFullScreenHint(this))\n            addWarning(I18n.t(this,"fullscreen_warning"),I18n.t(this,"allow_fullscreen"),v->requestFullScreenPermission());''', 1)
s = s.replace('''    private void requestFullScreenPermission(){if(Build.VERSION.SDK_INT>=34){try{startActivity(new Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,Uri.parse("package:"+getPackageName())));}catch(Exception e){startActivity(new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,getPackageName()));}}else Toast.makeText(this,I18n.t(this,"permission_not_needed"),Toast.LENGTH_SHORT).show();}''',
'''    private void requestFullScreenPermission(){AppMigration.markFullScreenHintHandled(this);if(Build.VERSION.SDK_INT>=34){try{startActivity(new Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,Uri.parse("package:"+getPackageName())));}catch(Exception e){startActivity(new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE,getPackageName()));}}else Toast.makeText(this,I18n.t(this,"permission_not_needed"),Toast.LENGTH_SHORT).show();}''', 1)
main.write_text(s, encoding='utf-8')

old_group_fg = '''    <group android:rotation="-45" android:pivotX="74" android:pivotY="74">\n        <path android:fillColor="#FFFFFF"\n            android:pathData="M68,66 L75,66 L75,82 L68,82 C63.6,82 60,78.4 60,74 C60,69.6 63.6,66 68,66 Z"/>\n        <path android:fillColor="#55E6CF"\n            android:pathData="M75,66 L82,66 C86.4,66 90,69.6 90,74 C90,78.4 86.4,82 82,82 L75,82 Z"/>\n        <path android:fillColor="#069EB9" android:pathData="M74.4,66 H75.6 V82 H74.4 Z"/>\n        <path android:fillColor="#FFFFFF" android:pathData="M79.5,68.5 C83,68.5 85.5,70.5 86.5,73" android:strokeColor="#FFFFFF" android:strokeWidth="2.2" android:strokeLineCap="round" android:fillAlpha="0"/>\n    </group>'''
new_group_fg = '''    <group android:rotation="-45" android:pivotX="69" android:pivotY="69">\n        <path android:fillColor="#FFFFFF"\n            android:pathData="M63,61 L70,61 L70,77 L63,77 C58.6,77 55,73.4 55,69 C55,64.6 58.6,61 63,61 Z"/>\n        <path android:fillColor="#55E6CF"\n            android:pathData="M70,61 L77,61 C81.4,61 85,64.6 85,69 C85,73.4 81.4,77 77,77 L70,77 Z"/>\n        <path android:fillColor="#069EB9" android:pathData="M69.4,61 H70.6 V77 H69.4 Z"/>\n        <path android:fillColor="#FFFFFF" android:pathData="M74.5,63.5 C78,63.5 80.5,65.5 81.5,68" android:strokeColor="#FFFFFF" android:strokeWidth="2.2" android:strokeLineCap="round" android:fillAlpha="0"/>\n    </group>'''
replace('app/src/main/res/drawable/ic_launcher_foreground.xml', old_group_fg, new_group_fg, 1)

old_group_legacy = '''    <group android:rotation="-45" android:pivotX="74" android:pivotY="74">\n        <path android:fillColor="#FFFFFF" android:pathData="M68,66 L75,66 L75,82 L68,82 C63.6,82 60,78.4 60,74 C60,69.6 63.6,66 68,66 Z"/>\n        <path android:fillColor="#55E6CF" android:pathData="M75,66 L82,66 C86.4,66 90,69.6 90,74 C90,78.4 86.4,82 82,82 L75,82 Z"/>\n        <path android:fillColor="#069EB9" android:pathData="M74.4,66 H75.6 V82 H74.4 Z"/>\n    </group>'''
new_group_legacy = '''    <group android:rotation="-45" android:pivotX="69" android:pivotY="69">\n        <path android:fillColor="#FFFFFF" android:pathData="M63,61 L70,61 L70,77 L63,77 C58.6,77 55,73.4 55,69 C55,64.6 58.6,61 63,61 Z"/>\n        <path android:fillColor="#55E6CF" android:pathData="M70,61 L77,61 C81.4,61 85,64.6 85,69 C85,73.4 81.4,77 77,77 L70,77 Z"/>\n        <path android:fillColor="#069EB9" android:pathData="M69.4,61 H70.6 V77 H69.4 Z"/>\n    </group>'''
replace('app/src/main/res/drawable/ic_launcher.xml', old_group_legacy, new_group_legacy, 1)

old_group_mono = '''    <group android:rotation="-45" android:pivotX="74" android:pivotY="74">\n        <path android:fillColor="#FFFFFFFF" android:pathData="M68,66 L82,66 C86.4,66 90,69.6 90,74 C90,78.4 86.4,82 82,82 L68,82 C63.6,82 60,78.4 60,74 C60,69.6 63.6,66 68,66 Z"/>\n    </group>'''
new_group_mono = '''    <group android:rotation="-45" android:pivotX="69" android:pivotY="69">\n        <path android:fillColor="#FFFFFFFF" android:pathData="M63,61 L77,61 C81.4,61 85,64.6 85,69 C85,73.4 81.4,77 77,77 L63,77 C58.6,77 55,73.4 55,69 C55,64.6 58.6,61 63,61 Z"/>\n    </group>'''
replace('app/src/main/res/drawable/ic_launcher_monochrome.xml', old_group_mono, new_group_mono, 1)

print('V3.0.1 patch applied')
