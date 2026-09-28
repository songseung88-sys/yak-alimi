from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
MAIN = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'

s = MAIN.read_text(encoding='utf-8')

# Keep the calendar visually quiet. The marks are self-explanatory once the user taps a date,
# where the popup gives the full status label.
legend = '''        LinearLayout legend=new LinearLayout(this);\n        legend.setOrientation(LinearLayout.HORIZONTAL);\n        legend.setGravity(Gravity.CENTER);\n        legend.setPadding(0,dp(10),0,0);\n        TextView lo=text("O  "+I18n.t(this,"calendar_all_done"),12,BLUE,true);lo.setGravity(Gravity.CENTER);\n        TextView lp=text("△  "+I18n.t(this,"calendar_partial"),12,WARNING,true);lp.setGravity(Gravity.CENTER);\n        TextView lx=text("X  "+I18n.t(this,"calendar_none_done"),12,Color.rgb(190,70,70),true);lx.setGravity(Gravity.CENTER);\n        legend.addView(lo,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));\n        legend.addView(lp,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));\n        legend.addView(lx,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));\n        calendar.addView(legend);\n\n'''
if legend not in s:
    raise SystemExit('calendar legend block missing')
s = s.replace(legend, '', 1)

# Samsung/One UI could visibly reposition AlertDialog while it measured differently-sized date
# contents. Replace AlertDialog entirely with a fixed-width custom Dialog, set all Window attributes
# before show(), and disable window animations. The first rendered frame is therefore already final.
old = '''        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle(TimeUtil.date(this,date))\n                .setView(scroll)\n                .setPositiveButton(I18n.t(this,"close"),null)\n                .create();\n        dialog.setOnShowListener(d->{\n            android.view.Window w=dialog.getWindow();\n            if(w!=null){\n                android.view.WindowManager.LayoutParams lp=new android.view.WindowManager.LayoutParams();\n                lp.copyFrom(w.getAttributes());\n                lp.width=(int)(getResources().getDisplayMetrics().widthPixels*0.90f);\n                lp.height=android.view.WindowManager.LayoutParams.WRAP_CONTENT;\n                w.setAttributes(lp);\n            }\n        });\n        dialog.show();'''

new = '''        int dialogWidth=(int)(getResources().getDisplayMetrics().widthPixels*0.88f);\n\n        LinearLayout panel=new LinearLayout(this);\n        panel.setOrientation(LinearLayout.VERTICAL);\n        panel.setPadding(dp(6),dp(14),dp(6),dp(8));\n        panel.setBackground(round(Color.WHITE,24,0,0));\n\n        TextView title=text(TimeUtil.date(this,date),20,TEXT,true);\n        title.setPadding(dp(18),dp(2),dp(18),dp(8));\n        panel.addView(title,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n        panel.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));\n\n        Button closeButton=smallButton(I18n.t(this,"close"));\n        LinearLayout.LayoutParams closeLp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(48));\n        closeLp.setMargins(dp(14),dp(6),dp(14),dp(4));\n        panel.addView(closeButton,closeLp);\n\n        android.app.Dialog dialog=new android.app.Dialog(this);\n        dialog.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE);\n        dialog.setCancelable(true);\n        dialog.setCanceledOnTouchOutside(true);\n        dialog.setContentView(panel,new ViewGroup.LayoutParams(dialogWidth,ViewGroup.LayoutParams.WRAP_CONTENT));\n        closeButton.setOnClickListener(v->dialog.dismiss());\n\n        android.view.Window w=dialog.getWindow();\n        if(w!=null){\n            w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));\n            w.setGravity(Gravity.CENTER);\n            w.setDimAmount(0.32f);\n            w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);\n            w.setWindowAnimations(0);\n            android.view.WindowManager.LayoutParams lp=w.getAttributes();\n            lp.width=dialogWidth;\n            lp.height=android.view.WindowManager.LayoutParams.WRAP_CONTENT;\n            lp.gravity=Gravity.CENTER;\n            w.setAttributes(lp);\n        }\n        dialog.show();'''

if old not in s:
    raise SystemExit('history AlertDialog block missing')
s = s.replace(old, new, 1)

MAIN.write_text(s, encoding='utf-8')
print('History calendar legend removed and popup replaced by a fixed-width custom Dialog')
