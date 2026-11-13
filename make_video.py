import json, os, sys, subprocess, wave, math
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from piper import PiperVoice, SynthesisConfig
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = PiperVoice.load("/workspace/nla/tts/en_US-amy-medium.onnx")
CFG = SynthesisConfig(length_scale=1.15)

W, H = 960, 540
FPS = 1
TOTAL = 600  # seconds

BG = {"A1": (253, 246, 227), "A2": (227, 240, 252), "B1": (230, 246, 232), "B2": (240, 240, 245)}
ACCENT = {"A1": (180, 95, 30), "A2": (30, 100, 180), "B1": (40, 120, 70), "B2": (90, 80, 140)}

F_EN_B = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Bold.ttf", 40)
F_EN = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Regular.ttf", 34)
F_EN_I = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Italic.ttf", 26)
F_SM = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Regular.ttf", 22)
F_SM_B = ImageFont.truetype("/workspace/nla/fonts/NotoSans-Bold.ttf", 24)
F_AR = ImageFont.truetype("/workspace/nla/fonts/NotoNaskhArabic-Regular.ttf", 26)

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

def make_slide(ep, beat_name, line, gesture, ar_hint, level):
    img = Image.new("RGB", (W, H), BG[level])
    d = ImageDraw.Draw(img)
    acc = ACCENT[level]
    d.rectangle([0, 0, W, 70], fill=acc)
    d.text((24, 14), f"Episode {ep['episode']} · {ep['level']} · Module {ep['module']} — {beat_name}", font=F_SM_B, fill=(255, 255, 255))
    d.text((W - 24 - d.textlength(ep['title'], font=F_SM_B), 14), ep['title'], font=F_SM_B, fill=(255, 255, 255))
    y = 120
    if line and line != "…":
        for ln in wrap(d, line, F_EN_B, W - 120):
            d.text((60, y), ln, font=F_EN_B, fill=(35, 35, 40))
            y += 52
        y += 8
        if gesture:
            for ln in wrap(d, "gesture: " + gesture, F_EN_I, W - 120):
                d.text((60, y), ln, font=F_EN_I, fill=(110, 110, 120))
                y += 34
    else:
        d.text((60, y + 30), "…", font=F_EN_B, fill=(140, 140, 150))
        y += 90
    if ar_hint:
        y = max(y + 20, H - 150)
        d.line([40, y - 16, W - 40, y - 16], fill=(200, 200, 205), width=2)
        for ln in wrap(d, ar_text(ar_hint), F_AR, W - 120):
            d.text((60, y), ln, font=F_AR, fill=(80, 80, 90))
            y += 36
    return img

def synth(text, path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        for chunk in VOICE.synthesize(text, syn_config=CFG):
            w.writeframes(chunk.audio_int16_bytes)

def silence(sec, path):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        w.writeframes(b"\x00\x00" * int(22050 * sec))

def wav_dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

def build_episode(ep, outdir):
    lvl = ep["level"]
    os.makedirs(outdir, exist_ok=True)
    segs = []  # (wav_path, slide_kwargs)
    i = 0
    def add(text, gap, beat_name, line=None, gesture=None, ar_hint=None):
        nonlocal i
        p = f"{outdir}/seg_{i:03d}.wav"
        if text:
            synth(text, p)
        else:
            silence(gap, p)
        dur = wav_dur(p) if text else gap
        segs.append((p, dur, beat_name, line, gesture, ar_hint))
        i += 1

    hints = {
        "Greeting ritual": "ابدأ دائمًا بنفس الجملة ونفس النبرة — الطقس يصنع الأمان",
        "Scene immersion": "أشِر ويلمس الشيء مع كل جملة. لا تطلب منه أي شيء — هو يشاهد فقط",
        "Live dialogue": "العب الدورين بصوتين مختلفين، واصمت 5 ثوانٍ بعد كل سؤال",
        "Echo & shadow play": "التظليل لعبة لا واجب — إن لم يقلد أكمل وحدك بفرح",
        "Silent invitation": "الصمت المنتظر هو الدرس — أنت من يكمل الإجابة دائمًا",
        "Old lines, new scene": "جمل مألوفة في مشهد جديد = متعة «أنا أعرف هذا»",
        "Action & touch": "خُض يده مع الفعل الحقيقي — اللغة تركب الحركة",
        "Variation & free play": "لو نطق كلمة وسّعها أنت للجملة كاملة بفرح — ولا تطلب منه تكرارها",
        "Spiral recall": "استرجع جمل قديمة وكأنك تذكروا معًا — بدون أي اختبار",
        "Quiet wind-down": "خفف الصوت تدريجيًا — الجملة تنتسب للهدوء",
        "Closing ritual": "نفس جملة الوداع ونفس الإيماءة في كل مرة",
    }

    def plan(beat_name, lines, dlgs):
        items = []  # (speak_text, gap_after, slide_line, gesture)
        if beat_name.startswith("Greeting"):
            for rep in range(2):
                for l in lines:
                    items.append((l, 3, l, None))
        elif beat_name.startswith("Scene immersion"):
            for l in lines:
                items.append(("Look. " + l, 2, l, None))
                items.append((l, 2, l, None))
                items.append((l, 4, l, None))
        elif beat_name.startswith("Live dialogue"):
            for d in dlgs:
                items.append((d["line"], 5, d["line"], d.get("gesture")))
            for d in dlgs:
                items.append((d["line"], 3, d["line"], d.get("gesture")))
            for l in lines:
                items.append((l, 3, l, None))
        elif beat_name.startswith("Echo"):
            for l in lines:
                items.append((l, 3, l, None))
                items.append((l, 4, l, None))
        elif beat_name.startswith("Silent invitation"):
            for d in dlgs:
                items.append((d["line"], 5, d["line"], d.get("gesture")))
            for d in dlgs:
                items.append((d["line"], 4, d["line"], d.get("gesture")))
            for d in dlgs:
                items.append((d["line"], 3, d["line"], d.get("gesture")))
        elif beat_name.startswith("Old lines"):
            for l in lines:
                items.append((l, 2, l, None))
                items.append((l, 4, l, None))
        elif beat_name.startswith("Action"):
            for l in lines[:2]:
                items.append((l, 2, l, None))
                items.append((l, 5, l, None))
        elif beat_name.startswith("Variation"):
            for l in lines[2:]:
                items.append(("Look! " + l, 3, l, None))
                items.append((l, 5, l, None))
            if len(lines) <= 3:
                items.append((lines[0], 5, lines[0], None))
        elif beat_name.startswith("Spiral recall"):
            for l in lines:
                items.append((l, 2, l, None))
                items.append((l, 5, l, None))
        elif beat_name.startswith("Quiet wind-down"):
            for rep in range(3):
                items.append((lines[0], 6, lines[0], None))
        elif beat_name.startswith("Closing"):
            items.append((lines[0], 4, lines[0], None))
            items.append((lines[0], 4, lines[0], None))
        return items

    for b in ep["beats"]:
        full = b["beat"]
        name = full.split(" (")[0]
        hint = hints.get(name, "")
        raw = [a["line"] for a in b["audio"] if a["line"] != "…"]
        clean = []
        for r in raw:
            clean.extend(x.strip() for x in r.split("·") if x.strip() and x.strip() != "...")
        dlgs = [a for a in b["audio"] if a.get("gesture") is not None and a["line"] != "…"]
        last_slide = [None, None, None]
        for speak, gap, slide, gest in plan(name, clean, dlgs):
            add(speak, gap, name, slide, gest, hint)
            if slide:
                last_slide = [slide, gest, hint]
        add(None, 4, name, last_slide[0], last_slide[1], last_slide[2])

    # pad to exactly TOTAL seconds with quiet
    used = sum(d for _, d, *_ in segs)
    if used < TOTAL:
        add(None, TOTAL - used, "Quiet together", None, None,
            "دقيقة هدوء معًا — الاستيعاب يحدث في السكينة. لا تملأ الصمت.")

    # audio concat
    with open(f"{outdir}/audio.txt", "w") as f:
        for p, dur, *_ in segs:
            f.write(f"file '{p}'\n")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", f"{outdir}/audio.txt",
                    "-c", "copy", f"{outdir}/audio.wav"], check=True, capture_output=True)

    # timeline: slide active at each second
    timeline = []
    for p, dur, name, line, gesture, hint in segs:
        timeline.extend([(name, line, gesture, hint)] * max(1, round(dur)))
    timeline = (timeline + [timeline[-1]] * TOTAL)[:TOTAL]

    out = f"{outdir}/episode_{ep['episode']:03d}.mp4"
    proc = subprocess.Popen(
        [FFMPEG, "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "1", "-i", "pipe:0",
         "-i", f"{outdir}/audio.wav",
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "64k", "-t", str(TOTAL), out],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    prev = None
    for t in range(TOTAL):
        name, line, gesture, hint = timeline[t]
        if (name, line, gesture, hint) != prev:
            img = make_slide(ep, name, line, gesture, hint, lvl)
            prev = (name, line, gesture, hint)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return out

if __name__ == "__main__":
    eps = json.load(open("/workspace/nla/book/video/video_scripts_full.json"))["episodes"]
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    if which == "module1":
        targets = [e for e in eps if e["module"] == 1]
        outroot = "/workspace/nla/videos"
    elif which == "all":
        targets = eps
        outroot = "/workspace/nla/videos"
    else:
        targets = [eps[int(which) - 1]]
        outroot = "/workspace/nla/videos_test"
    for e in targets:
        out = build_episode(e, f"{outroot}/ep{e['episode']:03d}")
        print("DONE", out, os.path.getsize(out), "bytes", flush=True)
