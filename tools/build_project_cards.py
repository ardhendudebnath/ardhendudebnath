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


CARDS = [
    ("gst-eval-harness", scene_gst_eval, "01", "gst-eval-harness",
     "slab accuracy across 5 identical runs · same prompt, same model"),
    ("gst-resilient-agent", scene_agent, "02", "gst-resilient-agent",
     "retrieval recall@k over 28 gazette-derived golden rows"),
    ("register-aware-translation", scene_register, "03", "register-aware-translation",
     "formality is a dial, not a coin flip · 20 languages, 1,369 rules, ~1ms"),
    ("symmetrynet-equivariant-gnn", scene_symmetry, "04", "symmetrynet-equivariant-gnn",
     "rotate the molecule — the prediction does not move"),
    ("chest-xray-classifier", scene_xray, "05", "chest-xray-classifier",
     "3,175 test images · research prototype, not a medical device"),
    ("smart-healthcare-triage", scene_triage, "06", "smart-healthcare-triage",
     "symptom text → urgency, offline · follow-ups can escalate"),
    ("llm-serving-unit-economics", scene_serving, "07", "llm-serving-unit-economics",
     "every number in this repo is absent rather than estimated"),
]

if __name__ == "__main__":
    print("project output cards")
    for name, scene, idx, title, footer in CARDS:
        render(name, scene, idx, title, footer)
    total = sum(os.path.getsize(os.path.join(OUT, f))
                for f in os.listdir(OUT)) / 1024
    print(f"\n  {'TOTAL assets/cards':30} {total:6.0f} KB")
