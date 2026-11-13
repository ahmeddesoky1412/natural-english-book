import json, os, sys, subprocess, wave
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from piper import PiperVoice, SynthesisConfig
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
TTS = "/workspace/nla/tts"

V_AR = PiperVoice.load(f"{TTS}/ar_JO-kareem-medium.onnx")
V_EN = PiperVoice.load(f"{TTS}/en_US-amy-medium.onnx")
V_ST = PiperVoice.load(f"{TTS}/en_US-ryan-high.onnx")
CFG_AR = SynthesisConfig(length_scale=1.15)
CFG_EN = SynthesisConfig(length_scale=1.0)
CFG_ST = SynthesisConfig(length_scale=1.0)

W, H = 960, 540
FPS = 1
TOTAL = 600

BG = {"A1": (253, 246, 227), "A2": (227, 240, 252), "B1": (230, 246, 232), "B2": (240, 240, 245)}
ACCENT = {"A1": (180, 95, 30), "A2": (30, 100, 180), "B1": (40, 120, 70), "B2": (90, 80, 140)}

F_EN_B = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Bold.ttf", 56)
F_EN_M = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Bold.ttf", 38)
F_EN = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Regular.ttf", 30)
F_SM_B = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Bold.ttf", 24)
F_AR = ImageFont.truetype("/workspace/nla/fonts/NotoNaskhArabic-Regular.ttf", 30)
F_AR_B = ImageFont.truetype("/workspace/nla/fonts/NotoNaskhArabic-Bold.ttf", 44)
F_AR_M = ImageFont.truetype("/workspace/nla/fonts/NotoNaskhArabic-Regular.ttf", 34)

TR = json.load(open("/workspace/nla/translations_all.json"))
CONCEPTS = {e["ep"]: e for e in json.load(open("/workspace/nla/ep_concepts.json"))}

def ar_text(t):
    return get_display(arabic_reshaper.reshape(t))

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines

def draw_person(d, cx, cy, skin, shirt, hair, glasses, label, label_ar=True):
    d.rounded_rectangle([cx - 48, cy + 30, cx + 48, cy + 130], radius=22, fill=shirt)
    r = 36
    d.ellipse([cx - r, cy - r - 6, cx + r, cy + r - 6], fill=skin)
    d.pieslice([cx - r - 2, cy - r - 12, cx + r + 2, cy + r - 2], 180, 360, fill=hair)
    d.ellipse([cx - 15, cy - 8, cx - 7, cy], fill=(40, 40, 45))
    d.ellipse([cx + 7, cy - 8, cx + 15, cy], fill=(40, 40, 45))
    d.arc([cx - 12, cy + 2, cx + 12, cy + 18], 20, 160, fill=(120, 60, 50), width=3)
    if glasses:
        d.ellipse([cx - 20, cy - 13, cx - 3, cy + 4], outline=(30, 30, 35), width=3)
        d.ellipse([cx + 3, cy - 13, cx + 20, cy + 4], outline=(30, 30, 35), width=3)
        d.line([cx - 3, cy - 5, cx + 3, cy - 5], fill=(30, 30, 35), width=3)
    f = F_AR_M if label_ar else F_SM_B
    txt = ar_text(label) if label_ar else label
    tw = d.textlength(txt, font=f)
    d.text((cx - tw / 2, cy + 138), txt, font=f, fill=(60, 60, 70))

def bubble(d, x0, x1, y, text, ar=True):
    f = F_AR if ar else F_EN
    txt = ar_text(text) if ar else text
    lines = wrap(d, txt, f, x1 - x0 - 40)
    bh = len(lines) * 40 + 28
    d.rounded_rectangle([x0, y, x1, y + bh], radius=16, fill=(255, 255, 255), outline=(160, 160, 168), width=2)
    yy = y + 12
    for ln in lines:
        d.text((x0 + 22, yy), ln, font=f, fill=(35, 35, 42))
        yy += 40

def header(d, ep, level, module, title):
    acc = ACCENT[level]
    d.rectangle([0, 0, W, 64], fill=acc)
    ar_head = ar_text(f"الحلقة {ep} \u00b7 مستوى {level} \u00b7 الموديول {module}")
    d.text((W - 24 - d.textlength(ar_head, font=F_AR_M), 12), ar_head, font=F_AR_M, fill=(255, 255, 255))
    d.text((24, 18), title[:52], font=F_SM_B, fill=(255, 255, 255))

def concept_card(d, c, mode="full"):
    y = 300
    word = c["word"].capitalize()
    meaning = TR["words"].get(c["word"].lower(), "")
    ph_ar = TR["phrases"].get(c["phrase"].lower(), "")
    sent_ar = TR["sents"].get(c["sent"], "")
    if mode in ("full", "word"):
        d.text((W // 2 - d.textlength(word, font=F_EN_B) / 2, y), word, font=F_EN_B, fill=(35, 35, 40))
        y += 76
        if meaning:
            t = ar_text(meaning)
            d.text((W // 2 - d.textlength(t, font=F_AR_B) / 2, y), t, font=F_AR_B, fill=ACCENT[c["level"]])
            y += 70
    if mode == "full":
        if ph_ar and c["phrase"].lower() != c["word"].lower():
            t = ar_text(f"{c['phrase']}  =  {ph_ar}")
            for ln in wrap(d, t, F_AR_M, W - 140):
                d.text((W // 2 - d.textlength(ln, font=F_AR_M) / 2, y), ln, font=F_AR_M, fill=(80, 80, 90))
                y += 44
        y += 6
        for ln in wrap(d, c["sent"], F_EN_M, W - 140):
            d.text((W // 2 - d.textlength(ln, font=F_EN_M) / 2, y), ln, font=F_EN_M, fill=(45, 45, 55))
            y += 50
    elif mode == "recall":
        for ln in wrap(d, c["sent"], F_EN, W - 140):
            d.text((W // 2 - d.textlength(ln, font=F_EN) / 2, y), ln, font=F_EN, fill=(90, 90, 100))
            y += 40

TEACHER = dict(skin=(240, 200, 165), shirt=(70, 90, 160), hair=(50, 40, 35), glasses=True, label="الأستاذ كريم")
STUDENT = dict(skin=(250, 220, 190), shirt=(200, 90, 80), hair=(190, 150, 90), glasses=False, label="Jake")

def make_slide(ep, kind, speaker, spoken, concept, ep_meta, extra):
    level = ep_meta["level"]
    img = Image.new("RGB", (W, H), BG[level])
    d = ImageDraw.Draw(img)
    header(d, ep, level, ep_meta["module"], ep_meta["title"])
    if kind == "title":
        t = ar_text("الأستاذ كريم يعلم جيك الإنجليزية")
        d.text((W // 2 - d.textlength(t, font=F_AR_B) / 2, 130), t, font=F_AR_B, fill=(50, 50, 60))
        t2 = ar_text("استمع بهدوء \u2014 لا يُطلب منك أي مجهود")
        d.text((W // 2 - d.textlength(t2, font=F_AR_M) / 2, 210), t2, font=F_AR_M, fill=(110, 110, 120))
        if extra:
            yy = 290
            for wd in extra:
                wd = wd.capitalize()
                d.text((W // 2 - d.textlength(wd, font=F_EN_M) / 2, yy), wd, font=F_EN_M, fill=(45, 45, 55))
                yy += 52
    elif kind == "closing":
        t = ar_text("أحسنتم! إلى اللقاء في الحلقة القادمة")
        d.text((W // 2 - d.textlength(t, font=F_AR_B) / 2, 200), t, font=F_AR_B, fill=(50, 50, 60))
    else:
        if concept:
            concept_card(d, concept, mode=extra or "full")
    if kind in ("title", "closing", "card"):
        draw_person(d, 130, 130, **TEACHER)
        draw_person(d, 830, 130, **STUDENT, label_ar=False)
    else:
        if speaker == "teacher":
            draw_person(d, 130, 130, **TEACHER)
            bubble(d, 200, 930, 96, spoken, ar=True)
        else:
            draw_person(d, 830, 130, **STUDENT, label_ar=False)
            bubble(d, 30, 760, 96, spoken, ar=False)
    return img

def synth(text, path, voice):
    v, cfg = {"ar": (V_AR, CFG_AR), "en": (V_EN, CFG_EN), "st": (V_ST, CFG_ST)}[voice]
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        for chunk in v.synthesize(text, syn_config=cfg):
            w.writeframes(chunk.audio_int16_bytes)

def wav_dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

INTRO_TPL = [
    "إليك كلمة جديدة. معناها",
    "ننتقل إلى كلمة أخرى. معناها",
    "والآن كلمة جديدة. معناها",
]

def build_segments(n):
    meta = CONCEPTS[n]
    cs = [dict(c, level=meta["level"]) for c in meta["concepts"]]
    segs = []
    def add(kind, speaker, spoken, concept=None, extra=None, pause=1.5):
        segs.append({"kind": kind, "speaker": speaker, "spoken": spoken,
                     "concept": concept, "extra": extra, "pause": pause})
    add("title", "teacher",
        "أهلًا وسهلًا. أنا الأستاذ كريم، ومعي صديقي جيك. اليوم سنتعلم كلمات إنجليزية جديدة بطريقة سهلة. استمع بهدوء، ولا تقلق من أي شيء.",
        extra=[c["word"] for c in cs[:4]], pause=2.5)
    add("talk", "student", "Hello!", pause=1.5)
    for i, c in enumerate(cs[:3]):
        w_ar = TR["words"].get(c["word"].lower(), "")
        p_ar = TR["phrases"].get(c["phrase"].lower(), "")
        s_ar = TR["sents"].get(c["sent"], "")
        add("card", "teacher", f"{INTRO_TPL[i % 3]}: {w_ar}.", concept=c, extra="word", pause=1.2)
        add("talk", "teacher", f"{c['word'].capitalize()}.", concept=c, extra="word", pause=1.2)
        add("talk", "student", f"{c['word'].capitalize()}!", concept=c, extra="word", pause=1.5)
        if p_ar and c["phrase"].lower() != c["word"].lower():
            add("card", "teacher", f"ونقول: {p_ar}.", concept=c, extra="full", pause=1.0)
            add("talk", "teacher", f"{c['phrase']}.", concept=c, extra="full", pause=1.2)
            add("talk", "student", f"{c['phrase']}!", concept=c, extra="full", pause=1.5)
        if s_ar:
            add("card", "teacher", f"والجملة كاملة معناها: {s_ar}.", concept=c, extra="full", pause=1.0)
            add("talk", "teacher", f"{c['sent']}.", concept=c, extra="full", pause=3.0)
            add("card", "teacher", "استمع مرة أخرى.", concept=c, extra="full", pause=1.0)
            add("talk", "teacher", f"{c['sent']}.", concept=c, extra="full", pause=4.0)
            add("card", "teacher", "ومرة أخيرة، بهدوء.", concept=c, extra="full", pause=1.0)
            add("talk", "teacher", f"{c['sent']}.", concept=c, extra="full", pause=4.0)
            add("talk", "student", f"{c['sent']}!", concept=c, extra="full", pause=2.5)
        if i == 1:
            c0 = cs[0]
            add("card", "teacher", f"لنتذكر سريعًا. معناها: {TR['words'].get(c0['word'].lower(), '')}.",
                concept=c0, extra="recall", pause=1.0)
            add("talk", "teacher", f"{c0['word'].capitalize()}.", concept=c0, extra="recall", pause=2.0)
    def review_concept(other_ep, label):
        if other_ep >= 1 and other_ep in CONCEPTS and CONCEPTS[other_ep]["concepts"]:
            c = dict(CONCEPTS[other_ep]["concepts"][0], level=meta["level"])
            w_ar = TR["words"].get(c["word"].lower(), "")
            add("card", "teacher", f"{label} معناها: {w_ar}.", concept=c, extra="recall", pause=1.0)
            add("talk", "teacher", f"{c['sent']}.", concept=c, extra="recall", pause=3.0)
    review_concept(n - 2, "مراجعة من حلقات سابقة.")
    review_concept(n - 3, "ونتذكر أيضًا.")
    review_concept(n - 5, "ومراجعة أبعد.")
    review_concept(n - 8, "وذاكرتنا القديمة.")
    add("card", "teacher", "والآن جيك يجرّب الجمل في مشهد حقيقي.", pause=1.5)
    for c in cs[:3]:
        add("talk", "student", f"{c['sent']}?", concept=c, extra="recall", pause=2.0)
    add("card", "teacher", "والآن نراجع كلمات اليوم معًا.", pause=1.5)
    for c in cs[:3]:
        add("card", "teacher", f"{TR['words'].get(c['word'].lower(), '')}.", concept=c, extra="word", pause=0.8)
        add("talk", "teacher", f"{c['word'].capitalize()}. {c['sent']}.", concept=c, extra="full", pause=2.2)
    add("closing", "teacher",
        "أحسنتم. بهذا ننهي حلقة اليوم. سنتقابل في الحلقة القادمة. مع السلامة!", pause=1.5)
    add("talk", "student", "Goodbye!", pause=2.0)
    return meta, segs

def build_episode(n, outdir):
    meta, segs = build_segments(n)
    os.makedirs(outdir, exist_ok=True)
    audio = []
    for i, s in enumerate(segs):
        p = f"{outdir}/seg_{i:03d}.wav"
        if s["kind"] == "talk":
            voice = "st" if s["speaker"] == "student" else "en"
            if s["speaker"] == "teacher" and not s["spoken"].isascii():
                voice = "ar"
            synth(s["spoken"], p, voice)
        else:
            synth(s["spoken"], p, "ar")
        audio.append((p, wav_dur(p), s))
    speech = sum(d for _, d, _ in audio)
    gaps = [s["pause"] for _, _, s in audio]
    base = sum(gaps)
    extra = TOTAL - speech - base
    if extra > 0:
        gaps = [g + extra * (g / base) for g in gaps]
    elif extra < 0:
        scale = max(0.3, 1 + extra / base)
        gaps = [max(0.4, g * scale) for g in gaps]
    print(f"  speech={speech:.0f}s base_pauses={base:.0f}s extra={extra:.0f}s", flush=True)
    out_wav = f"{outdir}/audio.wav"
    timeline = []
    t = 0.0
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        for i, (p, dur, s) in enumerate(audio):
            timeline.append({"t": t, "seg": s})
            with wave.open(p) as r:
                w.writeframes(r.readframes(r.getnframes()))
            t += dur + gaps[i]
            w.writeframes(b"\x00\x00" * int(22050 * gaps[i]))
    frames = []
    for f in range(TOTAL):
        cur = timeline[0]
        for tl in timeline:
            if tl["t"] <= f:
                cur = tl
        frames.append(cur["seg"])
    img_cache = {}
    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-framerate", "1", "-i", "-", "-i", out_wav, "-c:v", "libx264", "-preset", "ultrafast",
         "-crf", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "64k",
         "-t", str(TOTAL), f"{outdir}/episode_{n:03d}.mp4"],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for seg in frames:
        key = (seg["kind"], seg["speaker"], seg["spoken"], str(seg["extra"]),
               json.dumps(seg["concept"], ensure_ascii=False, sort_keys=True) if seg["concept"] else None)
        if key not in img_cache:
            img_cache[key] = make_slide(n, seg["kind"], seg["speaker"], seg["spoken"],
                                        seg["concept"], meta, seg["extra"])
        proc.stdin.write(img_cache[key].tobytes())
        if len(img_cache) > 60:
            img_cache.clear()
    proc.stdin.close()
    proc.wait()
    for p, _, _ in audio:
        os.remove(p)
    os.remove(out_wav)
    return t

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if arg == "all":
        for n in range(1, 137):
            d = build_episode(n, f"/workspace/nla/videos2/ep{n:03d}")
            print(f"DONE ep{n:03d} content={d:.0f}s", flush=True)
    else:
        n = int(arg)
        d = build_episode(n, f"/workspace/nla/videos2/ep{n:03d}")
        print(f"DONE ep{n:03d} content={d:.0f}s")
