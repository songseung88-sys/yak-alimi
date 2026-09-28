const DESTINATION_EMAIL = 'songseung88@hanmail.net';
const DAILY_LIMIT = 100;
const MAX_MESSAGE_LENGTH = 3000;

function doGet() {
  return ContentService
    .createTextOutput('Yak Alimi feedback server is running.')
    .setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return jsonResponse({ ok: false, error: 'empty_request' });
    }

    const data = JSON.parse(e.postData.contents);
    if (data.source !== 'yak-alimi-android') {
      return jsonResponse({ ok: false, error: 'invalid_source' });
    }

    const category = String(data.category || 'other');
    const message = String(data.message || '').trim();
    if (!message) {
      return jsonResponse({ ok: false, error: 'empty_message' });
    }
    if (message.length > MAX_MESSAGE_LENGTH) {
      return jsonResponse({ ok: false, error: 'message_too_long' });
    }

    if (!consumeDailyQuota_()) {
      return jsonResponse({ ok: false, error: 'daily_limit_reached' });
    }

    const categoryLabel = {
      bug: '버그 제보',
      suggestion: '개선 제안',
      other: '기타'
    }[category] || '기타';

    const subject = '[약 알리미 의견] ' + categoryLabel;
    const body = [
      '약 알리미 앱 내부 의견 보내기',
      '',
      '유형: ' + categoryLabel,
      '접수 시각: ' + Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss'),
      '',
      '내용:',
      message,
      '',
      '※ 약·영양제 이름, 복용 기록, 재고 등 앱의 복용 데이터는 자동 첨부되지 않습니다.'
    ].join('\n');

    MailApp.sendEmail(DESTINATION_EMAIL, subject, body);
    return jsonResponse({ ok: true });
  } catch (err) {
    console.error(err);
    return jsonResponse({ ok: false, error: 'server_error' });
  }
}

function consumeDailyQuota_() {
  const props = PropertiesService.getScriptProperties();
  const key = 'feedback_count_' + Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyyMMdd');
  const current = Number(props.getProperty(key) || '0');
  if (current >= DAILY_LIMIT) return false;
  props.setProperty(key, String(current + 1));
  return true;
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
