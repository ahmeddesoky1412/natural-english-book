import json, time
from fpdf import FPDF
from fpdf.enums import XPos, YPos
NX = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)

BOOK = json.load(open("/workspace/nla/book/nla_book_full.json"))
PAGES = BOOK["pages"]
F = "/workspace/nla/fonts/"

class Book(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.add_font("NotoSans", "", F + "NotoSans-Regular.ttf")
        self.add_font("NotoSans", "B", F + "NotoSans-Bold.ttf")
        self.add_font("NotoSans", "I", F + "NotoSans-Italic.ttf")
        self.add_font("Naskh", "", F + "NotoNaskhArabic-Regular.ttf")
        self.add_font("Naskh", "B", F + "NotoNaskhArabic-Bold.ttf")
        self.set_text_shaping(False)
        self.set_auto_page_break(auto=True, margin=16)
        self.set_margins(15, 14, 15)

    def header(self):
        if self.page_no() <= 2:
            return
        self.set_text_shaping(False)
        self.set_font("NotoSans", "", 7.5)
        self.set_text_color(130)
        self.cell(0, 5, "Natural English Acquisition — Zero to B2", align="L")
        self.cell(0, 5, f"Page {self.page_no()}", align="R")
        self.ln(7)
        self.set_draw_color(200)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def footer(self):
        if self.page_no() <= 2:
            return
        self.set_y(-12)
        self.set_font("NotoSans", "", 7.5)
        self.set_text_color(150)
        self.cell(0, 5, str(self.page_no()), align="C")

    def ar(self, txt, size=11, style="", align="R", h=7):
        self.set_text_shaping(True)
        self.set_font("Naskh", style, size)
        self.multi_cell(0, h, txt, align=align, **NX)
        self.set_text_shaping(False)

    def en(self, txt, size=9.5, style="", h=5.2):
        self.set_text_shaping(False)
        self.set_font("NotoSans", style, size)
        self.multi_cell(0, h, txt, **NX)

    def label(self, txt):
        self.set_text_shaping(False)
        self.set_font("NotoSans", "B", 8.5)
        self.set_text_color(190, 90, 30)
        self.cell(0, 5, txt, align="L")
        self.ln(5.4)

pdf = Book()
pdf.set_title("Natural English Acquisition — Zero to B2")
pdf.set_author("NLA Curriculum")

t0 = time.time()

# ---------- COVER ----------
pdf.add_page()
pdf.ln(30)
pdf.set_text_shaping(False)
pdf.set_font("NotoSans", "B", 26)
pdf.set_text_color(30, 30, 30)
pdf.multi_cell(0, 11, "Natural English Acquisition", align="C", **NX)
pdf.set_font("NotoSans", "", 15)
pdf.set_text_color(190, 90, 30)
pdf.multi_cell(0, 9, "Zero to B2", align="C", **NX)
pdf.ln(6)
pdf.set_font("NotoSans", "", 10)
pdf.set_text_color(80)
pdf.multi_cell(0, 6, "A Natural Language Acquisition (NLA) Curriculum for Arabic Speakers\n600 Pages · 17 Modules · 4 Levels (A1 › A2 › B1 › B2)", align="C", **NX)
pdf.ln(10)
pdf.set_font("NotoSans", "I", 9.5)
pdf.multi_cell(0, 6, "No translation · No grammar drills · No memorization\nMeaning through imagery, context, gesture, and sound", align="C", **NX)
pdf.ln(14)
pdf.ar("منحنى اكتساب طبيعي للناطقين بالعربية — من الصفر إلى الطلاقة العملية", size=12)
pdf.ar("الاستماع أولًا · الصورة تُثبّت المعنى · 85% مألوف و15% جديد في كل صفحة", size=10.5)
pdf.ln(20)
pdf.set_text_shaping(False)
pdf.set_font("NotoSans", "", 9)
pdf.set_text_color(120)
pdf.multi_cell(0, 6, "Every page contains:\nA. Visual Scene   B. Natural English   C. Real-Life Dialogue   D. Audio Script (TTS-ready, **NX)", align="C")

# ---------- TOC ----------
pdf.add_page()
pdf.ln(4)
pdf.set_font("NotoSans", "B", 15)
pdf.set_text_color(30)
pdf.cell(0, 9, "Table of Contents", align="C")
pdf.ln(11)
toc = [
    ("LEVEL A1 — THE IMMEDIATE WORLD", "Pages 1–100", None),
    ("Module 1 · Presence & Environment", "Pages 1–15", 1),
    ("Module 2 · The Human Body & Basic Actions", "Pages 16–35", 2),
    ("Module 3 · Home & Daily Life", "Pages 36–60", 3),
    ("Module 4 · Family & Immediate Relationships", "Pages 61–80", 4),
    ("Module 5 · Basic Interactions & Survival English", "Pages 81–100", 5),
    ("LEVEL A2 — MOVEMENT & ROUTINE", "Pages 101–220", None),
    ("Module 6 · Daily Routines & Habits", "Pages 101–130", 6),
    ("Module 7 · The City & Navigation", "Pages 131–160", 7),
    ("Module 8 · Commerce & Markets", "Pages 161–190", 8),
    ("Module 9 · Past Experiences & Simple Futures", "Pages 191–220", 9),
    ("LEVEL B1 — NARRATIVE & INDEPENDENCE", "Pages 221–380", None),
    ("Module 10 · Personal History & Storytelling", "Pages 221–260", 10),
    ("Module 11 · Work, Study & Ambitions", "Pages 261–300", 11),
    ("Module 12 · Relationships, Opinions & Feelings", "Pages 301–340", 12),
    ("Module 13 · Troubleshooting & Navigation of Problems", "Pages 341–380", 13),
    ("LEVEL B2 — FLUIDITY & ABSTRACTION", "Pages 381–600", None),
    ("Module 14 · Social Nuance & Cultural Context", "Pages 381–425", 14),
    ("Module 15 · Professional Communication", "Pages 426–475", 15),
    ("Module 16 · Abstract Concepts & Debates", "Pages 476–530", 16),
    ("Module 17 · Authentic Idiomatic English", "Pages 531–600", 17),
]
for title, rng, mod in toc:
    if mod is None:
        pdf.ln(2.5)
        pdf.set_font("NotoSans", "B", 10.5)
        pdf.set_text_color(190, 90, 30)
        pdf.cell(150, 6.5, title)
        pdf.set_font("NotoSans", "", 9)
        pdf.set_text_color(100)
        pdf.cell(0, 6.5, rng, align="R")
        pdf.ln(7.5)
    else:
        pdf.set_font("NotoSans", "", 9.5)
        pdf.set_text_color(50)
        pdf.cell(150, 6, "    " + title)
        pdf.set_font("NotoSans", "", 8.5)
        pdf.set_text_color(110)
        pdf.cell(0, 6, rng, align="R")
        pdf.ln(6.6)

# ---------- LEVEL DIVIDERS ----------
seen_levels = set()

def level_divider(lvl, title, p1, p2, ar_txt):
    pdf.add_page()
    pdf.ln(70)
    pdf.set_text_shaping(False)
    pdf.set_font("NotoSans", "B", 30)
    pdf.set_text_color(190, 90, 30)
    pdf.multi_cell(0, 14, lvl, align="C", **NX)
    pdf.set_font("NotoSans", "", 14)
    pdf.set_text_color(60)
    pdf.multi_cell(0, 9, title, align="C", **NX)
    pdf.set_font("NotoSans", "", 11)
    pdf.set_text_color(120)
    pdf.multi_cell(0, 8, f"Pages {p1}–{p2}", align="C", **NX)
    pdf.ln(8)
    pdf.ar(ar_txt, size=11, align="C")

KINDS = {"core": "Core Scene", "shadow": "Listen & Shadow", "your_turn": "Your Turn", "spiral": "Spiral Review"}
for p in PAGES:
    lvl = p["level"]
    if lvl not in seen_levels:
        seen_levels.add(lvl)
        div = {
            "A1": ("LEVEL A1", "THE IMMEDIATE WORLD", 1, 100,
                   "العالم الفوري: الناس، الأشياء، الجسد، البيت، العائلة، وأول التفاعلات الحيّة"),
            "A2": ("LEVEL A2", "MOVEMENT & ROUTINE", 101, 220,
                   "الحركة والروتين: اليوم من الصباح للمساء، المدينة، السوق، والماضي والمستقبل"),
            "B1": ("LEVEL B1", "NARRATIVE & INDEPENDENCE", 221, 380,
                   "السرد والاستقلال: قصتك، عملك، آراؤك ومشاعرك، وحل مشاكلك بنفسك"),
            "B2": ("LEVEL B2", "FLUIDITY & ABSTRACTION", 381, 600,
                   "الطلاقة والتجريد: الفروق الدقيقة، الاحتراف، النقاشات الكبرى، والإنجليزية الاصطلاحية"),
        }[lvl]
        level_divider(*div)

    if p["page"] % 25 == 0:
        print(f"... page {p['page']}/600 ({time.time()-t0:.0f}s)", flush=True)

    pdf.add_page()
    kind = KINDS.get(p.get("kind", "core"), "Core Scene")
    pdf.set_text_shaping(False)
    pdf.set_font("NotoSans", "", 8)
    pdf.set_text_color(150)
    pdf.cell(120, 4.5, f"{lvl} · Module {p['module']}: {p['module_title']}")
    pdf.set_font("NotoSans", "B", 8)
    pdf.set_text_color(190, 90, 30)
    pdf.cell(0, 4.5, kind, align="R")
    pdf.ln(6.5)
    pdf.set_font("NotoSans", "B", 12.5)
    pdf.set_text_color(25)
    pdf.multi_cell(0, 7, f"Page {p['page']} — {p['title']}", **NX)
    pdf.ln(1)

    pdf.label("A. Visual Scene")
    pdf.set_text_color(60)
    pdf.en(p["visual_scene"], size=9.5, style="I")
    pdf.ln(1.5)

    pdf.label("B. Natural English")
    for line in p["natural_english"]:
        pdf.set_text_color(30)
        pdf.set_x(19)
        pdf.cell(4, 5.2, "•")
        pdf.set_x(23)
        pdf.en(f"\u201c{line}\u201d")
    pdf.ln(1.5)

    pdf.label("C. Real-Life Dialogue")
    for d in p["dialogue"]:
        speaker = d["speaker"]; line = d["line"]; g = d.get("gesture", "")
        pdf.set_text_color(30)
        pdf.set_x(19)
        pdf.set_font("NotoSans", "B", 9.5)
        pdf.cell(pdf.get_string_width(speaker) + 2.5, 5.2, speaker + ":")
        pdf.set_font("NotoSans", "", 9.5)
        txt = f"\u201c{line}\u201d"
        if g and "respond aloud" not in line:
            txt += f"   ({g})"
        pdf.multi_cell(0, 5.2, txt, **NX)
    pdf.ln(1.5)

    pdf.label("D. Audio Script")
    a = p["audio_script"]
    for v in a["voices"]:
        pdf.set_text_color(60)
        pdf.set_x(19)
        pdf.set_font("NotoSans", "B", 8.8)
        pdf.multi_cell(0, 4.8, v["role"] + ":", **NX)
        pdf.set_font("NotoSans", "", 8.8)
        for ln_ in v["lines"]:
            pdf.set_x(23)
            pdf.multi_cell(0, 4.8, ln_, **NX)
    pdf.set_text_color(120)
    pdf.set_font("NotoSans", "I", 8)
    pdf.set_x(19)
    pdf.multi_cell(0, 4.5, f"Pacing: {a['pacing']}  |  Contractions: {a['contractions']}", **NX)
    pdf.ln(1.5)

    sp = p.get("spiral", {})
    ne = ", ".join(sp.get("new_elements", []))
    pdf.label("+15% New in This Page")
    pdf.set_text_color(60)
    pdf.en(ne if ne else "—", size=9)

out = "/workspace/nla/book/Natural_English_Acquisition_Zero_to_B2.pdf"
pdf.output(out)
print(f"DONE in {time.time()-t0:.0f}s -> {out}")
import os
print("size:", os.path.getsize(out), "bytes")
