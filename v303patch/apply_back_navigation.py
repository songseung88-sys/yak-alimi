from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')

# Keep an in-app navigation history so Android's Back button behaves like the visible X/close flow.
old = '''    private String screen = "today";\n    private Medicine draft;'''
new = '''    private String screen = "today";\n    private final java.util.ArrayDeque<String> screenBackStack = new java.util.ArrayDeque<>();\n    private long lastBackPressedAt = 0L;\n    private static final long BACK_EXIT_WINDOW_MS = 2000L;\n    private Medicine draft;'''
if old not in s:
    raise SystemExit('MainActivity screen field anchor missing')
s = s.replace(old, new, 1)

# Register the modern Android back callback on Android 13+, while retaining onBackPressed
# as a fallback on older devices and OEM implementations.
old = '''        super.onCreate(state);\n        AppMigration.run(this);'''
new = '''        super.onCreate(state);\n        if (Build.VERSION.SDK_INT >= 33) BackApi33.register(this, this::handleAppBackPressed);\n        AppMigration.run(this);'''
if old not in s:
    raise SystemExit('MainActivity onCreate anchor missing')
s = s.replace(old, new, 1)

# Once language selection is completed, Today becomes the navigation root.
old = '''    private void initializeAfterLanguage() {\n        nav.setVisibility(View.VISIBLE);'''
new = '''    private void initializeAfterLanguage() {\n        screenBackStack.clear();\n        nav.setVisibility(View.VISIBLE);'''
if old not in s:
    raise SystemExit('initializeAfterLanguage anchor missing')
s = s.replace(old, new, 1)

# Bottom navigation now records actual screen history. Explicitly tapping Today resets the stack.
old = '''        t.setOnClickListener(v->{screen=id;renderCurrent();});'''
new = '''        t.setOnClickListener(v->navigateTo(id));'''
if old not in s:
    raise SystemExit('bottom nav click anchor missing')
s = s.replace(old, new, 1)

# Enter editor/refill through the same navigation helper so Back returns to the true prior screen.
old = '''        draft=new Medicine();draft.name=I18n.t(this,"medicine_name");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;screen="editor";showMedicineEditor();'''
new = '''        draft=new Medicine();draft.name=I18n.t(this,"medicine_name");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;navigateTo("editor");'''
if old not in s:
    raise SystemExit('startNewMedicine navigation anchor missing')
s = s.replace(old, new, 1)

old = '''    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;screen="editor";showMedicineEditor();}'''
new = '''    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;navigateTo("editor");}'''
if old not in s:
    raise SystemExit('startEditMedicine navigation anchor missing')
s = s.replace(old, new, 1)

old = '''        TextView close=text(I18n.t(this,"close"),17,MUTED,false);close.setGravity(Gravity.RIGHT);close.setPadding(0,0,dp(4),dp(10));close.setOnClickListener(v->{screen="settings";showSettings();});content.addView(close);'''
new = '''        TextView close=text(I18n.t(this,"close"),17,MUTED,false);close.setGravity(Gravity.RIGHT);close.setPadding(0,0,dp(4),dp(10));close.setOnClickListener(v->handleAppBackPressed());content.addView(close);'''
if old not in s:
    raise SystemExit('medicine editor close anchor missing')
s = s.replace(old, new, 1)

old = '''    private void startRefill(String medId){refillMedId=medId;refillDate=LocalDate.now();refillCount=28;screen="refill";showRefill();}'''
new = '''    private void startRefill(String medId){refillMedId=medId;refillDate=LocalDate.now();refillCount=28;navigateTo("refill");}'''
if old not in s:
    raise SystemExit('startRefill navigation anchor missing')
s = s.replace(old, new, 1)

old = '''TextView close=text(I18n.t(this,"close"),17,MUTED,false);close.setGravity(Gravity.RIGHT);close.setOnClickListener(v->{screen="today";showToday();});content.addView(close,matchWrap(0,dp(8)));'''
new = '''TextView close=text(I18n.t(this,"close"),17,MUTED,false);close.setGravity(Gravity.RIGHT);close.setOnClickListener(v->handleAppBackPressed());content.addView(close,matchWrap(0,dp(8)));'''
if old not in s:
    raise SystemExit('refill close anchor missing')
s = s.replace(old, new, 1)

# Successful actions that deliberately return to Today should not leave stale detail pages in history.
s = s.replace('''        screen="today";showToday();\n    }\n\n    private void confirmDeleteMedicine()''', '''        goHomeAndClearHistory();\n    }\n\n    private void confirmDeleteMedicine()''', 1)
s = s.replace('''MedicationStore.deleteMedicine(this,draft.id);screen="today";showToday();}).show();''', '''MedicationStore.deleteMedicine(this,draft.id);goHomeAndClearHistory();}).show();''', 1)
s = s.replace('''if(m==null){screen="today";showToday();return;}''', '''if(m==null){goHomeAndClearHistory();return;}''', 1)
s = s.replace('''Toast.makeText(this,I18n.t(this,"added_units",I18n.qty(this,refillCount)),Toast.LENGTH_SHORT).show();screen="today";showToday();});''', '''Toast.makeText(this,I18n.t(this,"added_units",I18n.qty(this,refillCount)),Toast.LENGTH_SHORT).show();goHomeAndClearHistory();});''', 1)

# Insert navigation/back helpers before the Premium dialog section.
marker = '    private void showPremiumDialog(){\n'
if marker not in s:
    raise SystemExit('showPremiumDialog marker missing')
helpers = '''    private void navigateTo(String target){\n        if(target==null || target.equals(screen)) return;\n        if("today".equals(target)){\n            screenBackStack.clear();\n        }else if(!"language".equals(screen) || I18n.hasLanguage(this)){\n            if(screenBackStack.isEmpty() || !screen.equals(screenBackStack.peek())) screenBackStack.push(screen);\n        }\n        screen=target;\n        renderCurrent();\n    }\n\n    private void goHomeAndClearHistory(){\n        screenBackStack.clear();\n        screen="today";\n        showToday();\n    }\n\n    private void handleAppBackPressed(){\n        // Initial language selection has no in-app parent, so treat it like the app root.\n        if("language".equals(screen) && !I18n.hasLanguage(this)){\n            handleRootBackPress();\n            return;\n        }\n        while(!screenBackStack.isEmpty()){\n            String previous=screenBackStack.pop();\n            if(previous!=null && !previous.equals(screen)){\n                screen=previous;\n                renderCurrent();\n                return;\n            }\n        }\n        if(!"today".equals(screen)){\n            screen="today";\n            showToday();\n            return;\n        }\n        handleRootBackPress();\n    }\n\n    private void handleRootBackPress(){\n        long now=System.currentTimeMillis();\n        if(now-lastBackPressedAt<=BACK_EXIT_WINDOW_MS){\n            finish();\n            return;\n        }\n        lastBackPressedAt=now;\n        Toast.makeText(this,I18n.t(this,"press_back_again_exit"),Toast.LENGTH_SHORT).show();\n    }\n\n    @Override public void onBackPressed(){\n        handleAppBackPressed();\n    }\n\n    private static final class BackApi33 {\n        static void register(Activity activity, Runnable action){\n            activity.getOnBackInvokedDispatcher().registerOnBackInvokedCallback(\n                    android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, action::run);\n        }\n    }\n\n'''
s = s.replace(marker, helpers + marker, 1)
main.write_text(s, encoding='utf-8')

# Add the localized root-back hint to all six languages.
i18n = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
s = i18n.read_text(encoding='utf-8')
if 'M.put("press_back_again_exit"' not in s:
    prefix = '        M.put("restore_purchase_desc",'
    pos = s.find(prefix)
    if pos < 0:
        raise SystemExit('I18n insertion anchor missing')
    line_end = s.find('\n', pos)
    if line_end < 0:
        raise SystemExit('I18n insertion line end missing')
    addition = '''        M.put("press_back_again_exit",new String[]{"한 번 더 누르면 앱이 종료됩니다.","Press back again to exit.","もう一度戻るボタンを押すと終了します。","再按一次返回键退出应用。","ऐप से बाहर निकलने के लिए फिर से वापस दबाएँ।","Pulsa atrás de nuevo para salir."});\n'''
    s = s[:line_end+1] + addition + s[line_end+1:]
i18n.write_text(s, encoding='utf-8')

# Explicitly enable the modern system back callback for MainActivity/app navigation.
manifest = ROOT / 'app/src/main/AndroidManifest.xml'
s = manifest.read_text(encoding='utf-8')
if 'android:enableOnBackInvokedCallback=' not in s:
    if '<application' not in s:
        raise SystemExit('AndroidManifest application tag missing')
    s = s.replace('<application', '<application\n        android:enableOnBackInvokedCallback="true"', 1)
manifest.write_text(s, encoding='utf-8')

print('V3.0.3 Android back navigation patch applied')
