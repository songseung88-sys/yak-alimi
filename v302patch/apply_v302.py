from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')

def replace(path, old, new, count=None):
    p = ROOT / path
    s = p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing expected text in {path}: {old[:120]!r}')
    s2 = s.replace(old, new, count if count is not None else -1)
    p.write_text(s2, encoding='utf-8')

# Version
replace('app/build.gradle', 'versionCode 31', 'versionCode 32', 1)
replace('app/build.gradle', "versionName '3.0.1'", "versionName '3.0.2'", 1)

# Update-specific full-screen permission message, localized in all supported languages.
i18n = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
s = i18n.read_text(encoding='utf-8')
needle = '        M.put("updated_message",new String[]{"약 알리미 %s로 업데이트되었습니다.\\n기존 약과 복용 기록은 그대로 유지됩니다.","Medication Reminder was updated to %s.\\nYour medicines and dose records were kept.","お薬リマインダーを%sに更新しました。\\n登録済みの薬と服用記録はそのまま保持されています。","用药提醒已更新至%s。\\n已保存的药物和服药记录均已保留。","दवा रिमाइंडर %s में अपडेट हो गया है।\\nआपकी दवाएँ और खुराक रिकॉर्ड सुरक्षित हैं।","Recordatorio de medicación se actualizó a %s.\\nTus medicamentos y registros se conservaron."});\n'
if needle not in s:
    raise SystemExit('updated_message line missing')
extra = needle + '        M.put("updated_fullscreen_revoked",new String[]{"업데이트로 인해 전체화면 알림 권한이 해제되었습니다.\\n잠금화면 복용 알림을 계속 사용하려면 다시 허용해주세요.","The update has disabled full-screen alert permission.\\nTo keep using lock-screen medication reminders, please allow it again.","アップデートにより全画面通知の権限が解除されました。\\nロック画面の服薬リマインダーを引き続き使用するには、もう一度許可してください。","更新后，全屏提醒权限已被关闭。\\n如需继续使用锁屏服药提醒，请重新允许此权限。","अपडेट के कारण फुल-स्क्रीन अलर्ट की अनुमति बंद हो गई है।\\nलॉक स्क्रीन पर दवा रिमाइंडर जारी रखने के लिए इसे फिर से अनुमति दें।","La actualización ha desactivado el permiso de avisos a pantalla completa.\\nPara seguir usando los recordatorios de medicación en la pantalla de bloqueo, vuelve a permitirlo."});\n'
s = s.replace(needle, extra, 1)
i18n.write_text(s, encoding='utf-8')

# Append the warning only when an update notice is being shown and the special access is actually off.
main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
s = main.read_text(encoding='utf-8')
old = '''    private void maybeShowUpdateNotice(){
        if(!AppMigration.consumeUpdateNotice(this)) return;
        new AlertDialog.Builder(this)
                .setTitle(I18n.t(this,"updated_title"))
                .setMessage(I18n.t(this,"updated_message",AppMigration.currentVersionName(this)))
                .setPositiveButton(android.R.string.ok,null)
                .show();
    }'''
new = '''    private void maybeShowUpdateNotice(){
        if(!AppMigration.consumeUpdateNotice(this)) return;
        boolean fullScreenNeedsPermission = Build.VERSION.SDK_INT >= 34 && !NotificationHelper.canUseFullScreenIntent(this);
        String message = I18n.t(this,"updated_message",AppMigration.currentVersionName(this));
        if(fullScreenNeedsPermission) message += "\\n\\n" + I18n.t(this,"updated_fullscreen_revoked");
        AlertDialog.Builder builder = new AlertDialog.Builder(this)
                .setTitle(I18n.t(this,"updated_title"))
                .setMessage(message);
        if(fullScreenNeedsPermission){
            builder.setPositiveButton(I18n.t(this,"allow_fullscreen"),(d,w)->requestFullScreenPermission())
                    .setNegativeButton(android.R.string.cancel,null);
        }else{
            builder.setPositiveButton(android.R.string.ok,null);
        }
        builder.show();
    }'''
if old not in s:
    raise SystemExit('maybeShowUpdateNotice block missing')
s = s.replace(old, new, 1)
main.write_text(s, encoding='utf-8')

print('V3.0.2 patch applied')
