import json, os, re
from collections import OrderedDict

BOOK = json.load(open("/workspace/nla/book/nla_book_full.json"))
PAGES = BOOK["pages"]

LEVEL_STAGE = {
    "A1": {
        "stage": "Stage 1 — Pre-speech & First Words (linguistic age 0–18 months)",
        "teacher_role": "You are a caregiver narrating life. The child understands far more than he says. Expect silence, pointing, gaze, babble. Never demand speech.",
        "child_expected": "Watches your face and hands. Points. Reaches. May echo a final word after many repetitions (e.g. 'hot!').",
        "speech_style": "Parentese: short sentences, slow, musical, exaggerated intonation, lots of repetition. One idea per sentence.",
        "ar_stage": "المرحلة الأولى — ما قبل الكلام وأول الكلمات (عمر لغوي 0–18 شهرًا)",
        "ar_teacher_role": "أنت مُربٍّ يروي الحياة بصوت عالٍ. الطفل يفهم أكثر بكثير مما ينطق. توقّع الصمت والإشارة والنظر والتلبّغ. لا تطلب الكلام أبدًا.",
        "ar_child_expected": "يراقب وجهك ويديك. يشير. يتمطّى نحو الشيء. قد يردد آخر كلمة بعد تكرارات كثيرة (مثل: hot!).",
        "ar_speech_style": "لغة الأمهات: جمل قصيرة، بطيئة، موسيقية، نبرة مبالغة فيها، تكرار كثير. فكرة واحدة لكل جملة.",
    },
    "A2": {
        "stage": "Stage 2 — Toddler Talk (linguistic age 18 months–3 years)",
        "teacher_role": "You are a caregiver expanding the child's world: the city, the market, yesterday and tomorrow. You ask simple questions and wait. When the child answers with one or two words, you expand it naturally into a full sentence and move on.",
        "child_expected": "Says single words and two-word combos ('more juice', 'go bus!'). Answers 'what/where' questions with a word or gesture.",
        "speech_style": "Natural but still slow. Use expansions: child says 'Bus!' — you say 'Yes, the bus is coming!'",
        "ar_stage": "المرحلة الثانية — كلام الطفل سائرًا (عمر لغوي 18 شهرًا–3 سنوات)",
        "ar_teacher_role": "أنت مُربٍّ يوسّع عالم الطفل: المدينة والسوق وأمس وغدًا. اسأل أسئلة بسيطة وانتظر. حين يجيب بكلمة أو كلمتين، وسّعها أنت إلى جملة كاملة بشكل طبيعي وواصل.",
        "ar_child_expected": "ينطق كلمات مفردة وتركيبات من كلمتين (more juice / go bus). يجيب عن أسئلة ماذا وأين بكلمة أو بإشارة.",
        "ar_speech_style": "طبيعي لكن ما زال بطيئًا. استخدم التوسيع: يقول الطفل Bus! تقول أنت: Yes, the bus is coming!",
    },
    "B1": {
        "stage": "Stage 3 — The Narrating Child (linguistic age 4–8 years)",
        "teacher_role": "You are a parent of a school-age storyteller. The child now tells you about his day, his past, his plans and opinions. You listen like parents do: with real questions, real reactions, and gentle recasts instead of corrections.",
        "child_expected": "Speaks in full sentences. Tells simple stories. Gives opinions and reasons. Makes mistakes — that is the engine of growth.",
        "speech_style": "Completely natural adult speech. Your job is rich response, not correction.",
        "ar_stage": "المرحلة الثالثة — الطفل الحَكّاء (عمر لغوي 4–8 سنوات)",
        "ar_teacher_role": "أنت والدُ طفلٍ في سن المدرسة يحكي قصصه. صار يحكي يومه وماضيه وخططه وآراءه. أنصت كما يُنصت الآباء: بأسئلة حقيقية وتفاعل حقيقي، وبإعادة صياغة لطيفة بدل التصحيح.",
        "ar_child_expected": "يتكلم بجمل كاملة. يحكي قصصًا بسيطة. يرى آراءً وأسبابًا. يخطئ — والخطأ هو محرّك النمو.",
        "ar_speech_style": "كلام البالغين الطبيعي تمامًا. مهمتك الاستجابة الغنية لا التصحيح.",
    },
    "B2": {
        "stage": "Stage 4 — The Fluent Adolescent (linguistic age 9+ to adult fluency)",
        "teacher_role": "You are a mentor talking with a near-fluent speaker. Treat the child as an intellectual equal: humor, debate, professional scenarios, idiom-rich conversation. Push registers: formal, playful, sarcastic, diplomatic.",
        "child_expected": "Holds his own in any conversation. Understands jokes, irony, understatement. Argues positions with nuance.",
        "speech_style": "Authentic native speech at native speed, including hesitation markers, idioms, and cultural references.",
        "ar_stage": "المرحلة الرابعة — المراهق الطليق (عمر لغوي 9+ حتى طلاقة البالغ)",
        "ar_teacher_role": "أنت مرشدٌ تحاور شبه طليقًا. عامل الطفل كمثيل فكري: فكاهة ونقاش ومواقف مهنية وحديث غني بالمصطلحات. ادفع نحو مستويات اللغة: الرسمية والمرحة والساخرة والدبلوماسية.",
        "ar_child_expected": "يصمد في أي حوار. يفهم النكتة والسخرية والتقليل. يدافع عن مواقف ببراعة ودقة.",
        "ar_speech_style": "كلام أصلي أصيل بالسرعة الأصلية، بعلامات التردد والمصطلحات والمرجعيات الثقافية.",
    },
}

AR_NO_TRANSLATION = {
    "A1": "ممنوع الترجمة نهائيًا: اربط الكلمة بالشيء والفعل والتجربة نفسها أمام عينيه. الصورة والصوت واللمس هي القاموس.",
    "A2": "لا تترجم: إذا لم يفهم، أعد الجملة مع مشهد أقوى (إيماءة، صوت، حركة) لا مع ترجمة عربية.",
    "B1": "لا تترجم: أعد الصياغة بإنجليزية أبسط أو اطلب منه أن يريك بالفعل ما عنده في ذهنه.",
    "B2": "لا تترجم: استخدم التعريف بالإنجليزية والمقارنات والمواقف. السياق الثقافي نفسه جزء من الدرس.",
}

AR_WAIT = {
    "A1": "بعد كل جملة اصمت 3–5 ثوانٍ وانظر في عينيه. أي حركة أو صوت منه = تفاعل ناجح، كافئه بابتسامة وتكرار الجملة.",
    "A2": "بعد السؤال اصمت 5 ثوانٍ كاملة. أي كلمة واحدة منه = نجاح كبير. وسّعها أنت إلى الجملة الكاملة بفرح واضح.",
    "B1": "بعد سؤالك اصمت دون قلق. دعه يبني جملته كاملة حتى وإن تلعثم. التلعثم جزء من البناء.",
    "B2": "اترك له مساحة كاملة ليبني موقفه. لا تملأ الصمت. الجدل الهادئ معك هو الدرس نفسه.",
}

AR_RECAST = {
    "A1": "إذا نطق كلمة بشكل غير صحيح، لا تصحح: أعد أنت الكلمة الصحيحة بابتسامة في سياق جديد، وكأنك تؤكدها لا تعترض.",
    "A2": "صحح بالإعادة (recast): يقول 'Bus go!' فتقول بدهشة سعيدة 'Yes! The bus is going!' — دون أن تقل 'خطأ' أو 'لا'.",
    "B1": "صحح بالإعادة ضمن ردك الطبيعي: أعد جملته صحيحة وأنت تجيب عليه، فسمعها صحيحة دون أن يشعر بالتصحيح.",
    "B2": "تجاهل الأخطاء الصغيرة، وأعد الصياغة فقط حين يغيّر الخطأ المعنى. ركّز طاقتك على إدخال التعبيرات الأصيلة.",
}

AR_RITUAL = "اختم كل حلقة بنفس طقس الوداع (نفس الجملة ونفس الإيماءة) ليصبح أمانًا متوقعًا يفتح باب الاستقبال في الحلقة القادمة."

GOLDEN_RULE_AR = "القاعدة الذهبية — صفر مجهود: لا تطلب من الطفل أن يكرر، لا تقل له 'قل' أو 'جرب' أو 'قول معايا'. أنت تتكلم وتعمل، وهو يكتسب. الكلام سيخرج من وحده حين يجهز، تمامًا كما خرجت لغته الأولى."

AR_LADDER = "البناء التراكمي يحدث وحده: ستسمعه يقول الكلمة المفردة أولًا، بعد أسابيع كلمة+كلمة، ثم الجملة الكاملة. لا تقفز به خطوة — أكمل أنت الجملة الناقصة بابتسامة وواصل (التوسيع)، ولا تطلب منه إكمالها."

def ladder_for(lines):
    key = next((l for l in lines if l.strip().endswith("?")), lines[0])
    qmark = key.strip().endswith("?")
    words = re.sub(r"[^\w' ]", "", key).split()
    words = [w for w in words if w.lower() not in ("is", "are", "the", "a", "an", "do", "does", "can", "you", "i", "it")]
    word = words[-1] if words else key
    combo = " ".join(words[-2:]) if len(words) >= 2 else word
    end = "?" if qmark else "!"
    return {"1_single_word": word + end, "2_two_words": combo + end, "3_full_sentence": key,
             "note_ar": "هذا هو السلّم التلقائي: الكلمة ← كلمتان ← الجملة. يظهر من وحده مع الأسابيع — لا تتدرّب عليه ولا تختبره فيه أبدًا."}

def prev_module_lines(mod, by_module):
    for m in range(mod - 1, 0, -1):
        ps = by_module.get(m)
        if ps:
            return ps[:2]
    return None

def beats_for(p, unit_lines, dlg, kind, recall_lines):
    b = []
    b.append({
        "t": "0:00–0:30", "beat": "Greeting ritual",
        "camera": "Close on teacher's face, then tilt to include the child. Warm eye contact.",
        "action": "Teacher enters the scene with the same opening ritual every episode.",
        "audio": [{"who": "Teacher", "line": "Hello hello! Look, look! It's time."}],
        "sfx": "Soft, cheerful. Same intro jingle each episode.",
    })
    b.append({
        "t": "0:30–2:00", "beat": "Scene immersion — show, don't tell",
        "camera": "Wide shot of the full scene, then slow push-in on each key object as it is named.",
        "action": "Teacher physically points to and touches each object/action as it is named. Each line three times: slow, slower, natural. Child watches or joins. No requests, no 'say it'.",
        "audio": [{"who": "Teacher", "line": f"{l}  ·  {l}  ·  {l}"} for l in unit_lines[:2]],
        "sfx": "Real ambient sounds of the scene (traffic, kettle, market).",
    })
    if kind == "core":
        b.append({
            "t": "2:00–4:30", "beat": "Live dialogue — teacher plays both roles with the child",
            "camera": "Over-the-shoulder alternates; keep both faces in frame for reactions.",
            "action": "Teacher speaks line A to the child with gesture. Waits 5 seconds — silently. If the child offers anything, expand it joyfully. Then teacher voices B with a puppet/second voice. Replay the exchange once more with roles swapped.",
            "audio": [{"who": d["speaker"], "line": d["line"], "gesture": d.get("gesture", "")} for d in dlg],
            "sfx": "None. Faces and voices carry everything.",
        })
    elif kind == "shadow":
        b.append({
            "t": "2:00–4:30", "beat": "Echo & shadow play (pure imitation game, never a task)",
            "camera": "Full-body teacher shot so mouth, hands and body are all visible.",
            "action": "Teacher says each line twice: once slow with huge mouth movements, once natural. If the child shadows, wonderful; if not, the teacher simply continues, delighted either way.",
            "audio": [{"who": "Teacher", "line": f"{l}  ...  {l}"} for l in unit_lines],
            "sfx": "Optional light rhythm under the second pass.",
        })
    elif kind == "your_turn":
        b.append({
            "t": "2:00–4:30", "beat": "Silent invitation (no production ever required)",
            "camera": "Tight on teacher's expectant face during the pause — warm, patient, zero pressure.",
            "action": "Teacher asks, then holds a real 5-second silence with bright eyes and raised eyebrows. Whether the child answers or not, the teacher then completes the answer himself, warmly, as if the child had asked him to. Any sound the child makes is celebrated but never requested.",
            "audio": [{"who": "Teacher (asks, then waits 5s)", "line": dlg[0]["line"]},
                       {"who": "(silence — the child may or may not attempt; both are perfect)", "line": "…"},
                       {"who": "Teacher (completes warmly)", "line": dlg[-1]["line"]}],
            "sfx": "A tiny 'sparkle' cue only if the child initiates anything.",
        })
    else:
        b.append({
            "t": "2:00–4:30", "beat": "Old lines, new scene",
            "camera": "Cut between quick inserts of earlier episodes and the live scene.",
            "action": "Teacher opens with familiar lines from earlier modules (spiral), then lands them into today's new scene. The child feels 'I know this!' — that safety is the goal.",
            "audio": [{"who": "Teacher", "line": l} for l in unit_lines],
            "sfx": "Soft 'you know this!' chime on each familiar line.",
        })
    b.append({
        "t": "4:30–5:30", "beat": "Action & touch — the body learns",
        "camera": "Floor-level wide: both bodies moving in the scene.",
        "action": "Teacher acts out every line physically (picks up, pours, points, walks, mimes) and gently guides the child's hands through the same action. Language rides on movement.",
        "audio": [{"who": "Teacher", "line": unit_lines[1] if len(unit_lines) > 1 else unit_lines[0]}, {"who": "Teacher", "line": unit_lines[0]}],
        "sfx": "Real object sounds (cup set down, door, water).",
    })
    b.append({
        "t": "5:30–7:00", "beat": "Variation & free play (child leads, teacher expands)",
        "camera": "Handheld, playful. When the child initiates anything, the camera follows HIM.",
        "action": "Teacher changes one variable (color, size, person) and re-uses today's lines. If the child produces a word or fragment, the teacher expands it into the full sentence with visible joy — and never asks him to repeat the expanded version.",
        "audio": [{"who": "Teacher", "line": unit_lines[2] if len(unit_lines) > 2 else unit_lines[0]}],
        "sfx": "Natural room tone.",
    })
    if recall_lines:
        b.append({
            "t": "7:00–8:30", "beat": "Spiral recall — yesterday's lines inside today's world",
            "camera": "Same framing as the immersion beat; inserts of the earlier episode allowed.",
            "action": "Teacher weaves lines the child already owns into today's scene, casually, as if remembering them together. Zero testing — pure recognition pleasure.",
            "audio": [{"who": "Teacher", "line": l} for l in recall_lines],
            "sfx": "Gentle 'remember this?' musical tag.",
        })
    b.append({
        "t": "8:30–9:30", "beat": "Quiet wind-down",
        "camera": "Slow push-in. Soft light if possible.",
        "action": "Teacher repeats today's first line once, very softly, while both settle down. The line now belongs to the calm.",
        "audio": [{"who": "Teacher", "line": unit_lines[0]}],
        "sfx": "Ambient only, quieter.",
    })
    b.append({
        "t": "9:30–10:00", "beat": "Closing ritual (same every episode)",
        "camera": "Return to the opening framing. Slow, calm.",
        "action": "Same goodbye words and same gesture every time, then a quiet moment together.",
        "audio": [{"who": "Teacher", "line": "That's all for today. Bye bye, see you next time!"}],
        "sfx": "Same outro jingle each episode.",
    })
    return b

def notes_for(p, unit_lines, dlg, kind):
    lvl = p["level"]
    q = next((d["line"] for d in dlg if d["line"].strip().endswith("?")), dlg[0]["line"])
    new = ", ".join(p.get("spiral", {}).get("new_elements", [])) or unit_lines[-1]
    kind_note = {
        "shadow": "التظليل هنا لعبة تقليد طبيعية لا واجب نطق — إن لم يقلد فلا شيء، أنت وحدك تكمل بفرح.",
        "your_turn": "الدعوة صامتة: الصمت المنتظر هو جوهر الحلقة، وأنت من يكمل الإجابة دائمًا بعد الانتظار سواء نطق هو أم لا.",
        "spiral": "ابدأ بجمل مألوفة من حلقات سابقة قبل الجديد حتى يشعر بأمان «أنا أعرف هذا».",
        "core": "الأسماء والأفعال أمام عينيه أهم من أي شرح.",
    }[kind]
    return [
        GOLDEN_RULE_AR,
        AR_LADDER,
        f"جهّز المشهد قبل بدء التصوير: {p['visual_scene']}. الأهم أن الطفل يرى الأشياء الحقيقية والفعل الحقيقي، لا صورًا فقط.",
        f"انطق ببطء مع الإيماءة: «{unit_lines[0]}» — كررها ثلاث مرات قبل الانتقال لأي جملة جديدة. الهدف أن تسمع أذنه نفس النمط حتى يتنبأ به.",
        f"عنصر اليوم الجديد (15%): {new}. قدّمه وحده أولًا مرتين، ثم ادمجه في الجمل. لا تقدم أكثر من عنصر جديد واحد في الجلسة.",
        f"بعد سؤال «{q}» اصمت وانظر بترقّب. {AR_WAIT[lvl]}",
        AR_NO_TRANSLATION[lvl],
        AR_RECAST[lvl],
        f"نوع هذه الحلقة: {kind_note}",
        f"الحلقة 10 دقائق مقسّمة ثماني مشاهد زمنية — التزم بالمدد خاصة الصمت (5 ثوانٍ كاملة) وطقس الافتتاح والختام.",
        AR_RITUAL,
    ]

def kind_of(title):
    if "Listen & Shadow" in title:
        return "shadow"
    if "Your Turn" in title:
        return "your_turn"
    if "Spiral Review" in title:
        return "spiral"
    return "core"

by_module = OrderedDict()
for p in PAGES:
    by_module.setdefault(p["module"], []).append(p)

count = 0
episodes = []
per_module = {}
for mod, ps in by_module.items():
    distinct = []
    for p in ps:
        if p["title"] not in distinct:
            distinct.append(p["title"])
    bases = distinct[:8]
    alts = distinct[8:16]
    for idx, t in enumerate(bases):
        p = next(q for q in ps if q["title"] == t)
        kind = kind_of(t)
        alt_p = next((q for q in ps if q["title"] == alts[idx]), None) if idx < len(alts) else None
        count += 1
        lvl = p["level"]
        st = LEVEL_STAGE[lvl]
        dlg = p["dialogue"]
        recall = prev_module_lines(mod, by_module)
        ep = OrderedDict()
        ep["episode"] = count
        ep["level"] = lvl
        ep["module"] = mod
        ep["module_title"] = p["module_title"]
        ep["title"] = t
        ep["kind"] = kind
        ep["source_page"] = p["page"]
        ep["duration"] = "10 minutes"
        ep["stage"] = {k: st[k] for k in ("stage", "teacher_role", "child_expected", "speech_style")}
        ep["stage_ar"] = {k: st["ar_" + k] for k in ("stage", "teacher_role", "child_expected", "speech_style")}
        ep["scene"] = {"setting": p["visual_scene"],
                        "characters": "The Teacher (caregiver) and the Child. One real location, real objects.",
                        "props": "Everything the scene names must be physically present."}
        if alt_p is not None:
            ep["replay_variation"] = {
                "when": "Re-shoot or re-watch this episode with the alternate scene after a few days — same lines, new world.",
                "setting": alt_p["visual_scene"],
                "lines": alt_p["natural_english"],
                "dialogue": alt_p["dialogue"],
            }
        ep["beats"] = beats_for(p, p["natural_english"], dlg, kind, recall)
        ep["ladder"] = ladder_for(p["natural_english"])
        ep["teacher_notes_ar"] = notes_for(p, p["natural_english"], dlg, kind)
        ep["zero_effort_rule"] = {
            "rule": "The child is never asked to produce anything. No 'repeat after me', no 'say it', no 'your turn'. The teacher models; the child acquires. Speech emerges on its own: single word → two words → full sentence.",
            "rule_ar": "لا يُطلب من الطفل أي إنتاج إطلاقًا: لا 'كرر معي'، لا 'قل'، لا 'دورك'. أنت نمذج وهو يكتسب. الكلام يخرج وحده: كلمة ← كلمتان ← جملة كاملة.",
            "if_child_speaks": "Celebrate warmly, expand his words into the full sentence yourself, and move on. Never ask him to repeat the expansion.",
            "if_child_silent": "Perfectly fine. Silence is acquisition in progress. Complete the line yourself and continue naturally.",
        }
        ep["success_signs"] = {
            "A1": "The child watches your face, points, reaches, or babbles. Comprehension signs only — any spoken word is a bonus, never a goal.",
            "A2": "The child engages with the scene and may offer a word or two spontaneously. You expand it; he owes you nothing.",
            "B1": "The child begins narrating on his own initiative. Full sentences appear without ever being assigned.",
            "B2": "The child holds natural exchanges and argues points because he wants to, not because he is asked.",
        }[lvl]
        episodes.append(ep)
        per_module.setdefault(mod, []).append(ep)

os.makedirs("/workspace/nla/book/video", exist_ok=True)
with open("/workspace/nla/book/video/video_scripts_full.json", "w", encoding="utf-8") as f:
    json.dump({"course": "Natural English Acquisition — Zero to B2 (Video Edition)",
                "format": "136 episodes × 10 minutes: Teacher + Child, real scenes, Arabic notes for the teacher only, zero-effort acquisition, cumulative ladder",
                "episodes": episodes}, f, ensure_ascii=False, indent=1)
for mod, eps in per_module.items():
    with open(f"/workspace/nla/book/video/video_scripts_module_{mod:02d}.json", "w", encoding="utf-8") as f:
        json.dump({"module": mod, "module_title": eps[0]["module_title"], "level": eps[0]["level"],
                    "episodes": eps}, f, ensure_ascii=False, indent=1)
print("OK:", count, "episodes across", len(per_module), "modules")
