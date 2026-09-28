from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
MAIN = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'

s = MAIN.read_text(encoding='utf-8')
old = '''        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle(TimeUtil.date(this,date))\n                .setView(scroll)\n                .setPositiveButton(I18n.t(this,"close"),null)\n                .create();\n        dialog.setOnShowListener(d->{\n            android.view.Window w=dialog.getWindow();\n            if(w!=null){\n                android.view.WindowManager.LayoutParams lp=new android.view.WindowManager.LayoutParams();\n                lp.copyFrom(w.getAttributes());\n                lp.width=(int)(getResources().getDisplayMetrics().widthPixels*0.90f);\n                lp.height=android.view.WindowManager.LayoutParams.WRAP_CONTENT;\n                w.setAttributes(lp);\n            }\n        });\n        dialog.show();'''
new = '''        // Fix the popup width before it is shown. Changing Window attributes in OnShowListener\n        // caused a visible resize/sideways jump during the dialog entrance animation.\n        int minDialogContentWidth=(int)(getResources().getDisplayMetrics().widthPixels*0.78f);\n        scroll.setMinimumWidth(minDialogContentWidth);\n\n        AlertDialog dialog=new AlertDialog.Builder(this)\n                .setTitle(TimeUtil.date(this,date))\n                .setView(scroll)\n                .setPositiveButton(I18n.t(this,"close"),null)\n                .create();\n        dialog.show();'''
if old not in s:
    raise SystemExit('history popup sizing block missing')
s = s.replace(old, new, 1)
MAIN.write_text(s, encoding='utf-8')
print('History popup width stabilized before show; post-show window resize removed')
