from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

# Clarify purchase restoration without changing the V3.0.3 version.
i18n = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
s = i18n.read_text(encoding='utf-8')
old = '        M.put("restore_purchase",new String[]{"구매 복원","Restore Purchase","購入を復元","恢复购买","खरीदारी पुनर्स्थापित करें","Restaurar compra"});\n'
new = old.replace('"구매 복원"', '"이전 구매 복구"')
if old not in s:
    raise SystemExit('restore_purchase line missing')
s = s.replace(old, new, 1)
anchor = new
extra = anchor + '''        M.put("restore_purchase_question",new String[]{"이전에 구매했나요?","Purchased before?","以前に購入しましたか？","以前购买过吗？","क्या आपने पहले खरीदा था?","¿Ya lo compraste antes?"});\n        M.put("restore_purchase_desc",new String[]{"이전에 구매한 프리미엄을 다시 활성화합니다.","Reactivates Premium that you purchased previously.","以前購入したプレミアムを再び有効にします。","重新启用您之前购买的高级版。","पहले खरीदे गए प्रीमियम को फिर से सक्रिय करें।","Vuelve a activar Premium si ya lo compraste antes."});\n'''
s = s.replace(anchor, extra, 1)
i18n.write_text(s, encoding='utf-8')

main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')
old_settings = '''            Button restore=secondaryButton(I18n.t(this,"restore_purchase"));restore.setOnClickListener(v->billingManager.refreshPurchases());premium.addView(restore,matchWrap(dp(8),0));'''
new_settings = '''            Button restore=secondaryButton(I18n.t(this,"restore_purchase"));restore.setOnClickListener(v->billingManager.refreshPurchases());premium.addView(restore,matchWrap(dp(8),0));\n            TextView restoreDesc=text(I18n.t(this,"restore_purchase_desc"),13,MUTED,false);restoreDesc.setPadding(dp(4),dp(6),dp(4),0);premium.addView(restoreDesc);'''
if old_settings not in s:
    raise SystemExit('settings restore button line missing')
s = s.replace(old_settings, new_settings, 1)

old_dialog = '''        message += "\\n"+I18n.t(this,"premium_helper");\n        new AlertDialog.Builder(this)\n                .setTitle(I18n.t(this,"premium_title"))\n                .setMessage(message)\n                .setNegativeButton(I18n.t(this,"cancel"),null)\n                .setPositiveButton(I18n.t(this,"unlock_premium"),(d,w)->billingManager.purchasePremium())\n                .show();'''
new_dialog = '''        message += "\\n"+I18n.t(this,"premium_helper");\n        message += "\\n\\n"+I18n.t(this,"restore_purchase_question");\n        new AlertDialog.Builder(this)\n                .setTitle(I18n.t(this,"premium_title"))\n                .setMessage(message)\n                .setNeutralButton(I18n.t(this,"restore_purchase"),(d,w)->billingManager.refreshPurchases())\n                .setNegativeButton(I18n.t(this,"cancel"),null)\n                .setPositiveButton(I18n.t(this,"unlock_premium"),(d,w)->billingManager.purchasePremium())\n                .show();'''
if old_dialog not in s:
    raise SystemExit('V3.0.3 premium dialog block missing')
s = s.replace(old_dialog, new_dialog, 1)
main.write_text(s, encoding='utf-8')

# Apply release contact/link configuration in the same V3.0.3 build.
release_patch = Path(__file__).with_name('apply_release_links.py')
exec(compile(release_patch.read_text(encoding='utf-8'), str(release_patch), 'exec'), {'__name__':'__main__'})

# Match the launcher name to the user's device language.
name_patch = Path(__file__).with_name('apply_localized_app_names.py')
exec(compile(name_patch.read_text(encoding='utf-8'), str(name_patch), 'exec'), {'__name__':'__main__'})

# Make the Android system Back button follow the app's internal navigation.
back_patch = Path(__file__).with_name('apply_back_navigation.py')
exec(compile(back_patch.read_text(encoding='utf-8'), str(back_patch), 'exec'), {'__name__':'__main__'})

# Broaden user-facing copy so the same workflows naturally cover supplements too.
supplement_patch = Path(__file__).with_name('apply_med_supplement_copy.py')
exec(compile(supplement_patch.read_text(encoding='utf-8'), str(supplement_patch), 'exec'), {'__name__':'__main__'})

# Persist per-medication registration dates so history never extends before a medication existed.
registration_patch = Path(__file__).with_name('apply_med_registration_date.py')
exec(compile(registration_patch.read_text(encoding='utf-8'), str(registration_patch), 'exec'), {'__name__':'__main__'})

# Replace the old 14-day history list with a monthly adherence calendar.
calendar_patch = Path(__file__).with_name('apply_calendar_history.py')
exec(compile(calendar_patch.read_text(encoding='utf-8'), str(calendar_patch), 'exec'), {'__name__':'__main__'})

# Size history popups before show() so the entrance animation never visibly shifts sideways.
popup_stability_patch = Path(__file__).with_name('apply_history_popup_stability.py')
exec(compile(popup_stability_patch.read_text(encoding='utf-8'), str(popup_stability_patch), 'exec'), {'__name__':'__main__'})

# Keep feedback composition inside the app; the HTTPS endpoint is connected after Apps Script deployment.
feedback_patch = Path(__file__).with_name('apply_in_app_feedback.py')
exec(compile(feedback_patch.read_text(encoding='utf-8'), str(feedback_patch), 'exec'), {'__name__':'__main__'})

# Use the real AdMob app/banner IDs only in the production working tree.
admob_patch = Path(__file__).with_name('apply_production_admob.py')
exec(compile(admob_patch.read_text(encoding='utf-8'), str(admob_patch), 'exec'), {'__name__':'__main__'})

print('V3.0.3 purchase-restore, release-link, localized-name, back-navigation, medication/supplement, registration-date, calendar-history, stable-history-popup, in-app-feedback, and production AdMob patches applied')
