"""Use friendly quantity wording throughout the medication UI."""

from pathlib import Path
import json
import re
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

# Keep all six supported languages consistent with the friendlier Korean copy.
# Language order: Korean, English, Japanese, Chinese, Hindi, Spanish.
localized = {
    'stock_unregistered': [
        '수량 미입력', 'Quantity not entered', '数量未入力', '未填写数量',
        'संख्या दर्ज नहीं', 'Cantidad sin indicar',
    ],
    'add_stock': [
        '수량 추가', 'Add quantity', '数量を追加', '增加数量',
        'संख्या बढ़ाएँ', 'Añadir cantidad',
    ],
    'current_inventory': [
        '현재 남은 개수', 'Remaining quantity', '現在の残り', '目前剩余数量',
        'अभी बची संख्या', 'Cantidad restante',
    ],
    'low_stock_alert': [
        '남은 개수 알림', 'Low quantity reminder', '残り少ないときの通知', '剩余数量提醒',
        'कम मात्रा का रिमाइंडर', 'Aviso de pocas unidades',
    ],
    'stock_add_title': [
        '수량 추가', 'Add quantity', '数量を追加', '增加数量',
        'संख्या बढ़ाएँ', 'Añadir cantidad',
    ],
    'expected_stock': [
        '추가 후 남은 개수', 'Remaining after adding', '追加後の残り', '添加后剩余数量',
        'जोड़ने के बाद बची संख्या', 'Cantidad restante tras añadir',
    ],
    'stock_threshold': [
        '알림 기준 개수', 'Remind when this many remain', '通知する残りの数', '剩余多少时提醒',
        'इतने बचने पर रिमाइंडर', 'Avisar cuando queden',
    ],
    'channel_stock': [
        '남은 개수 알림', 'Quantity reminders', '残りの数の通知', '剩余数量提醒',
        'बची संख्या के रिमाइंडर', 'Avisos de cantidad restante',
    ],
    'channel_stock_desc': [
        '남은 개수 알림', 'Reminders when quantities run low', '残りが少ないときの通知', '剩余数量不足时提醒',
        'कम संख्या बचने पर रिमाइंडर', 'Avisos cuando queden pocas unidades',
    ],
    'undo_message': [
        '%s · %s 기록을 삭제할까요?\n차감했던 1개를 남은 개수에 다시 더합니다.',
        'Delete the %s · %s record?\nOne unit will be added back to the remaining quantity.',
        '%s・%sの記録を削除しますか？\n残りの数に1個戻します。',
        '删除%s · %s的记录？\n扣除的1个会加回剩余数量。',
        '%s · %s का रिकॉर्ड हटाएँ?\nघटाई गई 1 इकाई बची संख्या में वापस जुड़ जाएगी।',
        '¿Eliminar el registro de %s · %s?\nLa unidad descontada volverá a la cantidad restante.',
    ],
    'feedback_privacy_note': [
        '약·영양제 이름, 복용 기록, 남은 개수 정보는 자동으로 전송되지 않습니다.',
        'Medication, supplement, intake-record and remaining-quantity data are never attached automatically.',
        '薬・サプリ名、服用記録、残りの数は自動送信されません。',
        '药品、营养补充剂、服用记录和剩余数量不会自动发送。',
        'दवा, सप्लीमेंट, सेवन रिकॉर्ड और बची संख्या अपने-आप नहीं भेजी जाती।',
        'Los datos de medicamentos, suplementos, tomas y cantidades restantes no se adjuntan automáticamente.',
    ],
    'privacy_policy_text': [
        '약·영양제 이름, 복용 시간, 복용 기록과 남은 개수 정보는 사용자 기기에만 저장되며 약 알리미 서버로 전송되지 않습니다.',
        'Medication or supplement names, schedules, intake records, and remaining quantities are stored only on your device and are not sent to an app server.',
        '薬・サプリメント名、服用時刻、服用記録、残りの数は端末にのみ保存され、アプリのサーバーには送信されません。',
        '药物或保健品名称、服用时间、服用记录和剩余数量仅保存在用户设备上，不会发送到应用服务器。',
        'दवा या सप्लीमेंट के नाम, समय, सेवन रिकॉर्ड और बची संख्या केवल आपके डिवाइस पर संग्रहीत होती है और ऐप सर्वर पर नहीं भेजी जाती।',
        'Los nombres, horarios, registros de tomas y cantidades restantes se guardan solo en el dispositivo y no se envían al servidor de la app.',
    ],
}
for key, values in localized.items():
    if len(values) != 6:
        raise SystemExit(f'Expected six translations for {key}')
    pattern = rf'^        M\.put\("{key}",new String\[\]\{{.*\}}\);$'
    rendered = '        M.put(' + json.dumps(key, ensure_ascii=False) + ',new String[]{' + ','.join(json.dumps(v, ensure_ascii=False) for v in values) + '});'
    translations, count = re.subn(pattern, lambda match: rendered, translations, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f'Translation key {key} not found exactly once')

i18n.write_text(translations, encoding='utf-8')
print('Remaining-quantity copy applied in six languages')
