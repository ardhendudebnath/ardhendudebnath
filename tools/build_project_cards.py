"""
Animated output cards — one per project.

    python tools/build_project_cards.py

Every number drawn here is copied from that project's own README. Nothing is
invented, estimated, or rounded up. If a repo has not measured something yet,
this file does not draw it.

Rendering: each frame is drawn at 2x and downsampled, because PIL has no
antialiasing for shapes. Scanlines and grain go on after the downsample so
they stay a crisp single pixel.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "3d", "assets", "cards")
os.makedirs(OUT, exist_ok=True)

# The scene coordinate space stays 640x360 — every scene is written against it.
# EXPORT only changes the resolution the frames are written out at.
#
# Why 1.6x: the site renders a card at roughly 500 CSS px, and a 1.5x or 2x
# display then needs 750-1000 device pixels. A 640px export gets upscaled and
# every 9px label goes soft. 1024px covers both that and the ~890px GitHub
# renders the README image at.
W, H = 640, 360
EXPORT = 1.6
OW, OH = round(W * EXPORT), round(H * EXPORT)
SS = 3                      # supersample factor, for antialiasing
FRAMES = 30
FRAME_MS = 70
QUALITY = 72

VOID = (13, 15, 19)
INK = (22, 25, 30)
EDGE = (38, 43, 51)
ASH = (109, 116, 126)
SMOKE = (168, 174, 184)
BONE = (234, 231, 224)
BLOOD = (204, 41, 54)

F_MONO = r"C:\Windows\Fonts\consola.ttf"
F_MONO_B = r"C:\Windows\Fonts\consolab.ttf"
F_UI = r"C:\Windows\Fonts\bahnschrift.ttf"
F_BN = r"C:\Windows\Fonts\Nirmala.ttc"


def S(v):
    return int(round(v * SS))


def font(path, size):
    return ImageFont.truetype(path, S(size))


# ── static grade layers, applied after downsample ────────────────────────
_yy, _xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
_nx = (_xx / OW - 0.5) * 2.0
_ny = (_yy / OH - 0.5) * 2.0
VIGNETTE = np.clip(1.0 - (_nx * _nx * 0.16 + _ny * _ny * 0.20), 0, 1)[..., None]
SCAN = np.ones((OH, OW, 1), np.float32)
SCAN[1::max(2, round(3 * EXPORT))] = 0.90   # keep the scanline pitch constant
GRAIN = (np.random.default_rng(11).random((OH, OW, 1), dtype=np.float32) - 0.5) * 0.018


def finish(im):
    im = im.resize((OW, OH), Image.LANCZOS)
    a = np.asarray(im, np.float32) / 255.0
    a = np.clip(a * VIGNETTE * SCAN + GRAIN, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "RGB")


# ── easing ───────────────────────────────────────────────────────────────
def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def stagger(t, i, n, span=0.6):
    """Item i of n starts late and eases in over `span` of the timeline."""
    start = (i / max(n, 1)) * (1 - span)
    return ease((t - start) / span)


def tracked(d, xy, text, f, fill, tracking=0.0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + S(tracking)
    return x


def tracked_w(d, text, f, tracking=0.0):
    return sum(d.textlength(c, font=f) + S(tracking) for c in text) - S(tracking)


def dashed(d, x0, y, x1, fill, dash=6, gap=5, width=1):
    x = x0
    while x < x1:
        d.line([x, y, min(x + S(dash), x1), y], fill=fill, width=S(width))
        x += S(dash + gap)


# ── shared chrome ────────────────────────────────────────────────────────
def chrome(d, index, title, footer):
    f_t = font(F_MONO_B, 13)
    f_i = font(F_MONO_B, 11)
    f_f = font(F_MONO, 10)
    f_tag = font(F_MONO_B, 9)

    d.rectangle([S(14), S(14), S(W - 14), S(H - 14)], outline=EDGE, width=S(1))
    for cx, cy, sx, sy in ((14, 14, 1, 1), (W - 14, 14, -1, 1),
                           (14, H - 14, 1, -1), (W - 14, H - 14, -1, -1)):
        d.line([S(cx), S(cy), S(cx + 13 * sx), S(cy)], fill=BONE, width=S(1))
        d.line([S(cx), S(cy), S(cx), S(cy + 13 * sy)], fill=BONE, width=S(1))

    x = tracked(d, (S(30), S(26)), index, f_i, BLOOD, 1.4)
    tracked(d, (x + S(10), S(25)), title, f_t, BONE, 0.8)

    tag = "OUTPUT"
    tw = tracked_w(d, tag, f_tag, 2.2)
    d.rectangle([S(W - 30) - tw - S(12), S(24), S(W - 30), S(40)],
                outline=EDGE, width=S(1))
    tracked(d, (S(W - 30) - tw - S(6), S(28)), tag, f_tag, ASH, 2.2)

    tracked(d, (S(30), S(H - 36)), footer, f_f, ASH, 1.1)


def render(name, scene, index, title, footer):
    frames = []
    for i in range(FRAMES):
        raw = i / (FRAMES - 1)
        t = min(raw / 0.72, 1.0)           # animate in, then hold
        im = Image.new("RGB", (W * SS, H * SS), VOID)
        d = ImageDraw.Draw(im)
        chrome(d, index, title, footer)
        scene(d, t, raw)
        frames.append(finish(im))

    path = os.path.join(OUT, f"{name}.webp")
    frames[0].save(path, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, quality=QUALITY, method=6)
    frames[-1].save(os.path.join(OUT, f"{name}.jpg"), quality=88, optimize=True)
    print(f"  {name:30} {os.path.getsize(path)/1024:6.0f} KB")


# ═════════════════════════════════════════════════════════════════════════
# 01 · gst-eval-harness — run-to-run instability
# README: per-run slab accuracy 53.6 / 50.0 / 53.6 / 50.0 / 64.3, mean 54.3
# ═════════════════════════════════════════════════════════════════════════
def scene_gst_eval(d, t, raw):
    runs = [53.6, 50.0, 53.6, 50.0, 64.3]
    top, bottom = 118, 268
    left, right = 44, 404
    ymax = 70.0

    f_v = font(F_UI, 15)
    f_l = font(F_MONO, 9)
    f_k = font(F_MONO, 9)
    f_big = font(F_UI, 40)
    f_sub = font(F_MONO, 9)

    # grid
    for g in (0, 25, 50, 70):
        y = bottom - (g / ymax) * (bottom - top)
        dashed(d, S(left), S(y), S(right), (30, 34, 41))
        d.text((S(left - 26), S(y - 6)), f"{g}", font=f_k, fill=(70, 76, 85))

    slot = (right - left) / len(runs)
    bw = slot * 0.52
    for i, v in enumerate(runs):
        p = stagger(t, i, len(runs), 0.62)
        if p <= 0:
            continue
        h = (v / ymax) * (bottom - top) * p
        x0 = left + slot * i + (slot - bw) / 2
        hot = (i == 4)
        col = BLOOD if hot else (58, 64, 74)
        d.rectangle([S(x0), S(bottom - h), S(x0 + bw), S(bottom)], fill=col)
        d.rectangle([S(x0), S(bottom - h), S(x0 + bw), S(bottom - h + 2)],
                    fill=BONE if hot else SMOKE)
        if p > 0.55:
            lab = f"{v:.1f}"
            lw = d.textlength(lab, font=f_v)
            d.text((S(x0 + bw / 2) - lw / 2, S(bottom - h - 24)), lab,
                   font=f_v, fill=BONE if hot else SMOKE)
        d.text((S(x0 + bw / 2) - d.textlength(f"run {i+1}", font=f_l) / 2,
                S(bottom + 10)), f"run {i+1}", font=f_l, fill=ASH)

    d.line([S(left), S(bottom), S(right), S(bottom)], fill=EDGE, width=S(1))

    # mean line
    if t > 0.5:
        my = bottom - (54.3 / ymax) * (bottom - top)
        dashed(d, S(left), S(my), S(right), BLOOD, dash=5, gap=4)
        d.text((S(right + 6), S(my - 6)), "mean", font=f_k, fill=BLOOD)

    # readout
    val = 54.3 * ease(t / 0.8)
    d.text((S(452), S(126)), f"{val:.1f}%", font=f_big, fill=BONE)
    d.text((S(454), S(174)), "mean slab accuracy", font=f_sub, fill=ASH)
    d.line([S(454), S(196), S(596), S(196)], fill=EDGE, width=S(1))
    if t > 0.7:
        d.text((S(454), S(208)), "spread   50.0 → 64.3", font=f_sub, fill=SMOKE)
        d.text((S(454), S(226)), "self-agree      53.6%", font=f_sub, fill=SMOKE)
        d.text((S(454), S(244)), "stale slab cited 11.4%", font=f_sub, fill=BLOOD)


# ═════════════════════════════════════════════════════════════════════════
# 02 · gst-resilient-agent — retrieval recall@k
# ═════════════════════════════════════════════════════════════════════════
def scene_agent(d, t, raw):
    ks = [1, 3, 5, 10]
    series = [
        ("semantic", [46.4, 64.3, 75.0, 89.3], BONE, "715ms"),
        ("hybrid rrf", [32.1, 57.1, 64.3, 82.1], BLOOD, "708ms"),
        ("keyword", [32.1, 42.9, 46.4, 60.7], (95, 102, 112), "9ms"),
    ]
    top, bottom = 110, 268
    left, right = 52, 400

    f_k = font(F_MONO, 9)
    f_lg = font(F_MONO_B, 10)
    f_lt = font(F_MONO, 9)

    for g in (0, 25, 50, 75, 100):
        y = bottom - (g / 100) * (bottom - top)
        dashed(d, S(left), S(y), S(right), (30, 34, 41))
        d.text((S(left - 30), S(y - 6)), f"{g}", font=f_k, fill=(70, 76, 85))
    for i, k in enumerate(ks):
        x = left + (right - left) * i / (len(ks) - 1)
        d.text((S(x) - d.textlength(f"@{k}", font=f_k) / 2, S(bottom + 10)),
               f"@{k}", font=f_k, fill=ASH)
    d.line([S(left), S(bottom), S(right), S(bottom)], fill=EDGE, width=S(1))

    prog = ease(t) * (len(ks) - 1)
    for name, vals, col, _ in series:
        pts = []
        for i, v in enumerate(vals):
            x = left + (right - left) * i / (len(ks) - 1)
            y = bottom - (v / 100) * (bottom - top)
            pts.append((x, y))
        drawn = []
        for i in range(len(pts)):
            if i <= prog:
                drawn.append(pts[i])
            elif i - 1 < prog:
                f = prog - (i - 1)
                x = pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f
                y = pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f
                drawn.append((x, y))
                break
        if len(drawn) > 1:
            d.line([(S(x), S(y)) for x, y in drawn], fill=col,
                   width=S(2), joint="curve")
        for i, (x, y) in enumerate(pts):
            if i <= prog:
                d.ellipse([S(x - 3.2), S(y - 3.2), S(x + 3.2), S(y + 3.2)],
                          fill=VOID, outline=col, width=S(2))

    # legend
    ly = 122
    for name, vals, col, lat in series:
        d.rectangle([S(438), S(ly + 3), S(452), S(ly + 6)], fill=col)
        d.text((S(460), S(ly - 2)), name, font=f_lg, fill=SMOKE)
        d.text((S(460), S(ly + 14)), f"{vals[-1]:.1f}% @10 · {lat}",
               font=f_lt, fill=ASH)
        ly += 44

    if t > 0.8:
        d.line([S(438), S(250), S(600), S(250)], fill=EDGE, width=S(1))
        d.text((S(438), S(258)), "11 injected failure modes", font=f_lt, fill=BLOOD)


# ═════════════════════════════════════════════════════════════════════════
# 03 · register-aware-translation — the formality dial
# ═════════════════════════════════════════════════════════════════════════
def scene_register(d, t, raw):
    stops = [
        ("\u09a4\u09c1\u0987", "tui", "informal", "du", "tu"),
        ("\u09a4\u09c1\u09ae\u09bf", "tumi", "neutral", "ihr", "vous"),
        ("\u0986\u09aa\u09a8\u09bf", "apni", "formal", "Sie", "vous"),
    ]
    f_bn = font(F_BN, 40)
    f_rom = font(F_MONO_B, 12)
    f_lab = font(F_MONO, 9)
    f_sm = font(F_MONO, 9)
    f_eu = font(F_MONO, 10)

    track_y = 218
    left, right = 88, 552

    # The marker sweeps the full dial and back — the point is that register
    # is a continuous control, not a one-off choice.
    sweep = raw * 2.0
    pos = sweep if sweep <= 1 else max(0.0, 2.0 - sweep)
    active = min(int(round(pos * 2)), 2)

    d.line([S(left), S(track_y), S(right), S(track_y)], fill=EDGE, width=S(1))

    for i, (bn, rom, lab, de, fr) in enumerate(stops):
        x = left + (right - left) * i / 2
        near = 1.0 - min(abs(pos * 2 - i), 1.0)
        col = tuple(int(a + (b - a) * near) for a, b in zip((78, 84, 94), BONE))

        bw = d.textlength(bn, font=f_bn)
        d.text((S(x) - bw / 2, S(128)), bn, font=f_bn, fill=col)

        rw = tracked_w(d, rom, f_rom, 1.6)
        tracked(d, (S(x) - rw / 2, S(184)), rom, f_rom,
                BLOOD if i == active else ASH, 1.6)

        d.ellipse([S(x - 4), S(track_y - 4), S(x + 4), S(track_y + 4)],
                  fill=VOID, outline=BLOOD if i == active else EDGE, width=S(2))

        lw = tracked_w(d, lab, f_lab, 1.8)
        tracked(d, (S(x) - lw / 2, S(track_y + 14)), lab, f_lab,
                SMOKE if i == active else (70, 76, 85), 1.8)

        eu = f"{de} · {fr}"
        ew = d.textlength(eu, font=f_eu)
        d.text((S(x) - ew / 2, S(track_y + 32)), eu, font=f_eu,
               fill=(88, 94, 104) if i == active else (48, 53, 61))

    mx = left + (right - left) * pos
    d.line([S(mx), S(track_y - 22), S(mx), S(track_y + 10)], fill=BLOOD, width=S(2))
    d.polygon([(S(mx - 5), S(track_y - 26)), (S(mx + 5), S(track_y - 26)),
               (S(mx), S(track_y - 18))], fill=BLOOD)

    d.text((S(30), S(H - 58)), "100% register detection · 98.5% exact (bn)",
           font=f_sm, fill=SMOKE)


# ═════════════════════════════════════════════════════════════════════════
# 04 · symmetrynet — rotate the molecule, the prediction holds
# ═════════════════════════════════════════════════════════════════════════
def _molecule():
    atoms, bonds = [], []
    for k in range(6):                       # ring
        a = math.radians(60 * k)
        atoms.append([math.cos(a), math.sin(a), 0.0, 1.0])
        bonds.append((k, (k + 1) % 6))
    for k, z in ((0, 0.62), (3, -0.62)):     # two substituents, out of plane
        a = math.radians(60 * k)
        atoms.append([math.cos(a) * 1.95, math.sin(a) * 1.95, z, 0.72])
        bonds.append((k, len(atoms) - 1))
    return np.array(atoms, np.float32), bonds


ATOMS, BONDS = _molecule()


def scene_symmetry(d, t, raw):
    f_big = font(F_UI, 34)
    f_sub = font(F_MONO, 9)
    f_lock = font(F_MONO_B, 10)

    ang = raw * 2 * math.pi
    ca, sa = math.cos(ang), math.sin(ang)
    tilt = math.radians(24)
    ct, st = math.cos(tilt), math.sin(tilt)

    cx, cy, scale = 196, 196, 52
    pts = []
    for x, y, z, r in ATOMS:
        x2, z2 = x * ca - z * sa, x * sa + z * ca      # spin about Y
        y2, z3 = y * ct - z2 * st, y * st + z2 * ct    # fixed tilt
        depth = (z3 + 2.6) / 5.2
        pts.append((cx + x2 * scale, cy - y2 * scale, depth, r))

    for a, b in BONDS:
        x0, y0, d0, _ = pts[a]
        x1, y1, d1, _ = pts[b]
        shade = int(52 + 92 * ((d0 + d1) / 2))
        d.line([S(x0), S(y0), S(x1), S(y1)], fill=(shade, shade + 3, shade + 8),
               width=S(2))
    for x, y, depth, r in sorted(pts, key=lambda p: p[2]):
        rad = (7.5 + 5.5 * depth) * r
        tone = int(110 + 130 * depth)
        d.ellipse([S(x - rad), S(y - rad), S(x + rad), S(y + rad)],
                  fill=(tone, tone - 2, tone - 6), outline=VOID, width=S(2))

    d.line([S(360), S(96), S(360), S(276)], fill=EDGE, width=S(1))

    d.text((S(386), S(112)), "43.43", font=f_big, fill=BONE)
    d.text((S(478), S(130)), "meV", font=f_sub, fill=ASH)
    d.text((S(386), S(156)), "HOMO-LUMO gap, QM9 test MAE", font=f_sub, fill=ASH)

    d.text((S(386), S(196)), "equivariance error", font=f_sub, fill=ASH)
    # Bahnschrift has no superscript glyphs — set the exponent by hand.
    f_b, f_e = font(F_UI, 20), font(F_UI, 12)
    base_txt = "1.3 × 10"
    d.text((S(386), S(212)), base_txt, font=f_b, fill=BLOOD)
    d.text((S(386) + d.textlength(base_txt, font=f_b) + S(1), S(208)),
           "-15", font=f_e, fill=BLOOD)

    if t > 0.35:
        tracked(d, (S(386), S(250)), "PREDICTION LOCKED", f_lock, BONE, 1.6)


# ═════════════════════════════════════════════════════════════════════════
# 05 · chest-xray-classifier — per-class F1
# ═════════════════════════════════════════════════════════════════════════
def scene_xray(d, t, raw):
    rows = [("COVID19", 0.982), ("PNEUMONIA", 0.970),
            ("NORMAL", 0.953), ("LUNG_OPACITY", 0.929)]
    f_l = font(F_MONO, 10)
    f_v = font(F_UI, 14)
    f_big = font(F_UI, 40)
    f_sub = font(F_MONO, 9)

    left, right = 172, 424
    y = 116
    lo = 0.90                                # zoomed axis, labelled below
    for i, (name, v) in enumerate(rows):
        p = stagger(t, i, len(rows), 0.6)
        d.text((S(left - 12) - tracked_w(d, name, f_l, 1.2), S(y + 1)),
               "", font=f_l, fill=ASH)
        tracked(d, (S(left - 12) - tracked_w(d, name, f_l, 1.2), S(y)),
                name, f_l, SMOKE, 1.2)
        d.rectangle([S(left), S(y - 1), S(right), S(y + 11)], fill=(24, 27, 33))
        w = (right - left) * ((v - lo) / (1.0 - lo)) * p
        col = BLOOD if i == 0 else (72, 79, 90)
        d.rectangle([S(left), S(y - 1), S(left + w), S(y + 11)], fill=col)
        if p > 0.5:
            d.text((S(left + w + 8), S(y - 3)), f"{v:.3f}", font=f_v,
                   fill=BONE if i == 0 else SMOKE)
        y += 34

    d.text((S(left), S(y + 4)), f"axis starts at {lo:.2f}", font=f_sub,
           fill=(70, 76, 85))

    val = 0.9587 * ease(t / 0.8)
    d.text((S(452), S(122)), f"{val:.4f}", font=f_big, fill=BONE)
    d.text((S(454), S(170)), "macro F1 · ResNet18", font=f_sub, fill=ASH)
    d.line([S(454), S(190), S(600), S(190)], fill=EDGE, width=S(1))
    if t > 0.7:
        d.text((S(454), S(202)), "accuracy    0.9524", font=f_sub, fill=SMOKE)
        d.text((S(454), S(220)), "macro AUC   0.9928", font=f_sub, fill=SMOKE)
        d.text((S(454), S(238)), "lungs only  0.9341", font=f_sub, fill=SMOKE)


# ═════════════════════════════════════════════════════════════════════════
# 06 · smart-healthcare-triage — the escalation ladder
# ═════════════════════════════════════════════════════════════════════════
def scene_triage(d, t, raw):
    tiers = [("SELF_CARE", (72, 79, 90)), ("URGENT_CARE", (150, 110, 60)),
             ("EMERGENCY", BLOOD)]
    f_t = font(F_MONO_B, 12)
    f_s = font(F_MONO, 9)
    f_n = font(F_UI, 26)

    left, right = 44, 344      # leaves a gutter for the escalation arrows
    base, step = 258, 56
    reach = ease(t) * 2

    for i, (name, col) in enumerate(tiers):
        y = base - i * step
        lit = reach >= i - 0.15
        bg = tuple(int(a + (b - a) * (0.24 if lit else 0.05))
                   for a, b in zip(VOID, col))
        d.rectangle([S(left), S(y - 20), S(right), S(y + 12)],
                    fill=bg, outline=col if lit else (34, 38, 45), width=S(1))
        tracked(d, (S(left + 14), S(y - 12)), name, f_t,
                BONE if lit else (62, 68, 77), 1.4)
        if lit:
            d.rectangle([S(left), S(y - 20), S(left + 3), S(y + 12)], fill=col)

    for i in range(2):
        if reach > i + 0.2:
            y = base - i * step - 20
            ax = right + 22
            d.line([S(ax), S(y), S(ax), S(y - 24)], fill=BLOOD, width=S(1))
            d.polygon([(S(ax - 4), S(y - 22)), (S(ax + 4), S(y - 22)),
                       (S(ax), S(y - 30))], fill=BLOOD)

    d.line([S(400), S(100), S(400), S(276)], fill=EDGE, width=S(1))
    stats = [("79", "symptoms"), ("487", "phrases, 3 languages"),
             ("122", "tests")]
    sy = 112
    for n, lab in stats:
        d.text((S(424), S(sy)), n, font=f_n, fill=BONE)
        d.text((S(424 + d.textlength(n, font=f_n) / SS + 8), S(sy + 14)),
               lab, font=f_s, fill=ASH)
        sy += 58


# ═════════════════════════════════════════════════════════════════════════
# 07 · llm-serving-unit-economics — the measurement space, in 3D
#
# This repo has NOT measured anything yet: "build complete, nothing measured
# yet (week 1 of 6)", and its README states that every number in it is absent
# rather than estimated. So this card draws the *design* — the three axes it
# will measure on and the three workload profiles it will run — and leaves the
# slots visibly empty. Inventing a cost curve here would be the one thing the
# repo explicitly refuses to do.
# ═════════════════════════════════════════════════════════════════════════
def _box_edges(cx, cy, cz, sx, sy, sz):
    """The 12 edges of an axis-aligned box, as pairs of 3D vertices."""
    xs, ys, zs = (cx - sx / 2, cx + sx / 2), (cy - sy / 2, cy + sy / 2), \
                 (cz - sz / 2, cz + sz / 2)
    v = [(x, y, z) for x in xs for y in ys for z in zs]
    out = []
    for i in range(8):
        for bit in (1, 2, 4):
            j = i ^ bit
            if j > i:
                out.append((v[i], v[j]))
    return out


def _project(p, ang, tilt, cx, cy, scale):
    x, y, z = p
    ca, sa = math.cos(ang), math.sin(ang)
    x2, z2 = x * ca - z * sa, x * sa + z * ca
    ct, st = math.cos(tilt), math.sin(tilt)
    y2, z3 = y * ct - z2 * st, y * st + z2 * ct
    return cx + x2 * scale, cy - y2 * scale, z3


def scene_serving(d, t, raw):
    f_lab = font(F_MONO, 9)
    f_h = font(F_MONO_B, 10)
    f_k = font(F_MONO, 9)

    # Sway, don't spin. A full revolution would pass through face-on
    # orientations where a box collapses to a flat rectangle; an oscillation
    # about a three-quarter view keeps it reading as a solid the whole loop.
    ang = math.radians(34) + math.radians(15) * math.sin(raw * 2 * math.pi)
    tilt = math.radians(26)
    cx, cy, scale = 186, 190, 168

    def pr(p):
        return _project(p, ang, tilt, cx, cy, scale)

    # The measurement space itself.
    for a, b in _box_edges(0, 0, 0, 1.10, 0.86, 0.86):
        x0, y0, d0 = pr(a)
        x1, y1, d1 = pr(b)
        sh = int(40 + 46 * ((d0 + d1) / 2 + 0.6))
        d.line([S(x0), S(y0), S(x1), S(y1)], fill=(sh, sh + 3, sh + 8), width=S(1))

    # Three axes out of the front-bottom-left corner, one per dimension.
    org = (-0.55, -0.43, 0.43)
    axes = [((0.55, -0.43, 0.43), BLOOD),        # cost
            ((-0.55, 0.43, 0.43), BONE),         # quality
            ((-0.55, -0.43, -0.43), (120, 128, 140))]  # latency
    ox, oy, _ = pr(org)
    for end, col in axes:
        ex, ey, _ = pr(end)
        d.line([S(ox), S(oy), S(ex), S(ey)], fill=col, width=S(2))
        d.ellipse([S(ex - 3), S(ey - 3), S(ex + 3), S(ey + 3)], fill=col)

    # Three empty slots — one per workload profile, nothing measured in them.
    pulse = 0.5 + 0.5 * math.sin(raw * 2 * math.pi)
    for i, xoff in enumerate((-0.30, 0.0, 0.30)):
        lit = int(52 + 40 * pulse)
        for a, b in _box_edges(xoff, -0.02, 0.0, 0.20, 0.20, 0.20):
            x0, y0, _ = pr(a)
            x1, y1, _ = pr(b)
            d.line([S(x0), S(y0), S(x1), S(y1)], fill=(lit, lit, lit), width=S(1))

    # Right panel — only facts the repo actually states.
    px = 372
    d.line([S(px - 20), S(96), S(px - 20), S(286)], fill=EDGE, width=S(1))

    tracked(d, (S(px), S(100)), "MEASURING", f_h, SMOKE, 1.6)
    rows = [("cost", "$ / 1M tokens", BLOOD),
            ("quality", "macro F1", BONE),
            ("latency", "p95 ms", (120, 128, 140))]
    y = 122
    for name, unit, col in rows:
        d.rectangle([S(px), S(y + 3), S(px + 10), S(y + 6)], fill=col)
        d.text((S(px + 18), S(y - 2)), name, font=f_lab, fill=SMOKE)
        d.text((S(px + 76), S(y - 2)), unit, font=f_lab, fill=ASH)
        y += 18

    d.line([S(px), S(184), S(px + 214), S(184)], fill=EDGE, width=S(1))
    tracked(d, (S(px), S(194)), "WORKLOAD PROFILES", f_h, SMOKE, 1.6)
    profs = [("short", "606 ch", "48 tok"),
             ("long_in", "7,177 ch", "48 tok"),
             ("long_out", "446 ch", "768 tok")]
    y = 216
    for name, inp, out in profs:
        d.text((S(px), S(y)), name, font=f_lab, fill=BONE)
        d.text((S(px + 64), S(y)), inp, font=f_lab, fill=ASH)
        d.text((S(px + 130), S(y)), "→ " + out, font=f_lab, fill=ASH)
        y += 17

    if t > 0.4:
        tracked(d, (S(px), S(276)), "WEEK 1 OF 6 · NO DATA YET", f_h, BLOOD, 1.4)


# ═════════════════════════════════════════════════════════════════════════
# 08 · predicting_customer_churn — rebuilt on the real 7,032-row dataset
#
# The old notebook invented 5 rows and scored 0.5 AUC on a 2-row test set.
# These are measured on the real IBM Telco set. Only the two thresholds that
# were actually evaluated are shown — the card toggles between them rather
# than sweeping, because intermediate operating points were never measured.
# ═════════════════════════════════════════════════════════════════════════
def scene_churn(d, t, raw):
    f_big = font(F_UI, 44)
    f_lab = font(F_MONO, 9)
    f_h = font(F_MONO_B, 10)
    f_v = font(F_UI, 13)

    ops = [("0.50", 0.6426, 0.5722, 0.6054, 214, "default"),
           ("0.30", 0.5397, 0.7807, 0.6383, 292, "tuned for F1")]
    active = 0 if (raw % 1.0) < 0.5 else 1

    y = 104
    for i, (th, prec, rec, f1, caught, note) in enumerate(ops):
        on = (i == active)
        box = (26, 32, 40) if on else (18, 20, 25)
        d.rectangle([S(40), S(y), S(344), S(y + 84)], fill=box,
                    outline=BLOOD if on else EDGE, width=S(1))
        if on:
            d.rectangle([S(40), S(y), S(43), S(y + 84)], fill=BLOOD)

        tracked(d, (S(54), S(y + 10)), f"THRESHOLD {th}", f_h,
                BONE if on else (84, 90, 100), 1.4)
        d.text((S(186), S(y + 10)), note, font=f_lab,
               fill=SMOKE if on else (64, 70, 79))

        for j, (nm, val) in enumerate((("precision", prec), ("recall", rec))):
            by = y + 32 + j * 18
            d.text((S(54), S(by - 2)), nm, font=f_lab,
                   fill=SMOKE if on else (64, 70, 79))
            d.rectangle([S(118), S(by), S(258), S(by + 9)], fill=(24, 27, 33))
            w = 140 * val
            d.rectangle([S(118), S(by), S(118 + w), S(by + 9)],
                        fill=BLOOD if (on and nm == "recall") else
                        ((110, 117, 128) if on else (44, 48, 56)))
            d.text((S(266), S(by - 3)), f"{val:.4f}", font=f_lab,
                   fill=BONE if on else (70, 76, 85))

        d.text((S(54), S(y + 68)), f"caught {caught} of 374 churners",
               font=f_lab, fill=BLOOD if on else (64, 70, 79))
        y += 96

    px = 376
    d.line([S(px - 20), S(96), S(px - 20), S(286)], fill=EDGE, width=S(1))
    val = 0.8401 * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.4f}", font=f_big, fill=BONE)
    d.text((S(px + 2), S(156)), "ROC AUC", font=f_lab, fill=ASH)
    if t > 0.5:
        d.text((S(px + 2), S(176)), "was 0.5000 — chance,", font=f_lab, fill=BLOOD)
        d.text((S(px + 2), S(190)), "on 5 invented rows", font=f_lab, fill=BLOOD)
    d.line([S(px), S(210), S(px + 214), S(210)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["7,032 rows · 26.6% churn",
                                  "tenure          -1.24",
                                  "Contract 2yr    -0.62",
                                  "Fiber optic     +0.36"]):
            d.text((S(px), S(222 + k * 17)), line, font=f_lab,
                   fill=SMOKE if k == 0 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 09 · House_price_prediction — three measured variants
# ═════════════════════════════════════════════════════════════════════════
def scene_house(d, t, raw):
    f_big = font(F_UI, 44)
    f_lab = font(F_MONO, 9)
    f_h = font(F_MONO_B, 10)
    f_v = font(F_UI, 14)

    rows = [("cleaned + log target", 0.4263, 12),
            ("+ log areas, age", 0.5105, 12),
            ("+ city", 0.7086, 55)]
    left, right = 182, 362
    y = 120
    for i, (name, r2, feats) in enumerate(rows):
        p = stagger(t, i, len(rows), 0.6)
        hot = (i == 2)
        tw = tracked_w(d, name, f_lab, 1.0)
        tracked(d, (S(left - 12) - tw, S(y)), name, f_lab,
                BONE if hot else SMOKE, 1.0)
        d.rectangle([S(left), S(y - 2), S(right), S(y + 11)], fill=(24, 27, 33))
        w = (right - left) * r2 * p
        d.rectangle([S(left), S(y - 2), S(left + w), S(y + 11)],
                    fill=BLOOD if hot else (72, 79, 90))
        if p > 0.55:
            d.text((S(left + w + 8), S(y - 4)), f"{r2:.4f}", font=f_v,
                   fill=BONE if hot else SMOKE)
            d.text((S(left + w + 54), S(y)), f"{feats} feats", font=f_lab,
                   fill=(70, 76, 85))
        y += 44
    d.text((S(left), S(y - 6)), "R² on a held-out 20%", font=f_lab,
           fill=(70, 76, 85))

    px = 440
    d.line([S(px - 22), S(96), S(px - 22), S(286)], fill=EDGE, width=S(1))
    val = 22.4 + (13.2 - 22.4) * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.1f}%", font=f_big, fill=BONE)
    d.text((S(px + 2), S(156)), "median error", font=f_lab, fill=ASH)
    if t > 0.5:
        d.text((S(px + 2), S(176)), "was 22.4%", font=f_lab, fill=BLOOD)
    d.line([S(px), S(196), S(px + 150), S(196)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["MAE  147k → 96k",
                                  "RMSE 995k → 154k",
                                  "4,505 of 4,600 rows",
                                  "44 cities"]):
            d.text((S(px), S(208 + k * 17)), line, font=f_lab,
                   fill=SMOKE if k < 2 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 10 · sonar_rock-vs-mine-prediction — what one small split is worth
#
# 208 samples means a 10% test set is 21 rows, so accuracy moves 4.76 points
# per sample and can only land on a multiple of 1/21. Each bar below is one
# of those attainable values, counted over 200 seeds of the same split.
# ═════════════════════════════════════════════════════════════════════════
SONAR_HIST = [(0.400, 0), (0.448, 2), (0.495, 0), (0.543, 0), (0.590, 14),
              (0.638, 21), (0.686, 28), (0.733, 50), (0.781, 31), (0.828, 37),
              (0.876, 13), (0.924, 4)]
SONAR_BIN = 0.0476
CV_LO, CV_HI = 0.7477, 0.7778


def scene_sonar(d, t, raw):
    f_lab = font(F_MONO, 9)
    f_big = font(F_UI, 42)
    f_h = font(F_MONO_B, 10)

    lo, hi = 0.42, 1.00
    left, right = 52, 398
    base, top = 266, 116
    peak = 50

    def mx(a):
        return left + (a - lo) / (hi - lo) * (right - left)

    # axis ticks
    for a in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        x = mx(a)
        d.line([S(x), S(base), S(x), S(base + 4)], fill=EDGE, width=S(1))
        lab = f"{int(a*100)}"
        d.text((S(x) - d.textlength(lab, font=f_lab) / 2, S(base + 9)),
               lab, font=f_lab, fill=ASH)
    d.line([S(left), S(base), S(right), S(base)], fill=EDGE, width=S(1))

    # the cross-validated estimate: a narrow band, drawn behind the bars
    if t > 0.45:
        a = min((t - 0.45) / 0.3, 1.0)
        x0, x1 = mx(CV_LO), mx(CV_HI)
        col = tuple(int(VOID[i] + (BLOOD[i] - VOID[i]) * 0.30 * a) for i in range(3))
        d.rectangle([S(x0), S(top - 10), S(x1), S(base)], fill=col)

    # histogram of 200 single-split results
    for i, (blo, count) in enumerate(SONAR_HIST):
        if not count:
            continue
        p = stagger(t, i, len(SONAR_HIST), 0.62)
        if p <= 0:
            continue
        h = (count / peak) * (base - top) * p
        x0, x1 = mx(blo), mx(blo + SONAR_BIN)
        d.rectangle([S(x0 + 1), S(base - h), S(x1 - 1), S(base)],
                    fill=(78, 85, 96))
        d.rectangle([S(x0 + 1), S(base - h), S(x1 - 1), S(base - h + 2)],
                    fill=SMOKE)

    # CV interval edges, drawn over the bars so the narrow band is the thing
    # you actually see against the spread behind it
    if t > 0.45:
        x0, x1 = mx(CV_LO), mx(CV_HI)
        for x in (x0, x1):
            d.line([S(x), S(top - 10), S(x), S(base)], fill=BLOOD, width=S(1))
        lab = "CV"
        d.text((S((x0 + x1) / 2) - d.textlength(lab, font=f_lab) / 2,
                S(top - 24)), lab, font=f_lab, fill=BLOOD)

    # the full span one split can land on
    if t > 0.75:
        sy = top - 22
        d.line([S(mx(0.4762)), S(sy), S(mx(0.9524)), S(sy)],
               fill=(110, 117, 128), width=S(1))
        for x in (mx(0.4762), mx(0.9524)):
            d.line([S(x), S(sy - 4), S(x), S(sy + 4)],
                   fill=(110, 117, 128), width=S(1))
        d.text((S(mx(0.60)), S(sy - 16)), "one split lands anywhere here",
               font=f_lab, fill=SMOKE)

    d.text((S(left), S(base + 24)), "accuracy on a single 21-row test set, 200 seeds",
           font=f_lab, fill=(70, 76, 85))

    # right panel
    px = 430
    d.line([S(px - 20), S(96), S(px - 20), S(286)], fill=EDGE, width=S(1))
    val = 76.3 * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.1f}%", font=f_big, fill=BONE)
    d.text((S(px + 2), S(152)), "± 5.4   50-fold CV", font=f_lab, fill=ASH)
    if t > 0.5:
        tracked(d, (S(px), S(174)), "ONE SPLIT SAYS", f_h, BLOOD, 1.2)
        d.text((S(px + 2), S(192)), "47.6%  to  95.2%", font=f_lab, fill=BLOOD)
    d.line([S(px), S(214), S(px + 160), S(214)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["208 rows · 60 bands",
                                  "baseline      53.4%",
                                  "train-test gap +14.4"]):
            d.text((S(px), S(226 + k * 17)), line, font=f_lab,
                   fill=SMOKE if k == 0 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 11 · Chatbot_customer_satisfaction — the lexicon the model learned
#
# No sentiment word list was supplied anywhere. These weights come only from
# the labels, which is why `plot` and `script` land among the most negative
# terms: people reach for those nouns to explain why a film failed.
# ═════════════════════════════════════════════════════════════════════════
LEXICON = [("bad", -3.646), ("worst", -2.608), ("boring", -2.224),
           ("plot", -2.051), ("stupid", -1.874), ("script", -1.873),
           ("waste", -1.762), ("best", 1.398), ("excellent", 1.531),
           ("perfect", 1.566), ("hilarious", 1.570), ("great", 2.039)]


def scene_sentiment(d, t, raw):
    f_w = font(F_MONO, 9)
    f_big = font(F_UI, 42)
    f_h = font(F_MONO_B, 10)

    cx, scale = 238, 40.0
    y = 106
    step = 15

    d.line([S(cx), S(y - 6), S(cx), S(y + step * len(LEXICON) - 4)],
           fill=EDGE, width=S(1))

    for i, (word, wt) in enumerate(LEXICON):
        p = stagger(t, i, len(LEXICON), 0.6)
        if p <= 0:
            y += step
            continue
        length = abs(wt) * scale * p
        neg = wt < 0
        x0, x1 = (cx - length, cx) if neg else (cx, cx + length)
        d.rectangle([S(x0), S(y), S(x1), S(y + 9)],
                    fill=BLOOD if neg else (150, 157, 168))
        if p > 0.6:
            lab = f"{word} {wt:+.2f}"
            lw = d.textlength(lab, font=f_w)
            if neg:
                d.text((S(x0) - lw - S(7), S(y - 1)), lab, font=f_w, fill=SMOKE)
            else:
                d.text((S(x1) + S(7), S(y - 1)), lab, font=f_w, fill=SMOKE)
        y += step

    d.text((S(cx - 92), S(y + 6)), "learned from labels alone — no word list given",
           font=f_w, fill=(70, 76, 85))

    px = 436
    d.line([S(px - 20), S(96), S(px - 20), S(286)], fill=EDGE, width=S(1))
    val = 86.3 * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.1f}%", font=f_big, fill=BONE)
    d.text((S(px + 2), S(152)), "± 1.1   5-fold CV", font=f_w, fill=ASH)
    if t > 0.5:
        tracked(d, (S(px), S(176)), "ROC AUC 0.939", f_h, BLOOD, 1.2)
    d.line([S(px), S(198), S(px + 150), S(198)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["2,000 reviews, balanced",
                                  "baseline       50.0%",
                                  "6,000 tf-idf terms",
                                  "F1             0.863"]):
            d.text((S(px), S(210 + k * 17)), line, font=f_w,
                   fill=SMOKE if k == 0 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 12 · llm-gateway-rag — hybrid retrieval closes the gap to 1.000
# ═════════════════════════════════════════════════════════════════════════
def scene_gateway(d, t, raw):
    f_w = font(F_MONO, 9)
    f_big = font(F_UI, 42)
    f_h = font(F_MONO_B, 10)
    f_v = font(F_UI, 13)

    groups = [("all queries", 0.873, 1.000), ("identifier-only", 0.722, 1.000)]
    left, right = 150, 392
    y = 120
    for gi, (name, dense, hybrid) in enumerate(groups):
        tracked(d, (S(40), S(y - 2)), name, f_h, SMOKE, 1.0)
        for bi, (lab, val, col) in enumerate((("dense", dense, (72, 79, 90)),
                                              ("hybrid", hybrid, BLOOD))):
            p = stagger(t, gi * 2 + bi, 4, 0.6)
            by = y + 20 + bi * 20
            d.text((S(52), S(by - 1)), lab, font=f_w, fill=ASH)
            d.rectangle([S(left), S(by), S(right), S(by + 11)], fill=(24, 27, 33))
            w = (right - left) * val * p
            d.rectangle([S(left), S(by), S(left + w), S(by + 11)], fill=col)
            if p > 0.6:
                d.text((S(left + w + 8), S(by - 3)), f"{val:.3f}", font=f_v,
                       fill=BONE if bi else SMOKE)
        y += 86
    d.text((S(40), S(y - 6)), "recall@5 over 102 labelled questions, 227 chunks",
           font=f_w, fill=(70, 76, 85))

    px = 448
    d.line([S(px - 22), S(96), S(px - 22), S(286)], fill=EDGE, width=S(1))
    val = 156.8 * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.0f}", font=f_big, fill=BONE)
    d.text((S(px + 78), S(126)), "req/s", font=f_w, fill=ASH)
    d.text((S(px + 2), S(152)), "chat throughput", font=f_w, fill=ASH)
    if t > 0.5:
        d.text((S(px + 2), S(168)), "was 20.6 before backpressure", font=f_w, fill=BLOOD)
    d.line([S(px), S(188), S(px + 150), S(188)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["p95          460 ms",
                                  "594 tests, 97% cov",
                                  "0 failures in 2,100",
                                  "reqs, provider killed"]):
            d.text((S(px), S(200 + k * 17)), line, font=f_w,
                   fill=SMOKE if k < 2 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 13 · vision-rl-navigation — where the learned policy loses
# ═════════════════════════════════════════════════════════════════════════
NAV = [("nominal", 1.000, 0.937, True), ("sparse", 1.000, 0.980, False),
       ("large", 1.000, 0.970, False), ("dense", 0.890, 0.730, True),
       ("narrow", 0.850, 0.682, True), ("dynamic", 0.880, 0.860, False),
       ("dyn_dense", 0.820, 0.710, True)]


def scene_nav(d, t, raw):
    f_w = font(F_MONO, 8)
    f_big = font(F_UI, 40)
    f_h = font(F_MONO_B, 10)

    left, right = 44, 404
    base, top = 250, 112
    slot = (right - left) / len(NAV)
    for i, (name, cls, learned, sig) in enumerate(NAV):
        p = stagger(t, i, len(NAV), 0.6)
        x0 = left + slot * i + slot * 0.14
        bw = slot * 0.33
        for bi, (val, col) in enumerate(((cls, (96, 104, 116)),
                                         (learned, BLOOD))):
            h = ((val - 0.6) / 0.42) * (base - top) * p
            bx = x0 + bi * bw
            d.rectangle([S(bx), S(base - h), S(bx + bw - 2), S(base)], fill=col)
        lw = d.textlength(name, font=f_w)
        d.text((S(x0 + bw) - lw / 2, S(base + 8)), name, font=f_w, fill=ASH)
        if sig and p > 0.7:
            d.ellipse([S(x0 + bw - 2), S(top - 14), S(x0 + bw + 2), S(top - 10)],
                      fill=BLOOD)
    d.line([S(left), S(base), S(right), S(base)], fill=EDGE, width=S(1))
    d.text((S(left), S(base + 24)), "success rate · 100 held-out worlds · 6 seeds",
           font=f_w, fill=(70, 76, 85))
    d.rectangle([S(left), S(top - 34), S(left + 10), S(top - 28)], fill=(96, 104, 116))
    d.text((S(left + 16), S(top - 37)), "classical", font=f_w, fill=SMOKE)
    d.rectangle([S(left + 76), S(top - 34), S(left + 86), S(top - 28)], fill=BLOOD)
    d.text((S(left + 92), S(top - 37)), "learned", font=f_w, fill=SMOKE)
    d.text((S(left + 156), S(top - 37)), "• significant", font=f_w, fill=BLOOD)

    px = 440
    d.line([S(px - 22), S(96), S(px - 22), S(286)], fill=EDGE, width=S(1))
    d.text((S(px), S(104)), "0 of 7", font=f_big, fill=BONE)
    d.text((S(px + 2), S(150)), "conditions where the", font=f_w, fill=ASH)
    d.text((S(px + 2), S(164)), "learned policy wins", font=f_w, fill=ASH)
    d.line([S(px), S(184), S(px + 154), S(184)], fill=EDGE, width=S(1))
    if t > 0.6:
        for k, line in enumerate(["worst gap  narrow",
                                  "           -0.168",
                                  "61 experiments",
                                  "exact permutation tests"]):
            d.text((S(px), S(196 + k * 17)), line, font=f_w,
                   fill=BLOOD if k == 1 else (SMOKE if k > 1 else ASH))


# ═════════════════════════════════════════════════════════════════════════
# 14 · emotionedge-cpp — CPU to GPU, per stage
# ═════════════════════════════════════════════════════════════════════════
EDGE_STAGES = [("emotion fusion", 227, 47), ("ASR decode", 248, 32),
               ("translation", 266, 57), ("TTS first chunk", 340, 54)]


def scene_edge(d, t, raw):
    f_w = font(F_MONO, 9)
    f_big = font(F_UI, 40)
    f_h = font(F_MONO_B, 10)

    left, right = 166, 392
    y = 116
    scale = (right - left) / 360.0
    for i, (name, cpu, gpu) in enumerate(EDGE_STAGES):
        p = stagger(t, i, len(EDGE_STAGES), 0.6)
        tw = tracked_w(d, name, f_w, 0.8)
        tracked(d, (S(left - 12) - tw, S(y + 4)), name, f_w, SMOKE, 0.8)
        d.rectangle([S(left), S(y), S(left + cpu * scale), S(y + 8)],
                    fill=(62, 68, 78))
        gw = gpu * scale * p
        d.rectangle([S(left), S(y + 10), S(left + gw), S(y + 18)], fill=BLOOD)
        if p > 0.6:
            d.text((S(left + cpu * scale + 6), S(y - 2)), f"{cpu}", font=f_w,
                   fill=ASH)
            d.text((S(left + gw + 6), S(y + 8)), f"{gpu} ms", font=f_w, fill=BONE)
        y += 34
    d.text((S(left), S(y + 2)), "p50 per stage · grey CPU · red GPU",
           font=f_w, fill=(70, 76, 85))

    px = 440
    d.line([S(px - 22), S(96), S(px - 22), S(286)], fill=EDGE, width=S(1))
    val = 1262 + (365 - 1262) * ease(t / 0.8)
    d.text((S(px), S(104)), f"{val:.0f}", font=f_big, fill=BONE)
    d.text((S(px + 86), S(126)), "ms", font=f_w, fill=ASH)
    d.text((S(px + 2), S(150)), "end-to-end p50", font=f_w, fill=ASH)
    if t > 0.5:
        d.text((S(px + 2), S(166)), "was 1262 on CPU", font=f_w, fill=BLOOD)
    d.line([S(px), S(186), S(px + 154), S(186)], fill=EDGE, width=S(1))
    if t > 0.7:
        for k, line in enumerate(["p95 631  (budget 800)",
                                  "5 s CPU time, was 51 s",
                                  "RAVDESS WER   0.042",
                                  "C++20, ONNX Runtime"]):
            d.text((S(px), S(198 + k * 17)), line, font=f_w,
                   fill=SMOKE if k < 2 else ASH)


# ═════════════════════════════════════════════════════════════════════════
# 15 · neuro-sathi — built, but deliberately not validated
# ═════════════════════════════════════════════════════════════════════════
LANGS = [("Hindi", True), ("Assamese", False), ("Bengali", False),
         ("Nepali", False), ("Manipuri", False), ("Bodo", False)]


def scene_sathi(d, t, raw):
    f_w = font(F_MONO, 9)
    f_big = font(F_UI, 40)
    f_h = font(F_MONO_B, 10)

    tracked(d, (S(44), S(104)), "LANGUAGE PACKS", f_h, SMOKE, 1.5)
    y = 126
    for i, (name, ok) in enumerate(LANGS):
        p = stagger(t, i, len(LANGS), 0.6)
        if p <= 0:
            y += 22
            continue
        col = BONE if ok else (70, 76, 85)
        d.rectangle([S(44), S(y), S(50), S(y + 10)],
                    fill=BONE if ok else (44, 48, 56))
        d.text((S(60), S(y - 1)), name, font=f_w, fill=col)
        d.text((S(150), S(y - 1)),
               "reviewed" if ok else "hidden until reviewed", font=f_w,
               fill=SMOKE if ok else (70, 76, 85))
        y += 19

    d.line([S(44), S(y + 8), S(380), S(y + 8)], fill=EDGE, width=S(1))
    if t > 0.6:
        tracked(d, (S(44), S(y + 20)), "DEVIATION ALERTS", f_h, SMOKE, 1.5)
        d.text((S(44), S(y + 40)), "last 7 days vs previous 28, beyond 2 SD",
               font=f_w, fill=ASH)
        d.text((S(44), S(y + 56)), "rules only — no trained model yet",
               font=f_w, fill=BLOOD)

    px = 440
    d.line([S(px - 22), S(96), S(px - 22), S(286)], fill=EDGE, width=S(1))
    d.text((S(px), S(104)), "1 of 6", font=f_big, fill=BONE)
    d.text((S(px + 2), S(150)), "packs native-reviewed", font=f_w, fill=ASH)
    d.line([S(px), S(170), S(px + 154), S(170)], fill=EDGE, width=S(1))
    if t > 0.6:
        for k, line in enumerate(["FastAPI · Flutter · Next",
                                  "Postgres RLS · SQLCipher",
                                  "offline-first, syncs on",
                                  "reconnect"]):
            d.text((S(px), S(182 + k * 17)), line, font=f_w,
                   fill=SMOKE if k < 2 else ASH)
    if t > 0.8:
        tracked(d, (S(px), S(256)), "DOES NOT DIAGNOSE", f_h, BLOOD, 1.2)


CARDS = [
    # Starred repos only, strongest measured work first, in-progress last.
    ("llm-gateway-rag", scene_gateway, "01", "llm-gateway-rag",
     "one 12-vCPU laptop shared by every component"),
    ("vision-rl-navigation", scene_nav, "02", "vision-rl-navigation",
     "a strong classical planner is a hard baseline to beat"),
    ("emotionedge-cpp", scene_edge, "03", "emotionedge-cpp",
     "RTX 5070 Ti laptop · jfk.wav · C++20, no Python at runtime"),
    ("symmetrynet-equivariant-gnn", scene_symmetry, "04", "symmetrynet-equivariant-gnn",
     "rotate the molecule — the prediction does not move"),
    ("gst-eval-harness", scene_gst_eval, "05", "gst-eval-harness",
     "slab accuracy across 5 identical runs · same prompt, same model"),
    ("gst-resilient-agent", scene_agent, "06", "gst-resilient-agent",
     "retrieval recall@k over 28 gazette-derived golden rows"),
    ("register-aware-translation", scene_register, "07", "register-aware-translation",
     "formality is a dial, not a coin flip · 20 languages, 1,369 rules, ~1ms"),
    ("chest-xray-classifier", scene_xray, "08", "chest-xray-classifier",
     "3,175 test images · research prototype, not a medical device"),
    ("smart-healthcare-triage", scene_triage, "09", "smart-healthcare-triage",
     "symptom text → urgency, offline · follow-ups can escalate"),
    ("neuro-sathi", scene_sathi, "10", "neuro-sathi",
     "built and unvalidated — clinical studies still required"),
    ("llm-serving-unit-economics", scene_serving, "11", "llm-serving-unit-economics",
     "every number in this repo is absent rather than estimated"),
]

if __name__ == "__main__":
    print("project output cards")
    for name, scene, idx, title, footer in CARDS:
        render(name, scene, idx, title, footer)
    total = sum(os.path.getsize(os.path.join(OUT, f))
                for f in os.listdir(OUT)) / 1024
    print(f"\n  {'TOTAL assets/cards':30} {total:6.0f} KB")
