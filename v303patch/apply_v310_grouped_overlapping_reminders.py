from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("yak_alimi_v21_work")
java_dir = root / "app/src/main/java/com/yakalimi/app"
scheduler_file = java_dir / "AlarmScheduler.java"
receiver_file = java_dir / "AlarmReceiver.java"
notification_file = java_dir / "NotificationHelper.java"
fullscreen_file = java_dir / "FullScreenAlarmActivity.java"
i18n_file = java_dir / "I18n.java"
build_file = root / "app/build.gradle"

# -----------------------------------------------------------------------------
# AlarmScheduler: carry the intended trigger time and resolve all doses whose
# primary/repeat schedule lands on that exact minute.
# -----------------------------------------------------------------------------
s = scheduler_file.read_text(encoding="utf-8")
if "import java.time.Instant;" not in s:
    s = s.replace("import java.time.Duration;\n", "import java.time.Duration;\nimport java.time.Instant;\n", 1)
if "import java.util.ArrayList;" not in s:
    s = s.replace("import java.util.List;\n", "import java.util.ArrayList;\nimport java.util.List;\n", 1)

anchor = '''    public static class DoseOccurrence {
        public final Medicine medicine;
        public final String slot;
        public final LocalDateTime when;
        public final boolean overdue;
        DoseOccurrence(Medicine medicine, String slot, LocalDateTime when, boolean overdue) {
            this.medicine = medicine; this.slot = slot; this.when = when; this.overdue = overdue;
        }
    }
'''
insert = anchor + '''
    public static class DueDose {
        public final Medicine medicine;
        public final String slot;
        public final boolean secondary;
        public final int repeatIndex;
        public DueDose(Medicine medicine, String slot, boolean secondary, int repeatIndex) {
            this.medicine = medicine;
            this.slot = slot;
            this.secondary = secondary;
            this.repeatIndex = repeatIndex;
        }
    }
'''
if anchor not in s:
    raise SystemExit("DoseOccurrence anchor not found")
s = s.replace(anchor, insert, 1)

old = '''        PendingIntent pi = pending(c, req, medId, slot, secondary, repeatIndex);
'''
new = '''        PendingIntent pi = pending(c, req, medId, slot, secondary, repeatIndex, millis);
'''
if old not in s:
    raise SystemExit("schedule pending anchor not found")
s = s.replace(old, new, 1)

old = '''    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary, int repeatIndex) {
        Intent i = new Intent(c, AlarmReceiver.class)
                .putExtra("med_id", medId)
                .putExtra("slot", slot)
                .putExtra("secondary", secondary)
                .putExtra("repeat_index", repeatIndex);
        return PendingIntent.getBroadcast(c, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
'''
new = '''    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary, int repeatIndex) {
        return pending(c, req, medId, slot, secondary, repeatIndex, 0L);
    }

    private static PendingIntent pending(Context c, int req, String medId, String slot, boolean secondary, int repeatIndex, long scheduledAt) {
        Intent i = new Intent(c, AlarmReceiver.class)
                .putExtra("med_id", medId)
                .putExtra("slot", slot)
                .putExtra("secondary", secondary)
                .putExtra("repeat_index", repeatIndex)
                .putExtra("scheduled_at", scheduledAt);
        return PendingIntent.getBroadcast(c, req, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }
'''
if old not in s:
    raise SystemExit("pending overload anchor not found")
s = s.replace(old, new, 1)

anchor = '''    public static DoseOccurrence findCurrentOrNextDose(Context c) {
'''
method = '''    public static List<DueDose> findDueAt(Context c, long scheduledAt) {
        List<DueDose> out = new ArrayList<>();
        if (scheduledAt <= 0L) return out;
        LocalDateTime target = Instant.ofEpochMilli(scheduledAt)
                .atZone(ZoneId.systemDefault()).toLocalDateTime()
                .withSecond(0).withNano(0);
        LocalDate date = target.toLocalDate();
        for (Medicine m : MedicationStore.getMedicines(c)) {
            if (!MedicationStore.isDayEnabled(m, date)) continue;
            for (String slot : m.times) {
                if (MedicationStore.isTaken(c, m.id, date, slot)) continue;
                LocalDateTime primary = date.atTime(LocalTime.parse(slot));
                if (target.equals(primary)) {
                    out.add(new DueDose(m, slot, false, 0));
                    continue;
                }
                if (!target.isAfter(primary)) continue;
                int interval = Math.max(5, MedicationStore.snoozeMinutes(c, m.id));
                long delta = Duration.between(primary, target).toMinutes();
                if (delta > 0L && delta % interval == 0L) {
                    out.add(new DueDose(m, slot, true, (int)(delta / interval)));
                }
            }
        }
        return out;
    }

'''
if anchor not in s:
    raise SystemExit("findCurrentOrNextDose anchor not found")
s = s.replace(anchor, method + anchor, 1)
scheduler_file.write_text(s, encoding="utf-8")

# -----------------------------------------------------------------------------
# AlarmReceiver: the first broadcast for a minute claims the whole minute,
# resolves every overlapping primary/repeat dose, shows one alert, and advances
# each dose's own repeat schedule independently.
# -----------------------------------------------------------------------------
receiver = '''package com.yakalimi.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.List;

public class AlarmReceiver extends BroadcastReceiver {
    private static final String GROUP_CLAIMS = "alarm_group_claims_v1";

    @Override public void onReceive(Context context, Intent intent) {
        String medId = intent.getStringExtra("med_id");
        String slot = intent.getStringExtra("slot");
        boolean secondary = intent.getBooleanExtra("secondary", false);
        Medicine triggerMedicine = MedicationStore.getMedicine(context, medId);
        if (triggerMedicine == null || slot == null || !triggerMedicine.times.contains(slot)) return;

        long scheduledAt = intent.getLongExtra("scheduled_at", 0L);
        if (scheduledAt <= 0L) scheduledAt = fallbackScheduledAt(slot, secondary);

        List<AlarmScheduler.DueDose> due = AlarmScheduler.findDueAt(context, scheduledAt);
        if (due.isEmpty()) {
            if (!secondary) AlarmScheduler.scheduleNextPrimary(context, triggerMedicine, slot);
            return;
        }
        if (!claimGroup(context, scheduledAt)) return;

        NotificationHelper.showDoseGroup(context, due, scheduledAt);
        for (AlarmScheduler.DueDose d : due) {
            if (!d.secondary) AlarmScheduler.scheduleNextPrimary(context, d.medicine, d.slot);
            AlarmScheduler.scheduleNextSecondaryAligned(context, d.medicine.id, d.slot);
        }
    }

    private static long fallbackScheduledAt(String slot, boolean secondary) {
        LocalDateTime t;
        if (!secondary) t = LocalDate.now().atTime(LocalTime.parse(slot));
        else t = LocalDateTime.now().withSecond(0).withNano(0);
        return t.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli();
    }

    private static synchronized boolean claimGroup(Context context, long scheduledAt) {
        long minute = scheduledAt / 60000L;
        SharedPreferences sp = context.getSharedPreferences(GROUP_CLAIMS, Context.MODE_PRIVATE);
        String key = "m_" + minute;
        if (sp.getBoolean(key, false)) return false;
        SharedPreferences.Editor e = sp.edit().putBoolean(key, true);
        long cutoff = minute - (3L * 24L * 60L);
        for (String k : sp.getAll().keySet()) {
            if (!k.startsWith("m_")) continue;
            try {
                if (Long.parseLong(k.substring(2)) < cutoff) e.remove(k);
            } catch (Exception ignored) {}
        }
        e.apply();
        return true;
    }
}
'''
receiver_file.write_text(receiver, encoding="utf-8")

# -----------------------------------------------------------------------------
# NotificationHelper: overlapping reminders use one summary notification whose
# full-screen/content intent opens the combined per-dose control screen.
# -----------------------------------------------------------------------------
n = notification_file.read_text(encoding="utf-8")
if "import java.util.List;" not in n:
    n = n.replace("import android.os.Build;\n", "import android.os.Build;\n\nimport java.util.List;\n", 1)

# Let the rewritten activity know whether a legacy/single alert is a repeat.
old = '''        Intent full = new Intent(c, FullScreenAlarmActivity.class)
                .putExtra("med_id", m.id).putExtra("slot", slot)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
'''
new = '''        Intent full = new Intent(c, FullScreenAlarmActivity.class)
                .putExtra("med_id", m.id).putExtra("slot", slot)
                .putExtra("secondary", second).putExtra("repeat_index", repeatIndex)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
'''
if old not in n:
    raise SystemExit("single full-screen intent anchor not found")
n = n.replace(old, new, 1)

anchor = '''    public static void showLowStock(Context c, Medicine m) {
'''
group_methods = '''    private static final int GROUP_NOTIFICATION_ID = 390001;

    private static String channelForGroup(List<AlarmScheduler.DueDose> doses) {
        boolean vibrate = false;
        for (AlarmScheduler.DueDose d : doses) {
            if (d != null && d.medicine != null && "sound".equals(d.medicine.alertMode)) return CHANNEL_SOUND;
            if (d != null && d.medicine != null && "vibrate".equals(d.medicine.alertMode)) vibrate = true;
        }
        return vibrate ? CHANNEL_VIBRATE : CHANNEL_SILENT;
    }

    public static void showDoseGroup(Context c, List<AlarmScheduler.DueDose> doses, long scheduledAt) {
        if (doses == null || doses.isEmpty()) return;
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        nm.cancel(GROUP_NOTIFICATION_ID);
        if (doses.size() == 1) {
            AlarmScheduler.DueDose d = doses.get(0);
            showDose(c, d.medicine, d.slot, d.secondary, d.repeatIndex);
            return;
        }

        ensureChannels(c);
        if (Build.VERSION.SDK_INT >= 33 && c.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return;
        for (AlarmScheduler.DueDose d : doses) cancelDose(c, d.medicine.id, d.slot);

        Intent full = new Intent(c, FullScreenAlarmActivity.class)
                .putExtra("group_time", scheduledAt)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        int req = 940000 + (int)Math.abs((scheduledAt / 60000L) % 50000L);
        PendingIntent fullPi = PendingIntent.getActivity(c, req, full, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        String channel = channelForGroup(doses);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(c, channel)
                : new Notification.Builder(c);
        b.setSmallIcon(R.drawable.ic_notification)
                .setContentTitle(I18n.t(c,"group_notification_title"))
                .setContentText(I18n.t(c,"group_notification_text"))
                .setContentIntent(fullPi)
                .setFullScreenIntent(fullPi, true)
                .setVisibility(Notification.VISIBILITY_PUBLIC)
                .setCategory(Notification.CATEGORY_ALARM)
                .setPriority(Notification.PRIORITY_MAX)
                .setOngoing(true)
                .setAutoCancel(false);

        if (Build.VERSION.SDK_INT < 26) {
            if (CHANNEL_SOUND.equals(channel)) {
                b.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM));
                b.setVibrate(new long[]{0,500,350,500});
            } else if (CHANNEL_VIBRATE.equals(channel)) {
                b.setSound(null);
                b.setVibrate(new long[]{0,700,450,700});
            } else {
                b.setSound(null);
                b.setVibrate(new long[]{0});
            }
        }
        nm.notify(GROUP_NOTIFICATION_ID, b.build());
    }

    public static void cancelGroup(Context c, long scheduledAt) {
        c.getSystemService(NotificationManager.class).cancel(GROUP_NOTIFICATION_ID);
    }

'''
if anchor not in n:
    raise SystemExit("showLowStock anchor not found")
n = n.replace(anchor, group_methods + anchor, 1)
notification_file.write_text(n, encoding="utf-8")

# -----------------------------------------------------------------------------
# FullScreenAlarmActivity: a grouped alert shows one card per due dose. Each
# card has its own Later and Taken buttons. Later dismisses only that row for the
# current screen; its independently scheduled next repeat remains intact.
# -----------------------------------------------------------------------------
fullscreen = r'''package com.yakalimi.app;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.media.AudioAttributes;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.Gravity;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

public class FullScreenAlarmActivity extends Activity {
    private static final int BLUE=Color.rgb(23,105,232), TEXT=Color.rgb(17,24,39), MUTED=Color.rgb(104,115,134);
    private Ringtone ringtone;
    private Vibrator vibrator;
    private final List<AlarmScheduler.DueDose> visibleDoses = new ArrayList<>();
    private long groupTime = 0L;

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        if(Build.VERSION.SDK_INT>=27){setShowWhenLocked(true);setTurnScreenOn(true);}
        else getWindow().addFlags(WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED|WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        loadIntentAndRender();
    }

    @Override protected void onNewIntent(android.content.Intent intent){
        super.onNewIntent(intent);
        stopAlert();
        setIntent(intent);
        loadIntentAndRender();
    }

    private void loadIntentAndRender(){
        visibleDoses.clear();
        groupTime=getIntent().getLongExtra("group_time",0L);
        if(groupTime>0L){
            visibleDoses.addAll(AlarmScheduler.findDueAt(this,groupTime));
        }else{
            String medId=getIntent().getStringExtra("med_id");
            String slot=getIntent().getStringExtra("slot");
            Medicine m=MedicationStore.getMedicine(this,medId);
            if(m!=null&&slot!=null&&!MedicationStore.isTaken(this,medId,LocalDate.now(),slot)){
                visibleDoses.add(new AlarmScheduler.DueDose(m,slot,getIntent().getBooleanExtra("secondary",false),getIntent().getIntExtra("repeat_index",0)));
            }
        }
        if(visibleDoses.isEmpty()){
            if(groupTime>0L)NotificationHelper.cancelGroup(this,groupTime);
            finishAndRemoveTask();
            return;
        }
        buildUi();
        restartAlert();
    }

    private void buildUi(){
        if(visibleDoses.size()==1) buildSingleUi(visibleDoses.get(0));
        else buildGroupUi();
    }

    private void buildSingleUi(AlarmScheduler.DueDose d){
        LinearLayout root=baseRoot();
        LinearLayout card=new LinearLayout(this);card.setOrientation(LinearLayout.VERTICAL);card.setGravity(Gravity.CENTER);card.setPadding(dp(24),dp(30),dp(24),dp(26));card.setBackground(round(Color.WHITE,28,Color.rgb(225,232,242),1));
        MedicationIconView pill=new MedicationIconView(this,MedicationIconStore.get(this,d.medicine.id));LinearLayout.LayoutParams pillLp=new LinearLayout.LayoutParams(dp(92),dp(92));pillLp.gravity=Gravity.CENTER;card.addView(pill,pillLp);
        TextView label=text(I18n.t(this,"dose_time"),20,MUTED,false);label.setGravity(Gravity.CENTER);label.setPadding(0,dp(12),0,dp(8));card.addView(label);
        TextView name=text(d.medicine.name,34,TEXT,true);name.setGravity(Gravity.CENTER);card.addView(name);
        TextView time=text(TimeUtil.time(this,d.slot),28,BLUE,true);time.setGravity(Gravity.CENTER);time.setPadding(0,dp(12),0,dp(6));card.addView(time);
        TextView mode=text(I18n.modeLabel(this,d.medicine.alertMode),15,MUTED,false);mode.setGravity(Gravity.CENTER);mode.setPadding(0,0,0,dp(20));card.addView(mode);
        Button done=button(I18n.t(this,"done"),BLUE,Color.WHITE);done.setOnClickListener(v->markDone(d));card.addView(done,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(64)));
        Button later=button(I18n.t(this,"later"),Color.WHITE,TEXT);later.setBackground(round(Color.WHITE,24,Color.rgb(220,227,237),1));LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(58));lp.topMargin=dp(12);card.addView(later,lp);later.setOnClickListener(v->later(d));
        TextView hint=text(I18n.t(this,"later_hint"),15,MUTED,false);hint.setGravity(Gravity.CENTER);hint.setPadding(0,dp(18),0,0);card.addView(hint);
        root.addView(card,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        setContentView(root);
    }

    private void buildGroupUi(){
        LinearLayout root=baseRoot();
        root.setGravity(Gravity.TOP|Gravity.CENTER_HORIZONTAL);
        TextView title=text(I18n.t(this,"group_screen_title",visibleDoses.size()),30,TEXT,true);title.setGravity(Gravity.CENTER);title.setPadding(0,dp(6),0,dp(6));root.addView(title);
        TextView sub=text(I18n.t(this,"group_screen_sub"),16,MUTED,false);sub.setGravity(Gravity.CENTER);sub.setPadding(dp(8),0,dp(8),dp(16));root.addView(sub);

        ScrollView scroll=new ScrollView(this);
        LinearLayout list=new LinearLayout(this);list.setOrientation(LinearLayout.VERTICAL);
        for(AlarmScheduler.DueDose d:new ArrayList<>(visibleDoses)) list.addView(groupDoseCard(d),new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        scroll.addView(list,new ScrollView.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,0,1));
        setContentView(root);
    }

    private LinearLayout groupDoseCard(AlarmScheduler.DueDose d){
        LinearLayout card=new LinearLayout(this);card.setOrientation(LinearLayout.VERTICAL);card.setPadding(dp(18),dp(18),dp(18),dp(18));card.setBackground(round(Color.WHITE,24,Color.rgb(225,232,242),1));
        LinearLayout head=new LinearLayout(this);head.setOrientation(LinearLayout.HORIZONTAL);head.setGravity(Gravity.CENTER_VERTICAL);
        MedicationIconView icon=new MedicationIconView(this,MedicationIconStore.get(this,d.medicine.id));head.addView(icon,new LinearLayout.LayoutParams(dp(58),dp(58)));
        LinearLayout labels=new LinearLayout(this);labels.setOrientation(LinearLayout.VERTICAL);labels.setPadding(dp(12),0,0,0);
        labels.addView(text(d.medicine.name,23,TEXT,true));
        labels.addView(text(TimeUtil.time(this,d.slot)+" · "+I18n.modeLabel(this,d.medicine.alertMode),15,MUTED,false));
        head.addView(labels,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));card.addView(head);

        LinearLayout buttons=new LinearLayout(this);buttons.setOrientation(LinearLayout.HORIZONTAL);buttons.setPadding(0,dp(14),0,0);
        Button later=button(I18n.t(this,"later"),Color.WHITE,TEXT);later.setTextSize(17);later.setBackground(round(Color.WHITE,20,Color.rgb(220,227,237),1));later.setOnClickListener(v->later(d));
        Button done=button(I18n.t(this,"done"),BLUE,Color.WHITE);done.setTextSize(17);done.setOnClickListener(v->markDone(d));
        buttons.addView(later,new LinearLayout.LayoutParams(0,dp(54),1));LinearLayout.LayoutParams dp2=new LinearLayout.LayoutParams(0,dp(54),1);dp2.leftMargin=dp(8);buttons.addView(done,dp2);card.addView(buttons);
        LinearLayout.LayoutParams outer=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);outer.bottomMargin=dp(10);card.setLayoutParams(outer);
        return card;
    }

    private LinearLayout baseRoot(){
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setGravity(Gravity.CENTER);root.setPadding(dp(24),dp(40),dp(24),dp(40));root.setBackgroundColor(Color.rgb(250,251,253));
        root.setOnApplyWindowInsetsListener((v,insets)->{int top=0,bottom=0,left=0,right=0;if(Build.VERSION.SDK_INT>=30){android.graphics.Insets i=insets.getInsets(android.view.WindowInsets.Type.systemBars());top=i.top;bottom=i.bottom;left=i.left;right=i.right;}else{top=insets.getSystemWindowInsetTop();bottom=insets.getSystemWindowInsetBottom();left=insets.getSystemWindowInsetLeft();right=insets.getSystemWindowInsetRight();}v.setPadding(dp(24)+left,dp(24)+top,dp(24)+right,dp(24)+bottom);return insets;});
        return root;
    }

    private void markDone(AlarmScheduler.DueDose d){
        boolean added=MedicationStore.markTaken(this,d.medicine.id,LocalDate.now(),d.slot,LocalTime.now());
        AlarmScheduler.cancelSecondary(this,d.medicine.id,d.slot);NotificationHelper.cancelDose(this,d.medicine.id,d.slot);ActionReceiver.maybeWarnLowStock(this,d.medicine.id);
        Toast.makeText(this,added?I18n.t(this,"recorded"):I18n.t(this,"already_recorded"),Toast.LENGTH_SHORT).show();
        removeVisible(d);
    }

    private void later(AlarmScheduler.DueDose d){
        removeVisible(d);
    }

    private void removeVisible(AlarmScheduler.DueDose target){
        for(int i=visibleDoses.size()-1;i>=0;i--){AlarmScheduler.DueDose d=visibleDoses.get(i);if(d.medicine.id.equals(target.medicine.id)&&d.slot.equals(target.slot))visibleDoses.remove(i);}
        if(visibleDoses.isEmpty()){finishInteraction();return;}
        buildUi();
        restartAlert();
    }

    private void finishInteraction(){
        if(groupTime>0L&&AlarmScheduler.findDueAt(this,groupTime).isEmpty())NotificationHelper.cancelGroup(this,groupTime);
        stopAlert();
        finishAndRemoveTask();
    }

    private void restartAlert(){stopAlert();startAlert();}

    private void startAlert(){
        boolean sound=false,vibrateMode=false;
        for(AlarmScheduler.DueDose d:visibleDoses){if("sound".equals(d.medicine.alertMode))sound=true;else if("vibrate".equals(d.medicine.alertMode))vibrateMode=true;}
        if(sound){
            try{ringtone=RingtoneManager.getRingtone(this,RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM));if(ringtone!=null){if(Build.VERSION.SDK_INT>=28)ringtone.setLooping(true);ringtone.setAudioAttributes(new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_ALARM).build());ringtone.play();}}catch(Exception ignored){}
        }else if(vibrateMode)startVibration();
    }

    private void startVibration(){
        try{vibrator=(Vibrator)getSystemService(VIBRATOR_SERVICE);if(vibrator!=null&&vibrator.hasVibrator())vibrator.vibrate(VibrationEffect.createWaveform(new long[]{0,700,450,700,450},0));}catch(Exception ignored){}
    }

    private void stopAlert(){
        try{if(ringtone!=null&&ringtone.isPlaying())ringtone.stop();}catch(Exception ignored){}
        ringtone=null;
        try{if(vibrator!=null)vibrator.cancel();}catch(Exception ignored){}
        vibrator=null;
    }
    @Override protected void onDestroy(){stopAlert();super.onDestroy();}

    private TextView text(String s,float sp,int color,boolean bold){TextView t=new TextView(this);t.setText(s);t.setTextSize(sp);t.setTextColor(color);if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);return t;}
    private Button button(String s,int bg,int fg){Button b=new Button(this);b.setText(s);b.setTextSize(21);b.setTextColor(fg);b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);b.setAllCaps(false);b.setBackground(round(bg,24,0,0));return b;}
    private GradientDrawable round(int color,int radius,int stroke,int sw){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));if(sw>0)g.setStroke(dp(sw),stroke);return g;}
    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
}
'''
fullscreen_file.write_text(fullscreen, encoding="utf-8")

# -----------------------------------------------------------------------------
# Localized copy for the combined alert.
# -----------------------------------------------------------------------------
i18n = i18n_file.read_text(encoding="utf-8")
needle = '        M.put("dose_time",'
pos = i18n.find(needle)
if pos < 0:
    raise SystemExit("dose_time I18n anchor not found")
end = i18n.find("\n", pos)
if end < 0:
    raise SystemExit("dose_time I18n line end not found")
new_lines = '''        M.put("group_notification_title",new String[]{"약·영양제 복용 알림","Medication & supplement reminder","薬・サプリメントの服用通知","药物和保健品服用提醒","दवा और सप्लीमेंट रिमाइंडर","Recordatorio de medicamentos y suplementos"});
        M.put("group_notification_text",new String[]{"같은 시간에 복용할 항목이 여러 개 있어요. 눌러서 확인하세요.","Several items are due at the same time. Tap to review them.","同じ時刻に服用する項目が複数あります。タップして確認してください。","有多个项目需要在同一时间服用。点按查看。","एक ही समय पर कई चीज़ें लेनी हैं। देखने के लिए टैप करें।","Hay varios elementos que debes tomar a la misma hora. Toca para revisarlos."});
        M.put("group_screen_title",new String[]{"지금 복용할 항목 %d개","%d items to take now","今服用する項目 %d件","现在需服用 %d 项","अभी लेने के लिए %d आइटम","%d elementos para tomar ahora"});
        M.put("group_screen_sub",new String[]{"각 항목에서 먹었어요 또는 나중에를 선택하세요.","Choose Taken or Later for each item.","各項目で「服用した」または「あとで」を選んでください。","请为每个项目选择“已服用”或“稍后”。","हर आइटम के लिए लिया या बाद में चुनें।","Elige Tomado o Más tarde para cada elemento."});
'''
i18n = i18n[:end+1] + new_lines + i18n[end+1:]
i18n_file.write_text(i18n, encoding="utf-8")

# Version bump: production 46; closed-test workflow will use 47.
build = build_file.read_text(encoding="utf-8")
if "versionCode 44" not in build or "versionName '3.0.9'" not in build:
    raise SystemExit("Expected v3.0.9 version anchors not found")
build = build.replace("versionCode 44", "versionCode 46", 1)
build = build.replace("versionName '3.0.9'", "versionName '3.0.10'", 1)
build_file.write_text(build, encoding="utf-8")

print("V3.0.10 grouped overlapping reminders patch applied")
