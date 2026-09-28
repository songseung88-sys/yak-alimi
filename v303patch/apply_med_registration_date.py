from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else 'yak_alimi_v21_work')
MED = ROOT / 'app/src/main/java/com/yakalimi/app/Medicine.java'
STORE = ROOT / 'app/src/main/java/com/yakalimi/app/MedicationStore.java'

s = MED.read_text(encoding='utf-8')

# Persist the date on which each medication/supplement was registered in the app.
old = '''import java.util.ArrayList;\nimport java.util.Collections;'''
new = '''import java.time.LocalDate;\nimport java.util.ArrayList;\nimport java.util.Collections;'''
if old not in s:
    raise SystemExit('Medicine import anchor missing')
s = s.replace(old, new, 1)

old = '''    public String alertMode;\n    public final List<String> times = new ArrayList<>();'''
new = '''    public String alertMode;\n    public String createdDate;\n    public final List<String> times = new ArrayList<>();'''
if old not in s:
    raise SystemExit('Medicine field anchor missing')
s = s.replace(old, new, 1)

old = '''        alertMode = "vibrate";\n        times.add("08:00");'''
new = '''        alertMode = "vibrate";\n        createdDate = LocalDate.now().toString();\n        times.add("08:00");'''
if old not in s:
    raise SystemExit('Medicine constructor anchor missing')
s = s.replace(old, new, 1)

old = '''        m.alertMode = alertMode;\n        m.times.clear();'''
new = '''        m.alertMode = alertMode;\n        m.createdDate = createdDate;\n        m.times.clear();'''
if old not in s:
    raise SystemExit('Medicine copy anchor missing')
s = s.replace(old, new, 1)

old = '''            o.put("alertMode", alertMode);\n            JSONArray a = new JSONArray();'''
new = '''            o.put("alertMode", alertMode);\n            o.put("createdDate", createdDate);\n            JSONArray a = new JSONArray();'''
if old not in s:
    raise SystemExit('Medicine toJson anchor missing')
s = s.replace(old, new, 1)

old = '''            m.alertMode = o.optString("alertMode", "vibrate");\n            if (!"sound".equals(m.alertMode) && !"silent".equals(m.alertMode) && !"vibrate".equals(m.alertMode)) m.alertMode = "vibrate";'''
new = '''            m.alertMode = o.optString("alertMode", "vibrate");\n            m.createdDate = o.optString("createdDate", "");\n            if (!"sound".equals(m.alertMode) && !"silent".equals(m.alertMode) && !"vibrate".equals(m.alertMode)) m.alertMode = "vibrate";'''
if old not in s:
    raise SystemExit('Medicine fromJson anchor missing')
s = s.replace(old, new, 1)
MED.write_text(s, encoding='utf-8')

s = STORE.read_text(encoding='utf-8')

# Migrate existing medicines that predate this field. If old dose records exist, the earliest
# recorded dose is the best conservative approximation; otherwise start at the upgrade date.
old = '''            for (int i = 0; i < a.length(); i++) out.add(Medicine.fromJson(a.getJSONObject(i)));\n        } catch (Exception ignored) {}\n        return out;'''
new = '''            for (int i = 0; i < a.length(); i++) out.add(Medicine.fromJson(a.getJSONObject(i)));\n        } catch (Exception ignored) {}\n        boolean changed = false;\n        for (Medicine m : out) {\n            if (m.createdDate == null || m.createdDate.isEmpty()) {\n                m.createdDate = inferLegacyCreatedDate(c, m.id).toString();\n                changed = true;\n            }\n        }\n        if (changed) save(c, out);\n        return out;'''
if old not in s:
    raise SystemExit('MedicationStore getMedicines anchor missing')
s = s.replace(old, new, 1)

old = '''    private static void sanitize(Medicine m) {\n        if (m.id == null || m.id.isEmpty()) m.id = java.util.UUID.randomUUID().toString();'''
new = '''    private static void sanitize(Medicine m) {\n        if (m.id == null || m.id.isEmpty()) m.id = java.util.UUID.randomUUID().toString();\n        if (m.createdDate == null || m.createdDate.isEmpty()) m.createdDate = LocalDate.now().toString();\n        try { LocalDate.parse(m.createdDate); } catch (Exception e) { m.createdDate = LocalDate.now().toString(); }'''
if old not in s:
    raise SystemExit('MedicationStore sanitize anchor missing')
s = s.replace(old, new, 1)

old = '''    public static boolean isDayEnabled(Medicine m, LocalDate date) {\n        int bit = date.getDayOfWeek().getValue() - 1;\n        return (m.daysMask & (1 << bit)) != 0;\n    }'''
new = '''    public static boolean isDayEnabled(Medicine m, LocalDate date) {\n        if (m.createdDate != null && !m.createdDate.isEmpty()) {\n            try { if (date.isBefore(LocalDate.parse(m.createdDate))) return false; } catch (Exception ignored) {}\n        }\n        int bit = date.getDayOfWeek().getValue() - 1;\n        return (m.daysMask & (1 << bit)) != 0;\n    }\n\n    private static LocalDate inferLegacyCreatedDate(Context c, String medId) {\n        LocalDate earliest = null;\n        String prefix = "dose_rec_" + medId + "_";\n        for (String key : p(c).getAll().keySet()) {\n            if (!key.startsWith(prefix)) continue;\n            String tail = key.substring(prefix.length());\n            if (tail.length() < 10) continue;\n            try {\n                LocalDate d = LocalDate.parse(tail.substring(0, 10));\n                if (earliest == null || d.isBefore(earliest)) earliest = d;\n            } catch (Exception ignored) {}\n        }\n        return earliest == null ? LocalDate.now() : earliest;\n    }'''
if old not in s:
    raise SystemExit('MedicationStore isDayEnabled anchor missing')
s = s.replace(old, new, 1)
STORE.write_text(s, encoding='utf-8')

print('V3.0.3 medication registration-date patch applied')
