from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
BUILD = ROOT / 'app/build.gradle'
MAIN = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'
I18N = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'

# The actual Apps Script deployment URL is intentionally blank until the developer deploys
# the receiver. Keeping it in BuildConfig lets us wire the endpoint without changing UI code.
s = BUILD.read_text(encoding='utf-8')
if 'FEEDBACK_ENDPOINT' not in s:
    lines = s.splitlines()
    inserted = False
    for i, line in enumerate(lines):
        if 'buildConfigField' in line and 'FEEDBACK_EMAIL' in line:
            indent = line[:len(line)-len(line.lstrip())]
            lines.insert(i+1, indent + 'buildConfigField "String", "FEEDBACK_ENDPOINT", "\\\"\\\""')
            inserted = True
            break
    if not inserted:
        raise SystemExit('FEEDBACK_EMAIL BuildConfig anchor missing')
    s = '\n'.join(lines) + '\n'
BUILD.write_text(s, encoding='utf-8')

# Add localized feedback form strings in all six supported languages.
s = I18N.read_text(encoding='utf-8')
if 'M.put("feedback_form_intro"' not in s:
    anchor_pos = s.find('        M.put("restore_purchase_desc"')
    if anchor_pos < 0:
        raise SystemExit('I18n insertion anchor missing')
    line_end = s.find('\n', anchor_pos)
    if line_end < 0:
        raise SystemExit('I18n insertion line end missing')
    addition = '''        M.put("feedback_form_intro",new String[]{"앱에서 불편했던 점이나 개선 아이디어를 보내주세요.","Tell us what was inconvenient or what we could improve.","不便だった点や改善のアイデアをお送りください。","欢迎告诉我们使用中的不便或改进建议。","ऐप में हुई परेशानी या सुधार के सुझाव भेजें।","Cuéntanos qué te resultó incómodo o qué podríamos mejorar."});\n        M.put("feedback_category",new String[]{"의견 종류","Category","種類","意见类型","श्रेणी","Categoría"});\n        M.put("feedback_bug",new String[]{"버그 제보","Bug report","不具合報告","错误报告","बग रिपोर्ट","Informar de un error"});\n        M.put("feedback_suggestion",new String[]{"개선 제안","Suggestion","改善提案","改进建议","सुधार सुझाव","Sugerencia"});\n        M.put("feedback_other",new String[]{"기타","Other","その他","其他","अन्य","Otro"});\n        M.put("feedback_message_hint",new String[]{"의견을 입력해주세요.","Write your feedback here.","ご意見を入力してください。","请输入您的意见。","अपनी प्रतिक्रिया लिखें।","Escribe aquí tus comentarios."});\n        M.put("feedback_privacy_note",new String[]{"약·영양제 이름, 복용 기록, 재고 정보는 자동으로 전송되지 않습니다.","Medication, supplement, intake-record and inventory data are never attached automatically.","薬・サプリ名、服用記録、在庫情報は自動送信されません。","药品、营养补充剂、服用记录和库存信息不会自动发送。","दवा, सप्लीमेंट, सेवन रिकॉर्ड और स्टॉक की जानकारी अपने-आप नहीं भेजी जाती।","Los datos de medicamentos, suplementos, tomas e inventario no se adjuntan automáticamente."});\n        M.put("feedback_send",new String[]{"보내기","Send","送信","发送","भेजें","Enviar"});\n        M.put("feedback_required",new String[]{"의견을 입력해주세요.","Please enter your feedback.","ご意見を入力してください。","请输入您的意见。","कृपया अपनी प्रतिक्रिया लिखें।","Escribe tus comentarios."});\n        M.put("feedback_too_long",new String[]{"의견은 3,000자 이내로 작성해주세요.","Please keep feedback within 3,000 characters.","3,000文字以内で入力してください。","意见请控制在3,000字以内。","प्रतिक्रिया 3,000 अक्षरों के भीतर रखें।","Limita los comentarios a 3.000 caracteres."});\n        M.put("feedback_sending",new String[]{"전송 중…","Sending…","送信中…","正在发送…","भेजा जा रहा है…","Enviando…"});\n        M.put("feedback_sent",new String[]{"의견을 보내주셔서 감사합니다.","Thank you for your feedback.","ご意見ありがとうございます。","感谢您的反馈。","आपकी प्रतिक्रिया के लिए धन्यवाद।","Gracias por tus comentarios."});\n        M.put("feedback_failed",new String[]{"전송하지 못했습니다. 잠시 후 다시 시도해주세요.","Could not send. Please try again later.","送信できませんでした。しばらくしてからもう一度お試しください。","发送失败，请稍后重试。","भेजा नहीं जा सका। कृपया बाद में फिर कोशिश करें।","No se pudo enviar. Inténtalo de nuevo más tarde."});\n        M.put("feedback_not_ready",new String[]{"의견 전송 서버가 아직 연결되지 않았습니다.","The feedback service is not connected yet.","フィードバック送信サービスはまだ接続されていません。","意见发送服务尚未连接。","फ़ीडबैक सेवा अभी कनेक्ट नहीं है।","El servicio de comentarios aún no está conectado."});\n'''
    s = s[:line_end+1] + addition + s[line_end+1:]
I18N.write_text(s, encoding='utf-8')

# Replace the existing external-email feedback method. We deliberately locate the method by
# its BuildConfig.FEEDBACK_EMAIL usage, so this patch remains resilient to the method name.
s = MAIN.read_text(encoding='utf-8')
pos = s.find('BuildConfig.FEEDBACK_EMAIL')
if pos < 0:
    raise SystemExit('existing feedback email flow not found')
start = s.rfind('    private void ', 0, pos)
if start < 0:
    raise SystemExit('feedback method start not found')
brace = s.find('{', start)
if brace < 0 or brace > pos:
    raise SystemExit('feedback method opening brace not found')
match = re.search(r'private void\s+(\w+)\s*\(', s[start:brace])
if not match:
    raise SystemExit('feedback method name not found')
method_name = match.group(1)

depth = 0
end = None
for i in range(brace, len(s)):
    ch = s[i]
    if ch == '{': depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
if end is None:
    raise SystemExit('feedback method closing brace not found')

replacement = f'''    private void {method_name}(){{
        LinearLayout box=new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(20),dp(4),dp(20),0);

        TextView intro=text(I18n.t(this,"feedback_form_intro"),15,MUTED,false);
        intro.setPadding(0,0,0,dp(14));
        box.addView(intro);

        TextView categoryLabel=text(I18n.t(this,"feedback_category"),14,TEXT,true);
        categoryLabel.setPadding(0,0,0,dp(6));
        box.addView(categoryLabel);

        final String[] categoryCodes=new String[]{{"bug","suggestion","other"}};
        String[] categoryLabels=new String[]{{I18n.t(this,"feedback_bug"),I18n.t(this,"feedback_suggestion"),I18n.t(this,"feedback_other")}};
        android.widget.Spinner category=new android.widget.Spinner(this);
        android.widget.ArrayAdapter<String> adapter=new android.widget.ArrayAdapter<>(this,android.R.layout.simple_spinner_item,categoryLabels);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        category.setAdapter(adapter);
        box.addView(category,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(52)));

        EditText message=new EditText(this);
        message.setHint(I18n.t(this,"feedback_message_hint"));
        message.setTextSize(16);
        message.setGravity(Gravity.TOP|Gravity.START);
        message.setMinLines(6);
        message.setMaxLines(10);
        message.setPadding(dp(14),dp(12),dp(14),dp(12));
        message.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE|android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        message.setBackground(round(Color.WHITE,14,Color.rgb(215,222,228),1));
        box.addView(message,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(170)));

        TextView privacy=text(I18n.t(this,"feedback_privacy_note"),12,MUTED,false);
        privacy.setPadding(0,dp(10),0,0);
        box.addView(privacy);

        AlertDialog dialog=new AlertDialog.Builder(this)
                .setTitle(I18n.t(this,"feedback"))
                .setView(box)
                .setNegativeButton(I18n.t(this,"cancel"),null)
                .setPositiveButton(I18n.t(this,"feedback_send"),null)
                .create();
        dialog.setOnShowListener(d->{{
            Button send=dialog.getButton(AlertDialog.BUTTON_POSITIVE);
            send.setOnClickListener(v->{{
                String body=message.getText().toString().trim();
                if(body.isEmpty()){{message.setError(I18n.t(this,"feedback_required"));return;}}
                if(body.length()>3000){{message.setError(I18n.t(this,"feedback_too_long"));return;}}
                int selected=Math.max(0,Math.min(category.getSelectedItemPosition(),categoryCodes.length-1));
                submitInAppFeedback(categoryCodes[selected],body,dialog,send);
            }});
        }});
        dialog.show();
    }}

    private void submitInAppFeedback(String category, String message, AlertDialog dialog, Button sendButton){{
        String endpoint=BuildConfig.FEEDBACK_ENDPOINT==null?"":BuildConfig.FEEDBACK_ENDPOINT.trim();
        if(endpoint.isEmpty() || !endpoint.startsWith("https://")){{
            Toast.makeText(this,I18n.t(this,"feedback_not_ready"),Toast.LENGTH_LONG).show();
            return;
        }}
        sendButton.setEnabled(false);
        String original=sendButton.getText().toString();
        sendButton.setText(I18n.t(this,"feedback_sending"));
        new Thread(()->{{
            java.net.HttpURLConnection connection=null;
            boolean ok=false;
            try{{
                java.net.URL url=new java.net.URL(endpoint);
                connection=(java.net.HttpURLConnection)url.openConnection();
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(12000);
                connection.setInstanceFollowRedirects(true);
                connection.setRequestMethod("POST");
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type","application/json; charset=UTF-8");
                connection.setRequestProperty("Accept","application/json");
                org.json.JSONObject payload=new org.json.JSONObject();
                payload.put("source","yak-alimi-android");
                payload.put("category",category);
                payload.put("message",message);
                byte[] data=payload.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8);
                connection.setFixedLengthStreamingMode(data.length);
                try(java.io.OutputStream os=connection.getOutputStream()){{os.write(data);}}
                int code=connection.getResponseCode();
                java.io.InputStream stream=(code>=200&&code<400)?connection.getInputStream():connection.getErrorStream();
                StringBuilder response=new StringBuilder();
                if(stream!=null){{
                    try(java.io.BufferedReader r=new java.io.BufferedReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8))){{
                        String line;while((line=r.readLine())!=null)response.append(line);
                    }}
                }}
                ok=code>=200&&code<400 && response.toString().replace(" ","").contains("\\\"ok\\\":true");
            }}catch(Exception ignored){{
                ok=false;
            }}finally{{
                if(connection!=null)connection.disconnect();
            }}
            final boolean success=ok;
            runOnUiThread(()->{{
                if(success){{
                    if(dialog.isShowing())dialog.dismiss();
                    Toast.makeText(this,I18n.t(this,"feedback_sent"),Toast.LENGTH_LONG).show();
                }}else{{
                    sendButton.setEnabled(true);
                    sendButton.setText(original);
                    Toast.makeText(this,I18n.t(this,"feedback_failed"),Toast.LENGTH_LONG).show();
                }}
            }});
        }}).start();
    }}'''

s = s[:start] + replacement + s[end:]
MAIN.write_text(s, encoding='utf-8')
print('V3.0.3 in-app feedback form patch applied; endpoint remains blank until Apps Script deployment')
