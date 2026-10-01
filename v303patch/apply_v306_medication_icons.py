from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_dir = root / "app/src/main/java/com/yakalimi/app"
main_file = java_dir / "MainActivity.java"
full_file = java_dir / "FullScreenAlarmActivity.java"
i18n_file = java_dir / "I18n.java"
build_file = root / "app/build.gradle"

store_java = r'''package com.yakalimi.app;

import android.content.Context;
import android.content.SharedPreferences;

import java.util.Locale;

public final class MedicationIconStore {
    public static final String ROUND = "round";
    public static final String OVAL = "oval";
    public static final String CAPSULE = "capsule";
    public static final String SOFTGEL = "softgel";
    public static final String SACHET = "sachet";
    public static final String LIQUID = "liquid";
    public static final String DROPS = "drops";
    public static final String SUPPLEMENT = "supplement";

    private static final String FILE = "yak_alimi_medication_icons";
    private static final String[] TYPES = {ROUND, OVAL, CAPSULE, SOFTGEL, SACHET, LIQUID, DROPS, SUPPLEMENT};

    private MedicationIconStore() {}

    private static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(FILE, Context.MODE_PRIVATE);
    }

    public static String get(Context c, String medId) {
        if (medId == null || medId.isEmpty()) return CAPSULE;
        return normalize(prefs(c).getString("icon_" + medId, CAPSULE));
    }

    public static void set(Context c, String medId, String type) {
        if (medId == null || medId.isEmpty()) return;
        prefs(c).edit().putString("icon_" + medId, normalize(type)).apply();
    }

    public static void delete(Context c, String medId) {
        if (medId == null || medId.isEmpty()) return;
        prefs(c).edit().remove("icon_" + medId).apply();
    }

    public static String[] types() { return TYPES.clone(); }

    public static String labelKey(String type) {
        switch (normalize(type)) {
            case ROUND: return "icon_round_tablet";
            case OVAL: return "icon_oval_tablet";
            case SOFTGEL: return "icon_softgel";
            case SACHET: return "icon_sachet";
            case LIQUID: return "icon_liquid";
            case DROPS: return "icon_drops";
            case SUPPLEMENT: return "icon_supplement";
            default: return "icon_capsule";
        }
    }

    public static String guessFromName(String name) {
        String s = name == null ? "" : name.toLowerCase(Locale.ROOT);
        if (containsAny(s, "비타민", "vitamin", "오메가", "omega", "유산균", "probiotic", "영양제", "supplement", "サプリ", "维生素", "补充剂", "vitamina", "suplemento")) return SUPPLEMENT;
        if (containsAny(s, "시럽", "syrup", "액상", "liquid", "シロップ", "液体", "jarabe", "líquido")) return LIQUID;
        if (containsAny(s, "안약", "점안", "drop", "drops", "点眼", "滴", "gotas")) return DROPS;
        if (containsAny(s, "가루", "분말", "powder", "포", "sachet", "散剤", "粉", "polvo", "sobre")) return SACHET;
        if (containsAny(s, "연질", "softgel", "ソフトカプセル", "软胶囊", "cápsula blanda")) return SOFTGEL;
        if (containsAny(s, "캡슐", "capsule", "カプセル", "胶囊", "cápsula")) return CAPSULE;
        if (containsAny(s, "정", "tablet", "錠", "片", "comprimido", "tableta")) return OVAL;
        return CAPSULE;
    }

    private static boolean containsAny(String s, String... terms) {
        for (String term : terms) if (s.contains(term)) return true;
        return false;
    }

    private static String normalize(String type) {
        if (type == null) return CAPSULE;
        for (String t : TYPES) if (t.equals(type)) return type;
        return CAPSULE;
    }
}
'''

view_java = r'''package com.yakalimi.app;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.view.View;

public final class MedicationIconView extends View {
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private String type;
    private final int blue = Color.rgb(23, 105, 232);
    private final int blueDark = Color.rgb(13, 78, 178);
    private final int blueSoft = Color.rgb(231, 242, 255);
    private final int teal = Color.rgb(36, 154, 154);
    private final int amber = Color.rgb(232, 160, 55);
    private final int ink = Color.rgb(45, 61, 82);

    public MedicationIconView(Context context, String type) {
        super(context);
        this.type = type == null ? MedicationIconStore.CAPSULE : type;
        setMinimumWidth(dp(36));
        setMinimumHeight(dp(36));
    }

    public void setType(String type) {
        this.type = type == null ? MedicationIconStore.CAPSULE : type;
        invalidate();
    }

    @Override protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float w = getWidth(), h = getHeight();
        float size = Math.min(w, h);
        float cx = w / 2f, cy = h / 2f;
        paint.setStrokeWidth(Math.max(dp(1.5f), size * .035f));
        paint.setStrokeCap(Paint.Cap.ROUND);
        paint.setStrokeJoin(Paint.Join.ROUND);

        switch (type) {
            case MedicationIconStore.ROUND: drawRoundTablet(canvas, cx, cy, size); break;
            case MedicationIconStore.OVAL: drawOvalTablet(canvas, cx, cy, size); break;
            case MedicationIconStore.SOFTGEL: drawSoftgel(canvas, cx, cy, size); break;
            case MedicationIconStore.SACHET: drawSachet(canvas, cx, cy, size); break;
            case MedicationIconStore.LIQUID: drawLiquid(canvas, cx, cy, size); break;
            case MedicationIconStore.DROPS: drawDrops(canvas, cx, cy, size); break;
            case MedicationIconStore.SUPPLEMENT: drawSupplement(canvas, cx, cy, size); break;
            default: drawCapsule(canvas, cx, cy, size); break;
        }
    }

    private void drawRoundTablet(Canvas c, float cx, float cy, float s) {
        float r = s * .28f;
        fill(blueSoft); c.drawCircle(cx, cy, r, paint);
        stroke(blue); c.drawCircle(cx, cy, r, paint);
        c.drawLine(cx - r * .58f, cy, cx + r * .58f, cy, paint);
    }

    private void drawOvalTablet(Canvas c, float cx, float cy, float s) {
        RectF r = new RectF(cx-s*.34f, cy-s*.19f, cx+s*.34f, cy+s*.19f);
        fill(Color.WHITE); c.drawRoundRect(r, s*.19f, s*.19f, paint);
        stroke(blue); c.drawRoundRect(r, s*.19f, s*.19f, paint);
        c.drawLine(cx, cy-s*.13f, cx, cy+s*.13f, paint);
    }

    private void drawCapsule(Canvas c, float cx, float cy, float s) {
        RectF r = new RectF(cx-s*.34f, cy-s*.17f, cx+s*.34f, cy+s*.17f);
        fill(blueSoft); c.drawRoundRect(r, s*.17f, s*.17f, paint);
        int save = c.save();
        c.clipRect(r.left, r.top, cx, r.bottom);
        fill(blue); c.drawRoundRect(r, s*.17f, s*.17f, paint);
        c.restoreToCount(save);
        stroke(blueDark); c.drawRoundRect(r, s*.17f, s*.17f, paint);
        c.drawLine(cx, r.top+s*.02f, cx, r.bottom-s*.02f, paint);
    }

    private void drawSoftgel(Canvas c, float cx, float cy, float s) {
        RectF r = new RectF(cx-s*.31f, cy-s*.16f, cx+s*.31f, cy+s*.16f);
        fill(Color.rgb(255, 236, 190)); c.drawOval(r, paint);
        stroke(amber); c.drawOval(r, paint);
        fill(Color.argb(145,255,255,255)); c.drawOval(new RectF(cx-s*.14f,cy-s*.10f,cx-s*.02f,cy-s*.02f),paint);
    }

    private void drawSachet(Canvas c, float cx, float cy, float s) {
        RectF r = new RectF(cx-s*.25f, cy-s*.31f, cx+s*.25f, cy+s*.31f);
        fill(Color.rgb(245,249,253)); c.drawRoundRect(r, s*.05f, s*.05f, paint);
        stroke(ink); c.drawRoundRect(r, s*.05f, s*.05f, paint);
        c.drawLine(r.left+s*.04f, r.top+s*.09f, r.right-s*.04f, r.top+s*.09f, paint);
        c.drawLine(r.left+s*.04f, r.bottom-s*.09f, r.right-s*.04f, r.bottom-s*.09f, paint);
        fill(blueSoft); c.drawCircle(cx, cy+s*.02f, s*.09f, paint);
        stroke(blue); c.drawCircle(cx, cy+s*.02f, s*.09f, paint);
    }

    private void drawLiquid(Canvas c, float cx, float cy, float s) {
        RectF body = new RectF(cx-s*.22f, cy-s*.17f, cx+s*.22f, cy+s*.30f);
        fill(Color.rgb(236,249,249)); c.drawRoundRect(body, s*.07f, s*.07f, paint);
        stroke(teal); c.drawRoundRect(body, s*.07f, s*.07f, paint);
        RectF neck = new RectF(cx-s*.11f, cy-s*.30f, cx+s*.11f, cy-s*.17f);
        fill(Color.WHITE); c.drawRect(neck, paint); stroke(teal); c.drawRect(neck, paint);
        c.drawLine(cx-s*.13f, cy-s*.30f, cx+s*.13f, cy-s*.30f, paint);
        fill(teal); c.drawRect(cx-s*.14f, cy+s*.10f, cx+s*.14f, cy+s*.17f, paint);
    }

    private void drawDrops(Canvas c, float cx, float cy, float s) {
        Path p = new Path();
        p.moveTo(cx, cy-s*.32f);
        p.cubicTo(cx-s*.05f, cy-s*.17f, cx-s*.23f, cy+s*.04f, cx-s*.23f, cy+s*.15f);
        p.cubicTo(cx-s*.23f, cy+s*.32f, cx-s*.10f, cy+s*.39f, cx, cy+s*.39f);
        p.cubicTo(cx+s*.10f, cy+s*.39f, cx+s*.23f, cy+s*.32f, cx+s*.23f, cy+s*.15f);
        p.cubicTo(cx+s*.23f, cy+s*.04f, cx+s*.05f, cy-s*.17f, cx, cy-s*.32f);
        p.close();
        fill(Color.rgb(225,245,255)); c.drawPath(p, paint); stroke(blue); c.drawPath(p, paint);
    }

    private void drawSupplement(Canvas c, float cx, float cy, float s) {
        fill(Color.rgb(233,250,242)); c.drawCircle(cx-s*.13f,cy+s*.06f,s*.16f,paint);
        fill(Color.rgb(255,241,209)); c.drawCircle(cx+s*.14f,cy-s*.08f,s*.14f,paint);
        stroke(teal); c.drawCircle(cx-s*.13f,cy+s*.06f,s*.16f,paint);
        stroke(amber); c.drawCircle(cx+s*.14f,cy-s*.08f,s*.14f,paint);
        stroke(teal); c.drawLine(cx-s*.13f,cy-s*.01f,cx-s*.13f,cy+s*.13f,paint); c.drawLine(cx-s*.20f,cy+s*.06f,cx-s*.06f,cy+s*.06f,paint);
    }

    private void fill(int color){ paint.setStyle(Paint.Style.FILL); paint.setColor(color); }
    private void stroke(int color){ paint.setStyle(Paint.Style.STROKE); paint.setColor(color); }
    private float dp(float v){ return v * getResources().getDisplayMetrics().density; }
}
'''

(java_dir / "MedicationIconStore.java").write_text(store_java, encoding="utf-8")
(java_dir / "MedicationIconView.java").write_text(view_java, encoding="utf-8")

main = main_file.read_text(encoding="utf-8")

# Draft icon state.
anchor = '    private Medicine draft;\n    private boolean draftIsNew;\n'
replace = '    private Medicine draft;\n    private boolean draftIsNew;\n    private String draftIconType = MedicationIconStore.CAPSULE;\n    private boolean draftIconManual = false;\n'
if anchor not in main: raise SystemExit("draft state anchor not found")
main = main.replace(anchor, replace, 1)

# Multi-medicine summary icon.
anchor = '            TextView name=text("💊  "+medicine.name,21,TEXT,true);\n            item.addView(name);\n'
replace = '''            LinearLayout titleRow=new LinearLayout(this);titleRow.setOrientation(LinearLayout.HORIZONTAL);titleRow.setGravity(Gravity.CENTER_VERTICAL);\n            MedicationIconView icon=new MedicationIconView(this,MedicationIconStore.get(this,medicine.id));\n            titleRow.addView(icon,new LinearLayout.LayoutParams(dp(38),dp(38)));\n            TextView name=text(medicine.name,21,TEXT,true);name.setPadding(dp(10),0,0,0);titleRow.addView(name);\n            item.addView(titleRow);\n'''
if anchor not in main: raise SystemExit("multi summary icon anchor not found")
main = main.replace(anchor, replace, 1)

# Single next-dose card icon.
anchor = '''        AlarmScheduler.DoseOccurrence occ=AlarmScheduler.findCurrentOrNextDose(this);\n        LinearLayout main=card();\n        TextView pill=text("💊",46,BLUE,false);pill.setGravity(Gravity.CENTER);main.addView(pill);\n        if(occ==null){TextView s=text(I18n.t(this,"no_scheduled_dose"),26,TEXT,true);s.setGravity(Gravity.CENTER);main.addView(s);content.addView(main,matchWrap(0,dp(12)));return;}\n        TextView med=text(occ.medicine.name,25,TEXT,true);med.setGravity(Gravity.CENTER);med.setPadding(0,0,0,dp(12));main.addView(med);\n'''
replace = '''        AlarmScheduler.DoseOccurrence occ=AlarmScheduler.findCurrentOrNextDose(this);\n        LinearLayout main=card();\n        if(occ==null){MedicationIconView emptyIcon=new MedicationIconView(this,MedicationIconStore.CAPSULE);LinearLayout.LayoutParams emptyIconLp=new LinearLayout.LayoutParams(dp(64),dp(64));emptyIconLp.gravity=Gravity.CENTER;main.addView(emptyIcon,emptyIconLp);TextView s=text(I18n.t(this,"no_scheduled_dose"),26,TEXT,true);s.setGravity(Gravity.CENTER);main.addView(s);content.addView(main,matchWrap(0,dp(12)));return;}\n        MedicationIconView pill=new MedicationIconView(this,MedicationIconStore.get(this,occ.medicine.id));LinearLayout.LayoutParams pillLp=new LinearLayout.LayoutParams(dp(68),dp(68));pillLp.gravity=Gravity.CENTER;main.addView(pill,pillLp);\n        TextView med=text(occ.medicine.name,25,TEXT,true);med.setGravity(Gravity.CENTER);med.setPadding(0,dp(8),0,dp(12));main.addView(med);\n'''
if anchor not in main: raise SystemExit("next dose icon anchor not found")
main = main.replace(anchor, replace, 1)

# Medicine card icon.
anchor = '        LinearLayout head=new LinearLayout(this);head.setOrientation(LinearLayout.HORIZONTAL);head.setGravity(Gravity.CENTER_VERTICAL);\n        TextView name=text(m.name,22,TEXT,true);head.addView(name,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));\n'
replace = '''        LinearLayout head=new LinearLayout(this);head.setOrientation(LinearLayout.HORIZONTAL);head.setGravity(Gravity.CENTER_VERTICAL);\n        MedicationIconView medIcon=new MedicationIconView(this,MedicationIconStore.get(this,m.id));head.addView(medIcon,new LinearLayout.LayoutParams(dp(42),dp(42)));\n        TextView name=text(m.name,22,TEXT,true);name.setPadding(dp(10),0,0,0);head.addView(name,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));\n'''
if anchor not in main: raise SystemExit("medicine card icon anchor not found")
main = main.replace(anchor, replace, 1)

# Settings list icon.
anchor = '            LinearLayout row=card();row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);TextView n=text(m.name,19,TEXT,true);row.addView(n,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));TextView v=text(I18n.t(this,"daily_n_times",m.times.size())+"  ›",16,MUTED,false);row.addView(v);row.setOnClickListener(x->startEditMedicine(m.id));content.addView(row,matchWrap(0,dp(8)));\n'
replace = '''            LinearLayout row=card();row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);MedicationIconView iv=new MedicationIconView(this,MedicationIconStore.get(this,m.id));row.addView(iv,new LinearLayout.LayoutParams(dp(42),dp(42)));TextView n=text(m.name,19,TEXT,true);n.setPadding(dp(10),0,0,0);row.addView(n,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));TextView v=text(I18n.t(this,"daily_n_times",m.times.size())+"  ›",16,MUTED,false);row.addView(v);row.setOnClickListener(x->startEditMedicine(m.id));content.addView(row,matchWrap(0,dp(8)));\n'''
if anchor not in main: raise SystemExit("settings icon anchor not found")
main = main.replace(anchor, replace, 1)

# New/edit draft initialization.
anchor = '        draft=new Medicine();draft.name=I18n.t(this,"medicine_name_hint");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;navigateTo("editor");\n'
replace = '        draft=new Medicine();draft.name=I18n.t(this,"medicine_name_hint");draft.alertMode="vibrate";draftIsNew=true;draftReceivedDate=LocalDate.now();draftInitialCount=28;draftIconType=MedicationIconStore.CAPSULE;draftIconManual=false;navigateTo("editor");\n'
if anchor not in main: raise SystemExit("start new anchor not found")
main = main.replace(anchor, replace, 1)

anchor = '    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;navigateTo("editor");}\n'
replace = '    private void startEditMedicine(String id){Medicine m=MedicationStore.getMedicine(this,id);if(m==null)return;draft=m.copy();draftIsNew=false;draftIconType=MedicationIconStore.get(this,id);draftIconManual=true;navigateTo("editor");}\n'
if anchor not in main: raise SystemExit("start edit anchor not found")
main = main.replace(anchor, replace, 1)

# Editor icon selector row.
anchor = '        addSettingRow(g,"💊",I18n.t(this,"medicine_name"),draft.name,v->editDraftName());\n'
replace = '        addMedicationIconSettingRow(g);\n        addSettingRow(g,"Aa",I18n.t(this,"medicine_name"),draft.name,v->editDraftName());\n'
if anchor not in main: raise SystemExit("editor icon row anchor not found")
main = main.replace(anchor, replace, 1)

# Save/delete icon selection.
anchor = '        if(draftIsNew){draft.inventory=0;draft.stockInitialized=false;MedicationStore.addMedicine(this,draft);if(draftInitialCount>0)MedicationStore.addStock(this,draft.id,draftReceivedDate,draftInitialCount);'
replace = '        if(draftIsNew){draft.inventory=0;draft.stockInitialized=false;MedicationStore.addMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);if(draftInitialCount>0)MedicationStore.addStock(this,draft.id,draftReceivedDate,draftInitialCount);'
if anchor not in main: raise SystemExit("new save icon anchor not found")
main = main.replace(anchor, replace, 1)

anchor = '        else {Medicine old=MedicationStore.getMedicine(this,draft.id);if(old!=null)AlarmScheduler.cancelMedicine(this,old);MedicationStore.updateMedicine(this,draft);'
replace = '        else {Medicine old=MedicationStore.getMedicine(this,draft.id);if(old!=null)AlarmScheduler.cancelMedicine(this,old);MedicationStore.updateMedicine(this,draft);MedicationIconStore.set(this,draft.id,draftIconType);'
if anchor not in main: raise SystemExit("edit save icon anchor not found")
main = main.replace(anchor, replace, 1)

anchor = 'MedicationStore.deleteMedicine(this,draft.id);goHomeAndClearHistory();}).show();}'
replace = 'MedicationStore.deleteMedicine(this,draft.id);MedicationIconStore.delete(this,draft.id);goHomeAndClearHistory();}).show();}'
if anchor not in main: raise SystemExit("delete icon anchor not found")
main = main.replace(anchor, replace, 1)

# Name editing keeps automatic icon guessing until the user explicitly chooses a shape.
anchor = '    private void editDraftName(){EditText e=new EditText(this);e.setText(draft.name);e.setSelectAllOnFocus(true);new AlertDialog.Builder(this).setTitle(I18n.t(this,"medicine_name")).setView(e).setNegativeButton(I18n.t(this,"cancel"),null).setPositiveButton(I18n.t(this,"save").replace("✓  ",""),(d,w)->{String x=e.getText().toString().trim();if(!x.isEmpty())draft.name=x;showMedicineEditor();}).show();}\n'
replace = '    private void editDraftName(){EditText e=new EditText(this);e.setText(draft.name);e.setSelectAllOnFocus(true);new AlertDialog.Builder(this).setTitle(I18n.t(this,"medicine_name")).setView(e).setNegativeButton(I18n.t(this,"cancel"),null).setPositiveButton(I18n.t(this,"save").replace("✓  ",""),(d,w)->{String x=e.getText().toString().trim();if(!x.isEmpty()){draft.name=x;if(!draftIconManual)draftIconType=MedicationIconStore.guessFromName(x);}showMedicineEditor();}).show();}\n'
if anchor not in main: raise SystemExit("edit name icon guess anchor not found")
main = main.replace(anchor, replace, 1)

# Add editor row and visual picker helpers before commitMedicine.
anchor = '    private void commitMedicine(){\n'
helpers = r'''    private void addMedicationIconSettingRow(LinearLayout group){
        LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);row.setGravity(Gravity.CENTER_VERTICAL);row.setPadding(dp(12),dp(8),dp(8),dp(8));
        MedicationIconView icon=new MedicationIconView(this,draftIconType);row.addView(icon,new LinearLayout.LayoutParams(dp(50),dp(50)));
        LinearLayout labels=new LinearLayout(this);labels.setOrientation(LinearLayout.VERTICAL);labels.setPadding(dp(12),0,0,0);
        labels.addView(text(I18n.t(this,"medicine_icon"),17,TEXT,true));
        labels.addView(text(I18n.t(this,MedicationIconStore.labelKey(draftIconType)),14,MUTED,false));
        row.addView(labels,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        row.addView(text("›",22,MUTED,false));row.setOnClickListener(v->editDraftIcon());
        group.addView(row,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(72)));
    }

    private void editDraftIcon(){
        String[] types=MedicationIconStore.types();
        android.widget.GridLayout grid=new android.widget.GridLayout(this);grid.setColumnCount(2);grid.setPadding(dp(12),dp(6),dp(12),dp(6));
        final AlertDialog[] holder=new AlertDialog[1];
        for(String type:types){
            LinearLayout cell=new LinearLayout(this);cell.setOrientation(LinearLayout.HORIZONTAL);cell.setGravity(Gravity.CENTER_VERTICAL);cell.setPadding(dp(10),dp(10),dp(10),dp(10));
            boolean selected=type.equals(draftIconType);cell.setBackground(round(selected?SOFT_BLUE:Color.WHITE,16,selected?BLUE:CARD_BORDER,1));
            MedicationIconView icon=new MedicationIconView(this,type);cell.addView(icon,new LinearLayout.LayoutParams(dp(48),dp(48)));
            TextView label=text(I18n.t(this,MedicationIconStore.labelKey(type)),14,selected?BLUE_DARK:TEXT,selected);label.setPadding(dp(8),0,0,0);cell.addView(label,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
            android.widget.GridLayout.LayoutParams lp=new android.widget.GridLayout.LayoutParams();lp.width=0;lp.height=dp(70);lp.columnSpec=android.widget.GridLayout.spec(android.widget.GridLayout.UNDEFINED,1f);lp.setMargins(dp(4),dp(4),dp(4),dp(4));grid.addView(cell,lp);
            cell.setOnClickListener(v->{draftIconType=type;draftIconManual=true;if(holder[0]!=null)holder[0].dismiss();showMedicineEditor();});
        }
        holder[0]=new AlertDialog.Builder(this).setTitle(I18n.t(this,"medicine_icon")).setView(grid).setNegativeButton(I18n.t(this,"cancel"),null).create();
        holder[0].show();
    }

'''
if anchor not in main: raise SystemExit("commit helper insertion anchor not found")
main = main.replace(anchor, helpers + anchor, 1)

main_file.write_text(main, encoding="utf-8")

# Full-screen alarm uses the selected icon.
full = full_file.read_text(encoding="utf-8")
anchor = '        TextView pill=text("💊",58,BLUE,true);pill.setGravity(Gravity.CENTER);card.addView(pill);\n'
replace = '        MedicationIconView pill=new MedicationIconView(this,MedicationIconStore.get(this,m.id));LinearLayout.LayoutParams pillLp=new LinearLayout.LayoutParams(dp(92),dp(92));pillLp.gravity=Gravity.CENTER;card.addView(pill,pillLp);\n'
if anchor not in full: raise SystemExit("full screen icon anchor not found")
full = full.replace(anchor, replace, 1)
full_file.write_text(full, encoding="utf-8")

# Six-language labels.
i18n = i18n_file.read_text(encoding="utf-8")
anchor = '        M.put("medicine_name",new String[]{"이름","Name","名前","名称","नाम","Nombre"});\n'
labels = '''        M.put("medicine_name",new String[]{"이름","Name","名前","名称","नाम","Nombre"});\n        M.put("medicine_icon",new String[]{"약·영양제 모양","Medication / supplement shape","薬・サプリの形","药物/保健品外形","दवा / सप्लीमेंट का आकार","Forma del medicamento / suplemento"});\n        M.put("icon_round_tablet",new String[]{"원형 알약","Round tablet","丸い錠剤","圆形药片","गोल टैबलेट","Comprimido redondo"});\n        M.put("icon_oval_tablet",new String[]{"타원형 알약","Oval tablet","楕円形の錠剤","椭圆形药片","अंडाकार टैबलेट","Comprimido ovalado"});\n        M.put("icon_capsule",new String[]{"캡슐","Capsule","カプセル","胶囊","कैप्सूल","Cápsula"});\n        M.put("icon_softgel",new String[]{"연질캡슐","Softgel","ソフトカプセル","软胶囊","सॉफ्टजेल","Cápsula blanda"});\n        M.put("icon_sachet",new String[]{"가루약·포","Powder / sachet","粉薬・分包","粉剂/袋装","पाउडर / सैशे","Polvo / sobre"});\n        M.put("icon_liquid",new String[]{"액상약","Liquid medicine","液体薬","液体药","तरल दवा","Medicamento líquido"});\n        M.put("icon_drops",new String[]{"점적제","Drops","点眼・滴下薬","滴剂","ड्रॉप्स","Gotas"});\n        M.put("icon_supplement",new String[]{"영양제","Supplement","サプリメント","保健品","सप्लीमेंट","Suplemento"});\n'''
if anchor not in i18n: raise SystemExit("I18n medicine name anchor not found")
i18n = i18n.replace(anchor, labels, 1)
i18n_file.write_text(i18n, encoding="utf-8")

# v3.0.6 / production code 38; closed-test gets 39 in workflow.
build = build_file.read_text(encoding="utf-8")
if "versionCode 36" not in build or "versionName '3.0.5'" not in build:
    raise SystemExit("Expected v3.0.5 version anchors not found")
build = build.replace("versionCode 36", "versionCode 38", 1)
build = build.replace("versionName '3.0.5'", "versionName '3.0.6'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.6 selectable medication icon patch applied")
