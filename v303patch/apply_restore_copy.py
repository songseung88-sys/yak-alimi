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

print('V3.0.3 purchase-restore copy patch applied')
