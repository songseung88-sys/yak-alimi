from pathlib import Path
root=Path("yak_alimi_v21_work")
main_file=root/"app/src/main/java/com/yakalimi/app/MainActivity.java"
i18n_file=root/"app/src/main/java/com/yakalimi/app/I18n.java"

s=main_file.read_text(encoding="utf-8")
old='''        addSupportOption(box,"☕",I18n.t(this,"support_coffee"),I18n.t(this,"support_price_coffee"));
        addSupportOption(box,"🍲",I18n.t(this,"support_meal"),I18n.t(this,"support_price_meal"));
'''
new='''        addSupportOption(box,"☕",I18n.t(this,"support_coffee"),BuildConfig.SUPPORT_COFFEE_PRODUCT_ID,I18n.t(this,"support_price_coffee"));
        addSupportOption(box,"🍲",I18n.t(this,"support_meal"),BuildConfig.SUPPORT_MEAL_PRODUCT_ID,I18n.t(this,"support_price_meal"));
'''
if old not in s: raise SystemExit("support rows missing")
s=s.replace(old,new,1)

old='''    private void addSupportOption(LinearLayout parent,String emoji,String title,String price){
'''
new='''    private void addSupportOption(LinearLayout parent,String emoji,String title,String productId,String fallbackPrice){
        String playPrice=billingManager.getSupportFormattedPrice(productId);
        String price=(playPrice==null || playPrice.trim().isEmpty())?fallbackPrice:playPrice;
'''
if old not in s: raise SystemExit("support signature missing")
s=s.replace(old,new,1)

old='''        row.setOnClickListener(v->Toast.makeText(this,I18n.t(this,"support_payment_coming"),Toast.LENGTH_SHORT).show());
'''
new='''        row.setOnClickListener(v->billingManager.purchaseSupport(productId));
'''
if old not in s: raise SystemExit("support click missing")
s=s.replace(old,new,1)
main_file.write_text(s,encoding="utf-8")

i=i18n_file.read_text(encoding="utf-8")
anchor='        M.put("support_payment_coming",'
pos=i.find(anchor)
if pos<0: raise SystemExit("i18n anchor missing")
end=i.find("\n",pos)
addition='''        M.put("support_thanks",new String[]{"응원해 주셔서 감사합니다. 약 알리미를 더 꾸준히 다듬겠습니다.","Thank you for your support. It helps keep Medication Reminder improving.","応援ありがとうございます。お薬リマインダーをこれからも丁寧に改善していきます。","感谢您的支持。我们会继续认真改进用药提醒。","आपके सहयोग के लिए धन्यवाद। इससे Medication Reminder को लगातार बेहतर बनाने में मदद मिलती है।","Gracias por tu apoyo. Nos ayuda a seguir mejorando Recordatorio de medicación."});
'''
i=i[:end+1]+addition+i[end+1:]
i18n_file.write_text(i,encoding="utf-8")
print("v312 support UI applied")
