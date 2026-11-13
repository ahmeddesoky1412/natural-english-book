# -*- coding: utf-8 -*-
"""Builds the full 600-page NLA book as JSON with TTS-ready audio scripts."""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_a1_a2 import A1, A2
from content_b1_b2 import B1, B2
from content_alts_1 import ALTS_1
from content_alts_2 import ALTS_2

CONTENT = {**A1, **A2, **B1, **B2}
ALTS = {**ALTS_1, **ALTS_2}
for m, units in CONTENT.items():
    alts = ALTS.get(m, [])
    assert len(alts) == len(units), f"module {m}: {len(units)} units but {len(alts)} alts"

def unit_pair(module_no, idx):
    """Return (base, alt) content for a unit index."""
    return CONTENT[module_no][idx], ALTS[module_no][idx]

MODULE_META = [
    (1,  "A1", "Presence & Environment",            15),
    (2,  "A1", "The Human Body & Basic Actions",    20),
    (3,  "A1", "Home & Daily Life",                 25),
    (4,  "A1", "Family & Immediate Relationships",  20),
    (5,  "A1", "Basic Interactions & Survival English", 20),
    (6,  "A2", "Daily Routines & Habits",           30),
    (7,  "A2", "The City & Navigation",             30),
    (8,  "A2", "Commerce & Markets",                30),
    (9,  "A2", "Past Experiences & Simple Futures", 30),
    (10, "B1", "Personal History & Storytelling",   40),
    (11, "B1", "Work, Study & Ambitions",           40),
    (12, "B1", "Relationships, Opinions & Feelings",40),
    (13, "B1", "Troubleshooting & Navigation of Problems", 40),
    (14, "B2", "Social Nuance & Cultural Context",  45),
    (15, "B2", "Professional Communication",        50),
    (16, "B2", "Abstract Concepts & Debates",       55),
    (17, "B2", "Authentic Idiomatic English",       70),
]

PACING = {
    "A1": "slow and clear, ~120 wpm, full articulation, gentle pauses between lines",
    "A2": "relaxed natural pace, ~140 wpm, light contractions, brief natural pauses",
    "B1": "conversational pace, ~160 wpm, natural contractions, occasional hesitation",
    "B2": "authentic conversational pace, ~175 wpm, full contractions, hesitations and self-corrections welcome",
}

CONTRACTION_NOTES = {
    "A1": "Pronounce 'it is' fully; introduce 'it's' only in the dialogue voice.",
    "A2": "Use common contractions: I'm, don't, it's, can't.",
    "B1": "Use contractions freely; allow one hesitation marker ('well', 'hmm') before opinions.",
    "B2": "Fully natural speech: gonna/wanna acceptable in dialogue, fillers ('you know', 'I mean') permitted.",
}

VARIANT_KINDS = ["core", "shadow", "your_turn", "spiral"]


def previous_lines(level, module, k=2):
    """Pull review lines from earlier modules (the 85% familiar input)."""
    pool = []
    for m, lv, _, _ in MODULE_META:
        if m < module and lv == level or (m < module and lv != level):
            for u in CONTENT.get(m, []):
                pool.append(u["lines"][-1])
    if not pool:
        return []
    step = max(1, len(pool) // max(k, 1))
    return [pool[(module * 3 + i * step) % len(pool)] for i in range(k)]


def make_audio_script(unit, kind, level):
    v1_lines = list(unit["lines"])
    voices = [{"role": "Voice 1 — narrator / Speaker A", "lines": []},
              {"role": "Voice 2 — conversation partner / Speaker B", "lines": []}]
    if kind == "shadow":
        voices[0]["lines"] = v1_lines
        voices[1]["lines"] = [d[1] for d in unit["dialogue"]]
        direction = ("Voice 1 reads each line, then repeats it once slower. "
                     "Voice 2 enters only in the dialogue section. Listener shadows each line aloud.")
    elif kind == "your_turn":
        voices[0]["lines"] = v1_lines[:2]
        voices[1]["lines"] = [d[1] for d in unit["dialogue"]]
        direction = ("Voice 1 speaks; Voice 2's lines are replaced by a 3-second silent slot "
                     "for the listener to answer aloud, then Voice 2 models the answer.")
    elif kind == "spiral":
        voices[0]["lines"] = previous_lines(level, unit["_module"]) + v1_lines[-2:]
        voices[1]["lines"] = [d[1] for d in unit["dialogue"][:2]]
        direction = ("Review-first flow: familiar lines from earlier modules, then this page's new "
                     "element woven in at the end. Keep energy warm, like revision, not testing.")
    else:
        voices[0]["lines"] = v1_lines
        voices[1]["lines"] = [d[1] for d in unit["dialogue"]]
        direction = ("Voice 1 narrates the scene lines with a beat between each. "
                     "Voice 2 performs the dialogue naturally.")
    for v in voices:
        v["lines"] = [l for l in v["lines"] if l]
    return {
        "pacing": PACING[level],
        "contractions": CONTRACTION_NOTES[level],
        "direction": direction,
        "voices": [v for v in voices if v["lines"]],
    }


def build_page(page_no, level, module_no, module_title, unit, kind, occurrence):
    title_suffix = {"core": "", "shadow": " — Listen & Shadow",
                    "your_turn": " — Your Turn", "spiral": " — Spiral Review"}[kind]
    if occurrence > 0:
        title_suffix += f" ({occurrence + 1})"
    dialogue = []
    for spk, line, gesture in unit["dialogue"]:
        if kind == "your_turn" and spk == "B":
            dialogue.append({"speaker": "B (you)", "line": "… (respond aloud)", "gesture": ""})
            dialogue.append({"speaker": "B (model)", "line": line, "gesture": gesture})
        else:
            dialogue.append({"speaker": spk, "line": line, "gesture": gesture})
    lines = list(unit["lines"])
    if kind == "spiral":
        review = previous_lines(level, module_no)
        if review:
            lines = review + lines[-2:]
    return {
        "page": page_no,
        "level": level,
        "module": module_no,
        "module_title": module_title,
        "title": unit["title"] + title_suffix,
        "visual_scene": unit["scene"],
        "natural_english": lines,
        "dialogue": dialogue,
        "audio_script": make_audio_script({**unit, "_module": module_no}, kind, level),
        "spiral": {
            "familiar_pct": 85,
            "new_pct": 15,
            "new_elements": [unit["new"]],
        },
    }


def build():
    pages = []
    page_no = 1
    for module_no, level, title, count in MODULE_META:
        n_units = len(CONTENT[module_no])
        counters = {}
        for i in range(count):
            idx = i % n_units
            base, alt = unit_pair(module_no, idx)
            occ = counters.get((module_no, idx), 0)
            counters[(module_no, idx)] = occ + 1
            unit = base if occ % 2 == 0 else alt
            kind = VARIANT_KINDS[i % 4] if count > n_units else "core"
            pages.append(build_page(page_no, level, module_no, title, unit, kind, occ))
            page_no += 1
    return pages


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book")
    os.makedirs(out_dir, exist_ok=True)
    pages = build()
    assert len(pages) == 600, f"expected 600 pages, got {len(pages)}"
    assert [p["page"] for p in pages] == list(range(1, 601)), "page numbering broken"
    with open(os.path.join(out_dir, "nla_book_full.json"), "w", encoding="utf-8") as f:
        json.dump({"title": "Natural English Acquisition — Zero to B2",
                   "audience": "Arabic speakers, zero-translation input method",
                   "total_pages": 600, "pages": pages}, f, ensure_ascii=False, indent=2)
    by_level = {}
    for p in pages:
        by_level.setdefault(p["level"], []).append(p)
    for lv, ps in by_level.items():
        with open(os.path.join(out_dir, f"level_{lv}.json"), "w", encoding="utf-8") as f:
            json.dump({"level": lv, "pages": len(ps), "content": ps}, f, ensure_ascii=False, indent=2)
    manifest = [{"level": lv, "modules": sorted({p["module"] for p in ps}),
                 "page_range": [ps[0]["page"], ps[-1]["page"]], "pages": len(ps)}
                for lv, ps in by_level.items()]
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(pages)} pages written to {out_dir}")
    for m in manifest:
        print(f"  {m['level']}: pages {m['page_range'][0]}-{m['page_range'][1]} ({m['pages']} pages), modules {m['modules']}")


if __name__ == "__main__":
    main()
