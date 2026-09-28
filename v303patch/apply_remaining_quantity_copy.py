"""Use friendly quantity wording throughout the medication UI."""

from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
main = root / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
source = main.read_text(encoding='utf-8')
old = 'String stock=m.stockInitialized?I18n.qty(this,m.inventory):I18n.t(this,"stock_unregistered");'
new = 'String stock=m.stockInitialized?I18n.t(this,"remaining_quantity",I18n.qty(this,m.inventory)):I18n.t(this,"stock_unregistered");'
if source.count(old) != 1:
    raise SystemExit('Home quantity label not found exactly once')
main.write_text(source.replace(old, new, 1), encoding='utf-8')

i18n = root / 'app/src/main/java/com/yakalimi/app/I18n.java'
translations = i18n.read_text(encoding='utf-8')
anchor = '        M.put("my_medicines",'
line = '        M.put("remaining_quantity",new String[]{"잔여 %s","%s remaining","残り%s","剩余%s","%s शेष","Quedan %s"});\n'
if translations.count(anchor) != 1 or 'M.put("remaining_quantity",' in translations:
    raise SystemExit('Quantity translation insertion point is not unique')
translations = translations.replace(anchor, line + anchor, 1)

replacements = {
    '"재고 미등록"': ('"수량 미입력"', 1),
    '"현재 보유량"': ('"현재 남은 개수"', 1),
    '"재고 알림 기준"': ('"알림 기준 개수"', 1),
    '"추가 후 예상 재고"': ('"추가 후 남은 개수"', 1),
    '"재고 추가"': ('"수량 추가"', 2),
    '"재고 알림"': ('"남은 개수 알림"', 2),
    '재고에서 차감된 1개도 되돌립니다.': ('차감했던 1개를 남은 개수에 다시 더합니다.', 1),
    '재고 정보': ('남은 개수 정보', 2),
    '"남은 수량 알림"': ('"남은 개수 알림"', 1),
    '남은 수량이 적습니다.': ('남은 개수가 적어요.', 1),
    '"%s이(가) %s 남았습니다"': ('"%s · 잔여 %s"', 1),
}
for old, (new, expected) in replacements.items():
    if translations.count(old) != expected:
        raise SystemExit(f'Unexpected count for {old}: {translations.count(old)}')
    translations = translations.replace(old, new)
if '재고' in translations:
    raise SystemExit('Korean stock wording remains in app translations')
i18n.write_text(translations, encoding='utf-8')
print('Remaining-quantity copy applied')
