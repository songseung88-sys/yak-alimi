from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
i18n = ROOT / 'app/src/main/java/com/yakalimi/app/I18n.java'
main = ROOT / 'app/src/main/java/com/yakalimi/app/MainActivity.java'

s = i18n.read_text(encoding='utf-8')

repls = {
'        M.put("no_meds",new String[]{"등록된 약이 없습니다","No medicines added","薬が登録されていません","尚未添加药物","कोई दवा जोड़ी नहीं गई","No hay medicamentos añadidos"});':
'        M.put("no_meds",new String[]{"등록된 약이나 영양제가 없습니다","No medications or supplements added","薬やサプリメントが登録されていません","尚未添加药物或保健品","कोई दवा या सप्लीमेंट जोड़ा नहीं गया","No hay medicamentos ni suplementos añadidos"});',
'        M.put("no_meds_sub",new String[]{"약 이름, 복용 횟수와 알림 시간을 등록해보세요.","Add a medicine, dose frequency, and reminder times.","薬名、服用回数と通知時刻を登録しましょう。","添加药名、服用次数和提醒时间。","दवा का नाम, खुराक की संख्या और रिमाइंडर समय जोड़ें।","Añade el medicamento, la frecuencia y las horas de aviso."});':
'        M.put("no_meds_sub",new String[]{"약·영양제 이름, 복용 횟수와 알림 시간을 등록해보세요.","Add a medication or supplement, intake frequency, and reminder times.","薬・サプリメント名、服用回数と通知時刻を登録しましょう。","添加药物或保健品名称、服用次数和提醒时间。","दवा या सप्लीमेंट का नाम, लेने की आवृत्ति और रिमाइंडर समय जोड़ें।","Añade un medicamento o suplemento, la frecuencia y las horas de aviso."});',
'        M.put("add_medicine",new String[]{"새 약 추가","Add medicine","薬を追加","添加药物","दवा जोड़ें","Añadir medicamento"});':
'        M.put("add_medicine",new String[]{"약·영양제 추가","Add medication or supplement","薬・サプリを追加","添加药物或保健品","दवा या सप्लीमेंट जोड़ें","Añadir medicamento o suplemento"});',
'        M.put("my_medicines",new String[]{"내 약","My medicines","登録した薬","我的药物","मेरी दवाएँ","Mis medicamentos"});':
'        M.put("my_medicines",new String[]{"내 복용 목록","My intake list","服用リスト","我的服用列表","मेरी सेवन सूची","Mi lista de tomas"});',
'        M.put("no_meds_period",new String[]{"등록된 약이 없습니다.","No medicines added.","薬が登録されていません。","尚未添加药物。","कोई दवा जोड़ी नहीं गई।","No hay medicamentos añadidos."});':
'        M.put("no_meds_period",new String[]{"등록된 약이나 영양제가 없습니다.","No medications or supplements added.","薬やサプリメントが登録されていません。","尚未添加药物或保健品。","कोई दवा या सप्लीमेंट जोड़ा नहीं गया।","No hay medicamentos ni suplementos añadidos."});',
'        M.put("medicine_management",new String[]{"약 관리","Manage medicines","薬の管理","药物管理","दवा प्रबंधन","Gestionar medicamentos"});':
'        M.put("medicine_management",new String[]{"약·영양제 관리","Manage medications & supplements","薬・サプリ管理","药物与保健品管理","दवा और सप्लीमेंट प्रबंधन","Gestionar medicamentos y suplementos"});',
'        M.put("new_medicine",new String[]{"새 약 추가","Add medicine","薬を追加","添加药物","दवा जोड़ें","Añadir medicamento"});':
'        M.put("new_medicine",new String[]{"약·영양제 추가","Add medication or supplement","薬・サプリを追加","添加药物或保健品","दवा या सप्लीमेंट जोड़ें","Añadir medicamento o suplemento"});',
'        M.put("edit_medicine",new String[]{"약 수정","Edit medicine","薬を編集","编辑药物","दवा संपादित करें","Editar medicamento"});':
'        M.put("edit_medicine",new String[]{"약·영양제 수정","Edit medication or supplement","薬・サプリを編集","编辑药物或保健品","दवा या सप्लीमेंट संपादित करें","Editar medicamento o suplemento"});',
'        M.put("medicine_name",new String[]{"약 이름","Medicine name","薬の名前","药物名称","दवा का नाम","Nombre del medicamento"});':
'        M.put("medicine_name",new String[]{"이름","Name","名前","名称","नाम","Nombre"});\n        M.put("medicine_name_hint",new String[]{"약 또는 영양제 이름","Medication or supplement name","薬またはサプリメント名","药物或保健品名称","दवा या सप्लीमेंट का नाम","Nombre del medicamento o suplemento"});',
'        M.put("current_inventory",new String[]{"현재 약 보유량","Current stock","現在の残数","当前库存","मौजूदा स्टॉक","Stock actual"});':
'        M.put("current_inventory",new String[]{"현재 보유량","Current stock","現在の残数","当前库存","मौजूदा स्टॉक","Stock actual"});',
'        M.put("register_medicine",new String[]{"✓  약 등록","✓  Add medicine","✓  薬を登録","✓  添加药物","✓  दवा जोड़ें","✓  Añadir medicamento"});':
'        M.put("register_medicine",new String[]{"✓  등록","✓  Add","✓  登録","✓  添加","✓  जोड़ें","✓  Añadir"});',
'        M.put("delete_medicine",new String[]{"약 삭제","Delete medicine","薬を削除","删除药物","दवा हटाएँ","Eliminar medicamento"});':
'        M.put("delete_medicine",new String[]{"삭제","Delete","削除","删除","हटाएँ","Eliminar"});',
'        M.put("delete_message",new String[]{"%s을(를) 약 목록에서 삭제할까요?","Delete %s from your medicines?","%sを薬の一覧から削除しますか？","从药物列表中删除%s？","%s को दवाओं की सूची से हटाएँ?","¿Eliminar %s de tus medicamentos?"});':
'        M.put("delete_message",new String[]{"%s을(를) 복용 목록에서 삭제할까요?","Delete %s from your intake list?","%sを服用リストから削除しますか？","从服用列表中删除%s？","%s को सेवन सूची से हटाएँ?","¿Eliminar %s de tu lista de tomas?"});',
'        M.put("stock_add_title",new String[]{"약 재고 추가","Add medicine stock","薬の残数を追加","添加药物库存","दवा स्टॉक जोड़ें","Añadir stock"});':
'        M.put("stock_add_title",new String[]{"재고 추가","Add stock","残数を追加","添加库存","स्टॉक जोड़ें","Añadir existencias"});',
'        M.put("name_required",new String[]{"약 이름을 입력해주세요.","Enter a medicine name.","薬の名前を入力してください。","请输入药物名称。","दवा का नाम दर्ज करें।","Introduce el nombre del medicamento."});':
'        M.put("name_required",new String[]{"이름을 입력해주세요.","Enter a name.","名前を入力してください。","请输入名称。","नाम दर्ज करें।","Introduce un nombre."});',
'        M.put("dose_time",new String[]{"복용 시간입니다","Time to take your medicine","服用時間です","该服药了","दवा लेने का समय है","Es hora de tomar tu medicación"});':
'        M.put("dose_time",new String[]{"복용 시간입니다","Time for your dose","服用時間です","该服用了","लेने का समय है","Es hora de tomarlo"});',
'        M.put("low_stock_text",new String[]{"약이 얼마 남지 않았어요. 다음 약을 준비해주세요.","Your medicine is running low. Prepare your next supply.","薬の残りが少なくなっています。次の分を準備してください。","药物库存不足，请准备下一批。","दवा कम बची है। अगली आपूर्ति तैयार करें।","Queda poca medicación. Prepara la siguiente reposición."});':
'        M.put("low_stock_text",new String[]{"남은 수량이 적습니다. 다음 분량을 준비해주세요.","You are running low. Prepare your next supply.","残りが少なくなっています。次の分を準備してください。","剩余数量较少，请准备下一批。","मात्रा कम बची है। अगली आपूर्ति तैयार करें।","Quedan pocas unidades. Prepara la siguiente reposición."});',
'        M.put("channel_stock_desc",new String[]{"남은 약 개수 알림","Medicine stock reminders","薬の残数通知","药物库存提醒","दवा स्टॉक रिमाइंडर","Avisos de existencias de medicación"});':
'        M.put("channel_stock_desc",new String[]{"남은 수량 알림","Stock reminders","残数通知","剩余数量提醒","बची मात्रा के रिमाइंडर","Avisos de existencias"});',
'        M.put("updated_message",new String[]{"약 알리미 %s로 업데이트되었습니다.\\n기존 약과 복용 기록은 그대로 유지됩니다.","Medication Reminder was updated to %s.\\nYour medicines and dose records were kept.","お薬リマインダーを%sに更新しました。\\n登録済みの薬と服用記録はそのまま保持されています。","用药提醒已更新至%s。\\n已保存的药物和服药记录均已保留。","दवा रिमाइंडर %s में अपडेट हो गया है।\\nआपकी दवाएँ और खुराक रिकॉर्ड सुरक्षित हैं।","Recordatorio de medicación se actualizó a %s.\\nTus medicamentos y registros se conservaron."});':
'        M.put("updated_message",new String[]{"약 알리미 %s로 업데이트되었습니다.\\n기존 약·영양제와 복용 기록은 그대로 유지됩니다.","Medication Reminder was updated to %s.\\nYour medications, supplements, and intake records were kept.","お薬リマインダーを%sに更新しました。\\n登録済みの薬・サプリメントと服用記録はそのまま保持されています。","用药提醒已更新至%s。\\n已保存的药物、保健品和服用记录均已保留。","दवा रिमाइंडर %s में अपडेट हो गया है।\\nआपकी दवाएँ, सप्लीमेंट और सेवन रिकॉर्ड सुरक्षित हैं।","Recordatorio de medicación se actualizó a %s.\\nTus medicamentos, suplementos y registros se conservaron."});',
'        M.put("premium_active_desc",new String[]{"광고 없이 여러 약을 등록하고 모든 기능을 사용할 수 있습니다.","No ads, multiple medications, and access to all features.","広告なしで複数の薬を登録し、すべての機能を利用できます。","无广告，可添加多种药物并使用全部功能。","बिना विज्ञापन, कई दवाइयाँ और सभी सुविधाएँ इस्तेमाल करें।","Sin anuncios, varios medicamentos y acceso a todas las funciones."});':
'        M.put("premium_active_desc",new String[]{"광고 없이 여러 약·영양제를 등록하고 모든 기능을 사용할 수 있습니다.","No ads, multiple medications or supplements, and access to all features.","広告なしで複数の薬・サプリメントを登録し、すべての機能を利用できます。","无广告，可添加多种药物或保健品并使用全部功能。","बिना विज्ञापन, कई दवाएँ या सप्लीमेंट और सभी सुविधाएँ इस्तेमाल करें।","Sin anuncios, varios medicamentos o suplementos y acceso a todas las funciones."});',
'        M.put("free_plan_desc",new String[]{"약 1개를 등록할 수 있으며 하단에 광고가 표시됩니다.","Add 1 medicine. A banner ad is shown at the bottom.","薬は1つ登録でき、下部に広告が表示されます。","可添加1种药物，底部显示横幅广告。","1 दवा जोड़ें। नीचे बैनर विज्ञापन दिखेगा।","Añade 1 medicamento. Se muestra un banner abajo."});':
'        M.put("free_plan_desc",new String[]{"약 또는 영양제 1개를 등록할 수 있으며 하단에 광고가 표시됩니다.","Add 1 medication or supplement. A banner ad is shown at the bottom.","薬またはサプリメントを1つ登録でき、下部に広告が表示されます。","可添加1种药物或保健品，底部显示横幅广告。","1 दवा या सप्लीमेंट जोड़ें। नीचे बैनर विज्ञापन दिखेगा।","Añade 1 medicamento o suplemento. Se muestra un banner abajo."});',
'        M.put("premium_message",new String[]{"✓ 광고 없이 사용\\n✓ 여러 약 등록\\n✓ 모든 기능 사용","✓ No ads\\n✓ Add multiple medications\\n✓ Access all features","✓ 広告なし\\n✓ 複数の薬を登録\\n✓ すべての機能を利用","✓ 无广告\\n✓ 可添加多种药物\\n✓ 使用全部功能","✓ बिना विज्ञापन\\n✓ कई दवाइयाँ जोड़ें\\n✓ सभी सुविधाएँ इस्तेमाल करें","✓ Sin anuncios\\n✓ Añade varios medicamentos\\n✓ Accede a todas las funciones"});':
'        M.put("premium_message",new String[]{"✓ 광고 없이 사용\\n✓ 여러 약·영양제 등록\\n✓ 모든 기능 사용","✓ No ads\\n✓ Add multiple medications or supplements\\n✓ Access all features","✓ 広告なし\\n✓ 複数の薬・サプリメントを登録\\n✓ すべての機能を利用","✓ 无广告\\n✓ 可添加多种药物或保健品\\n✓ 使用全部功能","✓ बिना विज्ञापन\\n✓ कई दवाएँ या सप्लीमेंट जोड़ें\\n✓ सभी सुविधाएँ इस्तेमाल करें","✓ Sin anuncios\\n✓ Añade varios medicamentos o suplementos\\n✓ Accede a todas las funciones"});',
'        M.put("premium_required_message",new String[]{"무료 버전에서는 약을 1개까지 등록할 수 있습니다. 프리미엄을 구매하면 광고 없이 여러 약을 등록할 수 있습니다.","The free version supports 1 medication. Unlock Premium to add multiple medications and remove ads.","無料版では薬を1種類まで登録できます。プレミアムにすると、広告なしで複数の薬を登録できます。","免费版最多可添加 1 种药物。升级高级版后，可添加多种药物并移除广告。","मुफ्त संस्करण में 1 दवा तक जोड़ सकते हैं। प्रीमियम खरीदने पर कई दवाइयाँ जोड़ सकते हैं और विज्ञापन हट जाते हैं।","La versión gratuita permite registrar 1 medicamento. Con Premium puedes añadir varios medicamentos y eliminar los anuncios."});':
'        M.put("premium_required_message",new String[]{"무료 버전에서는 약 또는 영양제를 1개까지 등록할 수 있습니다. 프리미엄을 구매하면 광고 없이 여러 약·영양제를 등록할 수 있습니다.","The free version supports 1 medication or supplement. Unlock Premium to add multiple medications or supplements and remove ads.","無料版では薬またはサプリメントを1つまで登録できます。プレミアムにすると、広告なしで複数の薬・サプリメントを登録できます。","免费版最多可添加 1 种药物或保健品。升级高级版后，可添加多种药物或保健品并移除广告。","मुफ्त संस्करण में 1 दवा या सप्लीमेंट तक जोड़ सकते हैं। प्रीमियम खरीदने पर कई दवाएँ या सप्लीमेंट जोड़ सकते हैं और विज्ञापन हट जाते हैं।","La versión gratuita permite registrar 1 medicamento o suplemento. Con Premium puedes añadir varios medicamentos o suplementos y eliminar los anuncios."});',
'        M.put("privacy_policy_text",new String[]{"약 이름, 복용 시간, 복용 기록과 재고 정보는 사용자 기기에만 저장되며 약 알리미 서버로 전송되지 않습니다.","Medicine names, schedules, dose records, and stock are stored only on the user’s device and are not sent to a Yak Alimi server.","薬名、服用時刻、服用記録、在庫情報はユーザーの端末にのみ保存され、薬アラームのサーバーには送信されません。","药名、服药时间、服药记录和库存信息仅保存在用户设备上，不会发送到本应用服务器。","दवा के नाम, समय, रिकॉर्ड और स्टॉक केवल उपयोगकर्ता के डिवाइस पर संग्रहीत होते हैं और ऐप के सर्वर पर नहीं भेजे जाते।","Los nombres, horarios, registros y existencias se guardan únicamente en el dispositivo del usuario y no se envían a un servidor de Yak Alimi."});':
'        M.put("privacy_policy_text",new String[]{"약·영양제 이름, 복용 시간, 복용 기록과 재고 정보는 사용자 기기에만 저장되며 약 알리미 서버로 전송되지 않습니다.","Medication or supplement names, schedules, intake records, and stock are stored only on the user’s device and are not sent to an app server.","薬・サプリメント名、服用時刻、服用記録、在庫情報はユーザーの端末にのみ保存され、アプリのサーバーには送信されません。","药物或保健品名称、服用时间、服用记录和库存信息仅保存在用户设备上，不会发送到本应用服务器。","दवा या सप्लीमेंट के नाम, समय, सेवन रिकॉर्ड और स्टॉक केवल उपयोगकर्ता के डिवाइस पर संग्रहीत होते हैं और ऐप सर्वर पर नहीं भेजे जाते।","Los nombres de medicamentos o suplementos, horarios, registros de tomas y existencias se guardan únicamente en el dispositivo y no se envían al servidor de la app."});',
'        M.put("health_notice_text",new String[]{"약 알리미는 복용 시간을 알려주고 사용자가 입력한 복용 사실을 기록하는 도구입니다. 복용량 변경, 누락된 복용에 대한 대처 등 의학적 판단을 제공하지 않습니다. 약 복용에 관한 판단은 의사·약사 또는 처방 안내를 따르세요.","This app reminds you of medication times and records the doses you mark as taken. It does not provide medical decisions about dose changes or missed doses. Follow your prescription and advice from a doctor or pharmacist.","このアプリは服用時刻の通知と、ユーザーが入力した服用記録を管理するためのツールです。用量変更や飲み忘れ時の対応などの医学的判断は行いません。医師・薬剤師や処方の指示に従ってください。","本应用用于提醒服药时间并记录用户标记的服药情况，不提供剂量调整或漏服处理等医疗判断。请遵循处方以及医生或药师的建议。","यह ऐप दवा लेने का समय याद दिलाता है और आपके द्वारा दर्ज की गई खुराक रिकॉर्ड करता है। यह खुराक बदलने या छूटी खुराक पर चिकित्सा निर्णय नहीं देता। डॉक्टर, फार्मासिस्ट और पर्चे के निर्देशों का पालन करें।","Esta app recuerda los horarios y registra las dosis que marcas como tomadas. No ofrece decisiones médicas sobre cambios de dosis o dosis olvidadas. Sigue la receta y las indicaciones de tu médico o farmacéutico."});':
'        M.put("health_notice_text",new String[]{"약 알리미는 약·영양제의 복용 시간을 알려주고 사용자가 입력한 복용 사실을 기록하는 도구입니다. 복용량 변경, 누락된 복용에 대한 대처 등 의학적 판단을 제공하지 않습니다. 약 복용에 관한 판단은 의사·약사 또는 처방 안내를 따르세요.","This app reminds you when to take medications or supplements and records the intake you mark as taken. It does not provide medical decisions about dose changes or missed doses. For medications, follow your prescription and advice from a doctor or pharmacist.","このアプリは薬・サプリメントの服用時刻を通知し、ユーザーが入力した服用記録を管理するツールです。用量変更や飲み忘れ時の対応などの医学的判断は行いません。薬については医師・薬剤師や処方の指示に従ってください。","本应用用于提醒药物或保健品的服用时间并记录用户标记的服用情况，不提供剂量调整或漏服处理等医疗判断。药物使用请遵循处方以及医生或药师的建议。","यह ऐप दवाएँ या सप्लीमेंट लेने का समय याद दिलाता है और आपके द्वारा दर्ज सेवन को रिकॉर्ड करता है। यह खुराक बदलने या छूटी खुराक पर चिकित्सा निर्णय नहीं देता। दवाओं के लिए डॉक्टर, फार्मासिस्ट और पर्चे के निर्देशों का पालन करें।","Esta app recuerda cuándo tomar medicamentos o suplementos y registra las tomas que marcas. No ofrece decisiones médicas sobre cambios de dosis o dosis olvidadas. Para medicamentos, sigue la receta y las indicaciones de tu médico o farmacéutico."});'
}

for old, new in repls.items():
    if old not in s:
        raise SystemExit(f'missing expected i18n line: {old[:120]}')
    s = s.replace(old, new, 1)

i18n.write_text(s, encoding='utf-8')

m = main.read_text(encoding='utf-8')
old = 'draft=new Medicine();draft.name=I18n.t(this,"medicine_name");draft.alertMode="vibrate";'
new = 'draft=new Medicine();draft.name=I18n.t(this,"medicine_name_hint");draft.alertMode="vibrate";'
if old not in m:
    raise SystemExit('new medicine default-name line missing')
m = m.replace(old, new, 1)
main.write_text(m, encoding='utf-8')

print('V3.0.3 medication + supplement copy patch applied')
