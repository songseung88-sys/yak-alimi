from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

def replace(path, old, new, count=None):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing expected text in {path}: {old[:140]!r}')
    s = s.replace(old, new, count if count is not None else -1)
    p.write_text(s, encoding='utf-8')

# Version
replace('app/build.gradle', 'versionCode 32', 'versionCode 33', 1)
replace('app/build.gradle', "versionName '3.0.2'", "versionName '3.0.3'", 1)

# Premium copy: concise benefits, localized one-time purchase text, and restore labels.
i18n_path = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
s = i18n_path.read_text(encoding='utf-8')
repls = {
'''        M.put("premium_active_desc",new String[]{"광고 없이 여러 약을 등록할 수 있습니다.","No ads and unlimited medicines.","広告なしで複数の薬を登録できます。","无广告，可添加多种药物。","विज्ञापन नहीं, कई दवाएँ जोड़ें।","Sin anuncios y con medicamentos ilimitados."});''':
'''        M.put("premium_active_desc",new String[]{"광고 없이 여러 약을 등록하고 모든 기능을 사용할 수 있습니다.","No ads, multiple medications, and access to all features.","広告なしで複数の薬を登録し、すべての機能を利用できます。","无广告，可添加多种药物并使用全部功能。","बिना विज्ञापन, कई दवाइयाँ और सभी सुविधाएँ इस्तेमाल करें।","Sin anuncios, varios medicamentos y acceso a todas las funciones."});''',
'''        M.put("unlock_premium",new String[]{"1회 구매로 프리미엄 잠금 해제","Unlock Premium with one purchase","1回購入でプレミアムを解除","一次购买解锁高级版","एक बार खरीदकर प्रीमियम अनलॉक करें","Desbloquear Premium con un pago"});''':
'''        M.put("unlock_premium",new String[]{"프리미엄 구매","Unlock Premium","プレミアムを購入","升级高级版","प्रीमियम खरीदें","Comprar Premium"});''',
'''        M.put("restore_purchase",new String[]{"구매 복원","Restore purchase","購入を復元","恢复购买","खरीदारी पुनर्स्थापित करें","Restaurar compra"});''':
'''        M.put("restore_purchase",new String[]{"구매 복원","Restore Purchase","購入を復元","恢复购买","खरीदारी पुनर्स्थापित करें","Restaurar compra"});''',
'''        M.put("premium_message",new String[]{"무료 버전은 약 1개까지 등록할 수 있고 하단에 광고가 표시됩니다. 프리미엄은 1회 구매로 광고를 제거하고 여러 약을 등록할 수 있습니다.","The free version supports 1 medicine and shows a banner ad. A one-time Premium purchase removes ads and unlocks multiple medicines.","無料版は薬1つまでで下部に広告が表示されます。プレミアムは1回の購入で広告を削除し、複数の薬を登録できます。","免费版最多添加1种药物并显示横幅广告。一次购买高级版即可去除广告并添加多种药物。","मुफ़्त संस्करण में 1 दवा और नीचे विज्ञापन है। एक बार प्रीमियम खरीदने पर विज्ञापन हटेंगे और कई दवाएँ जोड़ सकेंगे।","La versión gratuita permite 1 medicamento y muestra un banner. Un único pago Premium elimina anuncios y permite varios medicamentos."});''':
'''        M.put("premium_message",new String[]{"✓ 광고 없이 사용\\n✓ 여러 약 등록\\n✓ 모든 기능 사용","✓ No ads\\n✓ Add multiple medications\\n✓ Access all features","✓ 広告なし\\n✓ 複数の薬を登録\\n✓ すべての機能を利用","✓ 无广告\\n✓ 可添加多种药物\\n✓ 使用全部功能","✓ बिना विज्ञापन\\n✓ कई दवाइयाँ जोड़ें\\n✓ सभी सुविधाएँ इस्तेमाल करें","✓ Sin anuncios\\n✓ Añade varios medicamentos\\n✓ Accede a todas las funciones"});'''
}
for old, new in repls.items():
    if old not in s:
        raise SystemExit('premium i18n source text missing')
    s = s.replace(old, new, 1)

anchor = '        M.put("restore_purchase",new String[]{"구매 복원","Restore Purchase","購入を復元","恢复购买","खरीदारी पुनर्स्थापित करें","Restaurar compra"});\n'
if anchor not in s:
    raise SystemExit('restore_purchase anchor missing')
insert = anchor + '''        M.put("premium_subtitle",new String[]{"약 알리미를 더 편리하게 사용하세요","Make medication management easier","お薬の管理をもっと便利に","更轻松地管理用药","दवाइयों का प्रबंधन और आसान बनाएं","Gestiona tus medicamentos con más comodidad"});\n        M.put("premium_price_line",new String[]{"%s · 한 번만 결제","%s · One-time purchase","%s · 1回限りのお支払い","%s · 一次性购买","%s · एक बार का भुगतान","%s · Pago único"});\n        M.put("premium_helper",new String[]{"한 번 구매하면 계속 사용할 수 있습니다.","Pay once and keep Premium.","一度購入すれば、ずっと利用できます。","一次购买，长期使用。","एक बार खरीदें, हमेशा इस्तेमाल करें।","Paga una vez y conserva Premium."});\n        M.put("premium_required_title",new String[]{"프리미엄이 필요합니다","Premium required","プレミアムが必要です","需要高级版","प्रीमियम आवश्यक है","Se necesita Premium"});\n        M.put("premium_required_message",new String[]{"무료 버전에서는 약을 1개까지 등록할 수 있습니다. 프리미엄을 구매하면 광고 없이 여러 약을 등록할 수 있습니다.","The free version supports 1 medication. Unlock Premium to add multiple medications and remove ads.","無料版では薬を1種類まで登録できます。プレミアムにすると、広告なしで複数の薬を登録できます。","免费版最多可添加 1 种药物。升级高级版后，可添加多种药物并移除广告。","मुफ्त संस्करण में 1 दवा तक जोड़ सकते हैं। प्रीमियम खरीदने पर कई दवाइयाँ जोड़ सकते हैं और विज्ञापन हट जाते हैं।","La versión gratuita permite registrar 1 medicamento. Con Premium puedes añadir varios medicamentos y eliminar los anuncios."});\n'''
s = s.replace(anchor, insert, 1)
i18n_path.write_text(s, encoding='utf-8')

# Expose the localized Google Play price without locking compilation to one specific
# Billing Library one-time-offer accessor. Reflection supports both legacy and newer APIs.
billing = ROOT / 'app/src/main/java/com/yakalimi/app/BillingManager.java'
s = billing.read_text(encoding='utf-8')
marker = '    public void purchasePremium() {\n'
if marker not in s:
    raise SystemExit('BillingManager purchasePremium marker missing')
method = '''    public String getPremiumFormattedPrice() {\n        if (premiumDetails == null) return null;\n        try {\n            Object listObject = premiumDetails.getClass()\n                    .getMethod("getOneTimePurchaseOfferDetailsList").invoke(premiumDetails);\n            if (listObject instanceof java.util.List && !((java.util.List<?>) listObject).isEmpty()) {\n                Object offer = ((java.util.List<?>) listObject).get(0);\n                Object value = offer.getClass().getMethod("getFormattedPrice").invoke(offer);\n                if (value != null) return value.toString();\n            }\n        } catch (Exception ignored) { }\n        try {\n            Object offer = premiumDetails.getClass()\n                    .getMethod("getOneTimePurchaseOfferDetails").invoke(premiumDetails);\n            if (offer != null) {\n                Object value = offer.getClass().getMethod("getFormattedPrice").invoke(offer);\n                if (value != null) return value.toString();\n            }\n        } catch (Exception ignored) { }\n        return null;\n    }\n\n'''
s = s.replace(marker, method + marker, 1)
billing.write_text(s, encoding='utf-8')

# Premium dialog: benefits + localized Play price + one-time-purchase helper.
main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')
old_dialog = '''    private void showPremiumDialog(){\n        new AlertDialog.Builder(this)\n                .setTitle(I18n.t(this,"premium_title"))\n                .setMessage(I18n.t(this,"premium_message"))\n                .setNegativeButton(I18n.t(this,"cancel"),null)\n                .setPositiveButton(I18n.t(this,"unlock_premium"),(d,w)->billingManager.purchasePremium())\n                .show();\n    }'''
new_dialog = '''    private void showPremiumDialog(){\n        String message=I18n.t(this,"premium_subtitle")+"\\n\\n"+I18n.t(this,"premium_message");\n        String formattedPrice=billingManager.getPremiumFormattedPrice();\n        if(formattedPrice!=null && !formattedPrice.trim().isEmpty())\n            message += "\\n\\n"+I18n.t(this,"premium_price_line",formattedPrice);\n        message += "\\n"+I18n.t(this,"premium_helper");\n        new AlertDialog.Builder(this)\n                .setTitle(I18n.t(this,"premium_title"))\n                .setMessage(message)\n                .setNegativeButton(I18n.t(this,"cancel"),null)\n                .setPositiveButton(I18n.t(this,"unlock_premium"),(d,w)->billingManager.purchasePremium())\n                .show();\n    }'''
if old_dialog not in s:
    raise SystemExit('showPremiumDialog block missing')
s = s.replace(old_dialog, new_dialog, 1)
main.write_text(s, encoding='utf-8')

print('V3.0.3 Premium patch applied')
