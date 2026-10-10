from pathlib import Path

root=Path("yak_alimi_v21_work")
main_file=root/"app/src/main/java/com/yakalimi/app/MainActivity.java"
i18n_file=root/"app/src/main/java/com/yakalimi/app/I18n.java"

s=main_file.read_text(encoding="utf-8")

# Remember the day whose records are being edited below the calendar.
field_anchor='''    private java.time.YearMonth historyMonth = java.time.YearMonth.now();
    private Medicine draft;'''
field_repl='''    private java.time.YearMonth historyMonth = java.time.YearMonth.now();
    private LocalDate historySelectedDate = LocalDate.now();
    private Medicine draft;'''
if field_anchor not in s:
    raise SystemExit("history selected-date field anchor missing")
s=s.replace(field_anchor,field_repl,1)

# Today button should also select today for the quick editor.
old_today='''        Button todayButton=smallButton(I18n.t(this,"today"));
        todayButton.setOnClickListener(v->{historyMonth=java.time.YearMonth.now();showHistory();});
        calendar.addView(todayButton,matchWrap(dp(12),0));
        content.addView(calendar,matchWrap(0,dp(12)));
    }
'''
new_today='''        Button todayButton=smallButton(I18n.t(this,"today"));
        todayButton.setOnClickListener(v->{
            historyMonth=java.time.YearMonth.now();
            historySelectedDate=LocalDate.now();
            showHistory();
        });
        calendar.addView(todayButton,matchWrap(dp(12),0));
        content.addView(calendar,matchWrap(0,dp(12)));

        if(historySelectedDate==null) historySelectedDate=LocalDate.now();
        addHistoryRecordEditor(meds,historySelectedDate);
    }
'''
if old_today not in s:
    raise SystemExit("history today/content anchor missing")
s=s.replace(old_today,new_today,1)

# Selected date gets its own highlight; today remains subtly marked when it is not selected.
old_cell_bg='''        boolean today=date.equals(LocalDate.now());
        if(today) cell.setBackground(round(SOFT_BLUE,15,BLUE,1));

        TextView day=text(String.valueOf(date.getDayOfMonth()),15,today?BLUE_DARK:TEXT,today);
'''
new_cell_bg='''        boolean today=date.equals(LocalDate.now());
        boolean selected=date.equals(historySelectedDate);
        if(selected) cell.setBackground(round(SOFT_BLUE,15,BLUE,2));
        else if(today) cell.setBackground(round(Color.rgb(248,251,255),15,Color.rgb(205,220,238),1));

        TextView day=text(String.valueOf(date.getDayOfMonth()),15,(today||selected)?BLUE_DARK:TEXT,today||selected);
'''
if old_cell_bg not in s:
    raise SystemExit("history day-cell background anchor missing")
s=s.replace(old_cell_bg,new_cell_bg,1)

# Keep the existing popup, but also update the persistent editor below the calendar.
old_click='''        cell.setOnClickListener(v->showHistoryDayDialog(meds,date));
        return cell;
'''
new_click='''        cell.setOnClickListener(v->{
            historySelectedDate=date;
            showHistory();
            showHistoryDayDialog(MedicationStore.getMedicines(this),date);
        });
        return cell;
'''
if old_click not in s:
    raise SystemExit("history date click anchor missing")
s=s.replace(old_click,new_click,1)

# When changing months, make the selected day visible in that month.
old_move='''    private void moveHistoryMonth(int delta){
        historyMonth=historyMonth.plusMonths(delta);
        showHistory();
    }
'''
new_move='''    private void moveHistoryMonth(int delta){
        historyMonth=historyMonth.plusMonths(delta);
        java.time.YearMonth selectedMonth=historySelectedDate==null?null:java.time.YearMonth.from(historySelectedDate);
        if(selectedMonth==null || !selectedMonth.equals(historyMonth)){
            historySelectedDate=historyMonth.equals(java.time.YearMonth.now())?LocalDate.now():historyMonth.atDay(1);
        }
        showHistory();
    }
'''
if old_move not in s:
    raise SystemExit("history month move anchor missing")
s=s.replace(old_move,new_move,1)

# Make undoing an accidental "Taken" restore today's repeat reminder as well.
old_undo='''    private void confirmUndo(String medId,LocalDate date,String slot){Medicine m=MedicationStore.getMedicine(this,medId);if(m==null)return;new AlertDialog.Builder(this).setTitle(I18n.t(this,"edit_record")).setMessage(I18n.t(this,"undo_message",m.name,TimeUtil.time(this,slot))).setNegativeButton(I18n.t(this,"cancel"),null).setPositiveButton(I18n.t(this,"delete_record"),(d,w)->{MedicationStore.undoTaken(this,medId,date,slot);renderCurrent();}).show();}
'''
new_undo='''    private void confirmUndo(String medId,LocalDate date,String slot){
        Medicine m=MedicationStore.getMedicine(this,medId);
        if(m==null)return;
        new AlertDialog.Builder(this)
                .setTitle(I18n.t(this,"edit_record"))
                .setMessage(I18n.t(this,"undo_message",m.name,TimeUtil.time(this,slot)))
                .setNegativeButton(I18n.t(this,"cancel"),null)
                .setPositiveButton(I18n.t(this,"delete_record"),(d,w)->{
                    boolean undone=MedicationStore.undoTaken(this,medId,date,slot);
                    if(undone && date.equals(LocalDate.now())
                            && MedicationStore.isDayEnabled(m,date)
                            && !LocalTime.now().isBefore(LocalTime.parse(slot))){
                        AlarmScheduler.scheduleNextSecondaryAligned(this,medId,slot);
                    }
                    renderCurrent();
                }).show();
    }
'''
if old_undo not in s:
    raise SystemExit("confirmUndo anchor missing")
s=s.replace(old_undo,new_undo,1)

# Insert the new persistent record editor before month navigation.
insert_anchor='''    private void moveHistoryMonth(int delta){
'''
if insert_anchor not in s:
    raise SystemExit("history editor insertion anchor missing")
editor_methods=r'''    private void addHistoryRecordEditor(List<Medicine> meds, LocalDate date){
        TextView title=text(I18n.t(this,"history_quick_edit_title"),22,TEXT,true);
        title.setPadding(dp(4),dp(4),0,dp(4));
        content.addView(title);

        TextView dateTitle=text(TimeUtil.date(this,date),16,BLUE_DARK,true);
        dateTitle.setPadding(dp(4),0,0,dp(2));
        content.addView(dateTitle);

        TextView hint=text(I18n.t(this,"history_quick_edit_hint"),14,MUTED,false);
        hint.setPadding(dp(4),0,dp(4),dp(10));
        content.addView(hint);

        boolean any=false;
        LocalDate today=LocalDate.now();
        LocalTime now=LocalTime.now();

        for(Medicine m:meds){
            if(!MedicationStore.isDayEnabled(m,date)) continue;
            for(String slot:m.times){
                any=true;
                boolean taken=MedicationStore.isTaken(this,m.id,date,slot);
                boolean editableMissing=!taken && (date.isBefore(today)
                        || (date.equals(today) && !now.isBefore(LocalTime.parse(slot))));
                content.addView(historyEditorCard(m,date,slot,taken,editableMissing),matchWrap(0,dp(8)));
            }
        }

        if(!any){
            LinearLayout empty=card();
            TextView none=text(I18n.t(this,"no_scheduled"),15,MUTED,false);
            none.setPadding(dp(2),dp(4),dp(2),dp(4));
            empty.addView(none);
            content.addView(empty,matchWrap(0,dp(8)));
        }
    }

    private View historyEditorCard(Medicine m, LocalDate date, String slot, boolean taken, boolean editableMissing){
        LinearLayout row=card();
        row.setOrientation(LinearLayout.VERTICAL);
        row.setPadding(dp(14),dp(14),dp(14),dp(12));

        LinearLayout head=new LinearLayout(this);
        head.setOrientation(LinearLayout.HORIZONTAL);
        head.setGravity(Gravity.CENTER_VERTICAL);

        MedicationIconView medIcon=new MedicationIconView(this,MedicationIconStore.get(this,m.id));
        head.addView(medIcon,new LinearLayout.LayoutParams(dp(46),dp(46)));

        LinearLayout labels=new LinearLayout(this);
        labels.setOrientation(LinearLayout.VERTICAL);
        labels.setPadding(dp(12),0,0,0);
        labels.addView(text(m.name+" · "+TimeUtil.time(this,slot),17,TEXT,true));

        String detail;
        int detailColor;
        if(taken){
            LocalTime actual=MedicationStore.takenTime(this,m.id,date,slot);
            detail=actual==null?I18n.t(this,"calendar_all_done")
                    :I18n.t(this,"dose_taken_prefix",TimeUtil.time(this,actual));
            detailColor=BLUE;
        }else if(editableMissing){
            detail=I18n.t(this,"missed");
            detailColor=WARNING;
        }else{
            detail=I18n.t(this,"scheduled");
            detailColor=MUTED;
        }
        labels.addView(text(detail,14,detailColor,taken));
        head.addView(labels,new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.WRAP_CONTENT,1));
        row.addView(head);

        if(taken){
            Button undo=smallButton(I18n.t(this,"history_mark_not_taken"));
            undo.setOnClickListener(v->confirmUndo(m.id,date,slot));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(46));
            lp.topMargin=dp(10);
            row.addView(undo,lp);
        }else if(editableMissing){
            Button mark=smallButton(I18n.t(this,"history_mark_taken"));
            mark.setOnClickListener(v->editHistoryTakenTime(m,date,slot));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(46));
            lp.topMargin=dp(10);
            row.addView(mark,lp);
        }
        return row;
    }

    private void editHistoryTakenTime(Medicine m, LocalDate date, String slot){
        if(date.isAfter(LocalDate.now())) return;
        LocalTime scheduled=LocalTime.parse(slot);
        LocalTime initial=date.equals(LocalDate.now())?LocalTime.now():scheduled;
        new TimePickerDialog(this,(view,hour,minute)->{
            LocalTime actual=LocalTime.of(hour,minute);
            boolean added=MedicationStore.markTaken(this,m.id,date,slot,actual);
            if(added && date.equals(LocalDate.now())){
                AlarmScheduler.cancelSecondary(this,m.id,slot);
                NotificationHelper.cancelDose(this,m.id,slot);
                ActionReceiver.maybeWarnLowStock(this,m.id);
            }
            historySelectedDate=date;
            showHistory();
            Toast.makeText(this,
                    added?I18n.t(this,"recorded"):I18n.t(this,"already_recorded"),
                    Toast.LENGTH_SHORT).show();
        },initial.getHour(),initial.getMinute(),android.text.format.DateFormat.is24HourFormat(this)).show();
    }

'''
s=s.replace(insert_anchor,editor_methods+insert_anchor,1)

main_file.write_text(s,encoding="utf-8")

# Six-language UI copy.
i=i18n_file.read_text(encoding="utf-8")
anchor='''        M.put("calendar_none_done",new String[]{"미완료","None","未完了","未完成","कोई पूरा नहीं","Ninguna"});
'''
if anchor not in i:
    raise SystemExit("history i18n insertion anchor missing")
extra=anchor+r'''        M.put("history_quick_edit_title",new String[]{"복용 기록 수정","Edit intake records","服用記録を編集","编辑服用记录","सेवन रिकॉर्ड संपादित करें","Editar registros de tomas"});
        M.put("history_quick_edit_hint",new String[]{"날짜를 선택한 뒤 아래에서 복용 여부를 바로 수정할 수 있습니다.","Select a date, then correct its intake status below.","日付を選ぶと、下で服用状況をすぐに修正できます。","选择日期后，可在下方直接修改服用状态。","तारीख चुनें और नीचे सेवन स्थिति सीधे ठीक करें।","Selecciona una fecha y corrige abajo el estado de cada toma."});
        M.put("history_mark_taken",new String[]{"먹었어요로 기록","Mark as taken","服用済みにする","标记为已服用","लिया हुआ दर्ज करें","Marcar como tomado"});
        M.put("history_mark_not_taken",new String[]{"먹었어요 취소","Undo taken","服用済みを取り消す","取消已服用","लिया हुआ रद्द करें","Deshacer tomado"});
'''
i=i.replace(anchor,extra,1)
i18n_file.write_text(i,encoding="utf-8")

print("v3.0.17 calendar quick record editor applied")
