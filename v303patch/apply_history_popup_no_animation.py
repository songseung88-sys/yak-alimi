"""Render record details inside MainActivity's existing window without animations."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "yak_alimi_v21_work")
main = root / "app/src/main/java/com/yakalimi/app/MainActivity.java"
s = main.read_text(encoding="utf-8")

old_scroll = "        panel.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));"
new_scroll = """        int maxScrollHeight=Math.max(dp(120),getResources().getDisplayMetrics().heightPixels-dp(190));
        scroll.measure(View.MeasureSpec.makeMeasureSpec(dialogWidth-dp(48),View.MeasureSpec.AT_MOST),
                View.MeasureSpec.makeMeasureSpec(maxScrollHeight,View.MeasureSpec.AT_MOST));
        panel.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                Math.min(scroll.getMeasuredHeight(),maxScrollHeight)));"""
if s.count(old_scroll) != 1:
    raise SystemExit("record popup scroll anchor missing")
s = s.replace(old_scroll, new_scroll, 1)

old_dialog = """        android.app.Dialog dialog=new android.app.Dialog(this);
        dialog.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE);
        dialog.setCancelable(true);
        dialog.setCanceledOnTouchOutside(true);
        dialog.setContentView(panel,new ViewGroup.LayoutParams(dialogWidth,ViewGroup.LayoutParams.WRAP_CONTENT));
        closeButton.setOnClickListener(v->dialog.dismiss());

        android.view.Window w=dialog.getWindow();
        if(w!=null){
            w.setBackgroundDrawable(new android.graphics.drawable.ColorDrawable(Color.TRANSPARENT));
            w.setGravity(Gravity.CENTER);
            w.setDimAmount(0.32f);
            w.addFlags(android.view.WindowManager.LayoutParams.FLAG_DIM_BEHIND);
            w.setWindowAnimations(0);
            android.view.WindowManager.LayoutParams lp=w.getAttributes();
            lp.width=dialogWidth;
            lp.height=android.view.WindowManager.LayoutParams.WRAP_CONTENT;
            lp.gravity=Gravity.CENTER;
            w.setAttributes(lp);
        }
        dialog.show();"""
new_overlay = """        // Add both the dim layer and the fixed-width panel in one layout pass.
        // No separate dialog window, animation, translation, or delayed width change.
        FrameLayout overlay=new FrameLayout(this);
        overlay.setBackgroundColor(Color.argb(82,0,0,0));
        overlay.setOnClickListener(v->dismissHistoryPopup());
        panel.setOnClickListener(v->{}); // A tap inside must not reach the dim layer.
        overlay.addView(panel,new FrameLayout.LayoutParams(dialogWidth,
                ViewGroup.LayoutParams.WRAP_CONTENT,Gravity.CENTER));
        closeButton.setOnClickListener(v->dismissHistoryPopup());
        dismissHistoryPopup();
        historyPopupOverlay=overlay;
        ((FrameLayout)findViewById(android.R.id.content)).addView(overlay,
                new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT));"""
if s.count(old_dialog) != 1:
    raise SystemExit("existing custom dialog block missing")
s = s.replace(old_dialog, new_overlay, 1)

back = "    private void handleAppBackPressed(){\n"
if s.count(back) != 1:
    raise SystemExit("back navigation anchor missing")
s = s.replace(back, """    private FrameLayout historyPopupOverlay;

    private void dismissHistoryPopup(){
        if(historyPopupOverlay==null) return;
        ViewGroup parent=(ViewGroup)historyPopupOverlay.getParent();
        if(parent!=null) parent.removeView(historyPopupOverlay);
        historyPopupOverlay=null;
    }

    private void handleAppBackPressed(){
        if(historyPopupOverlay!=null){dismissHistoryPopup();return;}
""", 1)

undo = "                if(taken) row.setOnClickListener(v->{\n                    confirmUndo(m.id,date,slot);"
if s.count(undo) != 1:
    raise SystemExit("record undo click anchor missing")
s = s.replace(undo, "                if(taken) row.setOnClickListener(v->{\n                    dismissHistoryPopup();\n                    confirmUndo(m.id,date,slot);", 1)

main.write_text(s, encoding="utf-8")
print("Record popup now opens instantly in the Activity window without animation")
