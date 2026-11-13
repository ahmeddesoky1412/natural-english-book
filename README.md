# Natural English Acquisition — Zero to B2

كتاب NLA كامل (600 صفحة) للناطقين بالعربية: من A0 إلى B2 — بدون ترجمة، بدون حفظ قواعد، بدون واجبات. كل صفحة تحمل: مشهدًا بصريًا، جملًا طبيعية، حوارًا واقعيًا مع الإيماءات، وسكربتًا صوتيًا جاهزًا لـ TTS.

## الملفات

| الملف | الوصف |
|---|---|
| `book/nla_book_full.json` | الكتاب كامل — 600 صفحة في ملف واحد |
| `book/level_A1.json` | المستوى A1 — الصفحات 1–100 (الموديولات 1–5) |
| `book/level_A2.json` | المستوى A2 — الصفحات 101–220 (الموديولات 6–9) |
| `book/level_B1.json` | المستوى B1 — الصفحات 221–380 (الموديولات 10–13) |
| `book/level_B2.json` | المستوى B2 — الصفحات 381–600 (الموديولات 14–17) |
| `book/manifest.json` | فهرس المستويات والموديولات |
| `build_book.py` | مولّد الكتاب (يعيد بناء الـ JSON من بنوك المحتوى) |
| `content_*.py` | بنوك المحتوى: 272 مشهدًا مؤلَّفًا + 136 مشهدًا بديلًا |

## بنية الصفحة (JSON)

```json
{
  "page": 131,
  "level": "A2",
  "module": 7,
  "title": "Where Is the Station?",
  "visual_scene": "...",
  "natural_english": ["..."],
  "dialogue": [{"speaker": "...", "line": "...", "gesture": "..."}],
  "audio_script": {"pacing": "...", "contractions": "...", "voices": [{"role": "...", "lines": ["..."]}]},
  "spiral": {"familiar_pct": 85, "new_pct": 15, "new_elements": ["..."]}
}
```

## إعادة البناء

```bash
python3 build_book.py
```

## التحميل

زر **Code** الأخضر أعلى الصفحة ← **Download ZIP**.
