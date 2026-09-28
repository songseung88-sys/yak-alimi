from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_closedtest_work')
BILLING = ROOT / 'app/src/main/java/com/yakalimi/app/BillingManager.java'
I18N = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
MAIN = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'

# This patch is applied ONLY to the separate closed-test working copy.
# The normal production working tree is left untouched.

# 1) Force Premium entitlement for closed-test participants.
s = BILLING.read_text(encoding='utf-8')
anchor = '    private static final String KEY_PREMIUM = "premium_unlocked";\n'
if anchor not in s:
    raise SystemExit('BillingManager premium key anchor missing')
insert = anchor + '    private static final boolean CLOSED_TEST_PREMIUM = true;\n'
s = s.replace(anchor, insert, 1)

old = '''    public static boolean isPremium(Context context) {\n        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)\n                .getBoolean(KEY_PREMIUM, false);\n    }'''
new = '''    public static boolean isClosedTestPremium() {\n        return CLOSED_TEST_PREMIUM;\n    }\n\n    public static boolean isPremium(Context context) {\n        if (CLOSED_TEST_PREMIUM) return true;\n        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)\n                .getBoolean(KEY_PREMIUM, false);\n    }'''
if old not in s:
    raise SystemExit('BillingManager isPremium block missing')
s = s.replace(old, new, 1)
BILLING.write_text(s, encoding='utf-8')

# 2) Add clear tester-only labels in all six supported languages.
s = I18N.read_text(encoding='utf-8')
pattern = re.compile(r'(\s*M\.put\("premium_active",new String\[\]\{.*?\}\);\n)', re.S)
m = pattern.search(s)
if not m:
    raise SystemExit('premium_active i18n anchor missing')
extra = m.group(1) + (
    '        M.put("test_premium_active",new String[]{'
    '"테스트 프리미엄 활성화됨",'
    '"Test Premium active",'
    '"テスト用プレミアム有効",'
    '"测试高级版已启用",'
    '"टेस्ट प्रीमियम सक्रिय",'
    '"Premium de prueba activo"});\n'
    '        M.put("test_premium_desc",new String[]{'
    '"비공개 테스트 기간에는 결제 없이 프리미엄 기능을 사용할 수 있습니다.",'
    '"Premium features are unlocked at no charge during the closed test.",'
    '"クローズドテスト期間中は購入せずにプレミアム機能を利用できます。",'
    '"封闭测试期间无需付费即可使用高级功能。",'
    '"क्लोज़्ड टेस्ट के दौरान प्रीमियम सुविधाएँ बिना भुगतान के उपलब्ध हैं।",'
    '"Durante la prueba cerrada, las funciones Premium están disponibles sin pago."});\n'
)
s = s[:m.start()] + extra + s[m.end():]
I18N.write_text(s, encoding='utf-8')

# 3) Show the tester entitlement explicitly in Settings and hide purchase/restore controls.
s = MAIN.read_text(encoding='utf-8')
old = '''        boolean unlocked=BillingManager.isPremium(this);\n        TextView ps=text(unlocked?I18n.t(this,"premium_active"):I18n.t(this,"free_plan"),19,unlocked?BLUE:TEXT,true);premium.addView(ps);\n        TextView pd=text(unlocked?I18n.t(this,"premium_active_desc"):I18n.t(this,"free_plan_desc"),15,MUTED,false);pd.setPadding(0,dp(4),0,dp(10));premium.addView(pd);'''
new = '''        boolean unlocked=BillingManager.isPremium(this);\n        boolean testPremium=BillingManager.isClosedTestPremium();\n        TextView ps=text(testPremium?I18n.t(this,"test_premium_active"):(unlocked?I18n.t(this,"premium_active"):I18n.t(this,"free_plan")),19,(unlocked||testPremium)?BLUE:TEXT,true);premium.addView(ps);\n        TextView pd=text(testPremium?I18n.t(this,"test_premium_desc"):(unlocked?I18n.t(this,"premium_active_desc"):I18n.t(this,"free_plan_desc")),15,MUTED,false);pd.setPadding(0,dp(4),0,dp(10));premium.addView(pd);'''
if old not in s:
    raise SystemExit('MainActivity premium card block missing')
s = s.replace(old, new, 1)
MAIN.write_text(s, encoding='utf-8')

print('Closed-test Premium entitlement applied to test working copy only')
