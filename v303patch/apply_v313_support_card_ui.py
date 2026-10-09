from pathlib import Path
root=Path("yak_alimi_v21_work")
main_file=root/"app/src/main/java/com/yakalimi/app/MainActivity.java"
i18n_file=root/"app/src/main/java/com/yakalimi/app/I18n.java"

s=main_file.read_text(encoding="utf-8")
anchor='''        TextView intro=text(I18n.t(this,"support_intro"),15,MUTED,false);
        intro.setPadding(0,0,0,dp(16));
        box.addView(intro);

        addSupportOption(box,"☕",I18n.t(this,"support_coffee"),BuildConfig.SUPPORT_COFFEE_PRODUCT_ID,I18n.t(this,"support_price_coffee"));
'''
insert='''        TextView intro=text(I18n.t(this,"support_intro"),15,MUTED,false);
        intro.setPadding(0,0,0,dp(8));
        box.addView(intro);

        TextView rewardHint=text(I18n.t(this,"support_card_explainer"),13,MUTED,false);
        rewardHint.setPadding(0,0,0,dp(16));
        box.addView(rewardHint);

        int coffeeCards=SupportRewardStore.coffee(this);
        int mealCards=SupportRewardStore.meal(this);
        int supportTotal=coffeeCards+mealCards;
        if(supportTotal>0){
            LinearLayout rewardBox=new LinearLayout(this);
            rewardBox.setOrientation(LinearLayout.VERTICAL);
            rewardBox.setPadding(dp(14),dp(12),dp(14),dp(12));
            rewardBox.setBackground(round(Color.rgb(247,250,255),16,Color.rgb(218,226,236),1));
            rewardBox.addView(text(I18n.t(this,"support_cards_title"),14,TEXT,true));
            TextView rewardCounts=text("☕  "+coffeeCards+"    🍲  "+mealCards,18,BLUE,true);
            rewardCounts.setPadding(0,dp(6),0,0);
            rewardBox.addView(rewardCounts);
            LinearLayout.LayoutParams rewardLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
            rewardLp.bottomMargin=dp(14);
            box.addView(rewardBox,rewardLp);
        }

        addSupportOption(box,"☕",I18n.t(this,"support_coffee"),BuildConfig.SUPPORT_COFFEE_PRODUCT_ID,I18n.t(this,"support_price_coffee"));
'''
if anchor not in s:
    raise SystemExit("support dialog anchor missing")
s=s.replace(anchor,insert,1)
main_file.write_text(s,encoding="utf-8")

i=i18n_file.read_text(encoding="utf-8")
anchor='        M.put("support_thanks",'
pos=i.find(anchor)
if pos<0:
    raise SystemExit("support_thanks anchor missing")
end=i.find("\n",pos)
addition='''        M.put("support_card_explainer",new String[]{"응원 1회마다 앱 안에 작은 감사 카드가 한 장 추가됩니다.","Each support purchase adds a small thank-you card inside the app.","応援1回ごとに、アプリ内に小さな感謝カードが1枚追加されます。","每次支持都会在应用内增加一张小小的感谢卡。","हर सहयोग खरीद पर ऐप में एक छोटा धन्यवाद कार्ड जुड़ता है।","Cada apoyo añade una pequeña tarjeta de agradecimiento dentro de la app."});
        M.put("support_cards_title",new String[]{"내 응원 카드","My support cards","応援カード","我的支持卡片","मेरे सहयोग कार्ड","Mis tarjetas de apoyo"});
        M.put("support_card_added",new String[]{"응원해 주셔서 감사합니다. 감사 카드가 추가되었습니다.","Thank you for your support. A thank-you card was added.","応援ありがとうございます。感謝カードを追加しました。","感谢您的支持。已添加一张感谢卡。","आपके सहयोग के लिए धन्यवाद। धन्यवाद कार्ड जोड़ दिया गया है।","Gracias por tu apoyo. Se añadió una tarjeta de agradecimiento."});
'''
i=i[:end+1]+addition+i[end+1:]
i18n_file.write_text(i,encoding="utf-8")
print("Support card collection UI applied")
