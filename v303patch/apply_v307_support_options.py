from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_dir = root / "app/src/main/java/com/yakalimi/app"
main_file = java_dir / "MainActivity.java"
i18n_file = java_dir / "I18n.java"
build_file = root / "app/build.gradle"

main = main_file.read_text(encoding="utf-8")

old_method = '''    private void supportDeveloper(){
        if(BuildConfig.SUPPORT_URL==null || BuildConfig.SUPPORT_URL.trim().isEmpty()){
            new AlertDialog.Builder(this).setTitle(I18n.t(this,"support_developer"))
                    .setMessage(I18n.t(this,"support_not_configured"))
                    .setPositiveButton(android.R.string.ok,null).show();
            return;
        }
        try{startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(BuildConfig.SUPPORT_URL)));}
        catch(Exception e){Toast.makeText(this,I18n.t(this,"cannot_open_link"),Toast.LENGTH_LONG).show();}
    }
'''

new_method = '''    private void supportDeveloper(){
        LinearLayout box=new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20),dp(4),dp(20),dp(6));

        TextView intro=text(I18n.t(this,"support_intro"),15,MUTED,false);
        intro.setPadding(0,0,0,dp(16));
        box.addView(intro);

        addSupportOption(box,"☕",I18n.t(this,"support_coffee"),I18n.t(this,"support_price_coffee"));
        addSupportOption(box,"🍲",I18n.t(this,"support_meal"),I18n.t(this,"support_price_meal"));

        new AlertDialog.Builder(this)
                .setTitle(I18n.t(this,"support_developer"))
                .setView(box)
                .setNegativeButton(I18n.t(this,"close"),null)
                .show();
    }

    private void addSupportOption(LinearLayout parent,String emoji,String title,String price){
        LinearLayout row=new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setPadding(dp(16),dp(14),dp(16),dp(14));
        row.setBackground(round(Color.WHITE,18,Color.rgb(218,226,236),1));
        row.setClickable(true);
        row.setFocusable(true);

        TextView icon=text(emoji,28,TEXT,false);
        icon.setGravity(Gravity.CENTER);
        row.addView(icon,new LinearLayout.LayoutParams(dp(46),dp(46)));

        LinearLayout labels=new LinearLayout(this);
        labels.setOrientation(LinearLayout.VERTICAL);
        labels.setPadding(dp(10),0,dp(8),0);
        labels.addView(text(title,17,TEXT,true));
        TextView priceText=text(price,14,BLUE,true);
        priceText.setPadding(0,dp(3),0,0);
        labels.addView(priceText);
        row.addView(labels,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));

        TextView arrow=text("›",24,MUTED,false);
        arrow.setGravity(Gravity.CENTER);
        row.addView(arrow,new LinearLayout.LayoutParams(dp(28),dp(46)));

        row.setOnClickListener(v->Toast.makeText(this,I18n.t(this,"support_payment_coming"),Toast.LENGTH_SHORT).show());
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin=dp(10);
        parent.addView(row,lp);
    }
'''

if old_method not in main:
    raise SystemExit("supportDeveloper method anchor not found")
main = main.replace(old_method, new_method, 1)
main_file.write_text(main, encoding="utf-8")

i18n = i18n_file.read_text(encoding="utf-8")
anchor = '        M.put("support_not_configured",new String[]{"테스트 버전에서는 응원 링크가 아직 연결되지 않았습니다. 배포 전에 연결합니다.","The support link is not connected in this test build. It will be configured before release.","テスト版では応援リンクはまだ設定されていません。公開前に設定します。","测试版尚未连接支持链接，将在发布前设置。","टेस्ट बिल्ड में समर्थन लिंक अभी जुड़ा नहीं है। रिलीज़ से पहले सेट होगा।","El enlace de apoyo aún no está configurado en esta versión de prueba. Se añadirá antes del lanzamiento."});\n'
if anchor not in i18n:
    raise SystemExit("support I18n anchor not found")
insert = anchor + '''        M.put("support_intro",new String[]{"약 알리미가 일상에 도움이 되었다면 개발을 계속할 수 있도록 응원해 주세요.","If Medication Reminder has been helpful in your daily life, you can support continued development.","お薬リマインダーが日々の生活に役立っていると感じたら、開発を続けるために応援していただけるとうれしいです。","如果用药提醒对您的日常生活有所帮助，欢迎支持我们继续开发。","यदि Medication Reminder आपके रोज़मर्रा के जीवन में उपयोगी रहा है, तो इसके विकास को जारी रखने में सहयोग करें।","Si Recordatorio de medicación te resulta útil en el día a día, puedes apoyar su desarrollo continuo."});
        M.put("support_coffee",new String[]{"커피 한 잔 선물하기","Buy the developer a coffee","コーヒー一杯を贈る","请开发者喝杯咖啡","डेवलपर को एक कॉफी दें","Invitar al desarrollador a un café"});
        M.put("support_meal",new String[]{"국밥 한 그릇 든든하게","Buy the developer a meal","開発者にご飯を一食おごる","请开发者吃顿饭","डेवलपर को एक भरपेट भोजन दें","Invitar al desarrollador a una comida"});
        M.put("support_price_coffee",new String[]{"₩5,000","₩5,000","₩5,000","₩5,000","₩5,000","₩5,000"});
        M.put("support_price_meal",new String[]{"₩10,000","₩10,000","₩10,000","₩10,000","₩10,000","₩10,000"});
        M.put("support_payment_coming",new String[]{"결제 연결은 다음 단계에서 추가할 예정입니다.","Payment will be connected in a later update.","決済機能は今後のアップデートで接続する予定です。","支付功能将在后续更新中接入。","भुगतान सुविधा बाद के अपडेट में जोड़ी जाएगी।","El pago se conectará en una actualización posterior."});
'''
i18n = i18n.replace(anchor, insert, 1)
i18n_file.write_text(i18n, encoding="utf-8")

build = build_file.read_text(encoding="utf-8")
if "versionCode 38" not in build or "versionName '3.0.6'" not in build:
    raise SystemExit("Expected v3.0.6 version anchors not found")
build = build.replace("versionCode 38", "versionCode 40", 1)
build = build.replace("versionName '3.0.6'", "versionName '3.0.7'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.7 developer support options patch applied")
