"""
Build every generated asset for the profile.

    python tools/build_assets.py

Outputs into assets/:
    <name>.jpg            optimised artwork for the WebGL page
    <name>-depth.jpg      derived depth map, drives the parallax shader
    banner.webp           animated 3D parallax banner for the README
    banner.jpg            static first frame, fallback
    plates.jpg            the three plates as 3D perspective cards

The banner is rendered as real warped frames rather than an SVG with an
embedded image: GitHub serves README images through camo under a strict
CSP, which can block data: URIs inside an SVG. Warped frames always render.

SOURCE_DIR points at the original full-resolution PNGs. If they are gone the
script falls back to the optimised copies already in assets/, which is enough
to rebuild the banner and plates.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "3d", "assets")
SOURCE_DIR = r"C:\Users\ardhendudebnath\Downloads\Mobile Devices"

FILES = {
    "hero":     "60f6fe4d-5608-410e-a940-c1545d949292.png",
    "deadlift": "2b00c6e2-2dc9-427f-b45b-ab13ad911951.png",
    "flex":     "98f427a8-c5e6-42e9-a211-333faba05f90.png",
}

FONT_DISPLAY = r"C:\Windows\Fonts\impact.ttf"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"

BONE = (234, 231, 224)
BLOOD = (204, 41, 54)
VOID = (7, 8, 10)

os.makedirs(OUT, exist_ok=True)


# ── small helpers ────────────────────────────────────────────────────────
def to_im(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def blur(a, r):
    return np.asarray(to_im(a).filter(ImageFilter.GaussianBlur(r)), np.float32) / 255.0


def dilate(a, size):
    return np.asarray(to_im(a).filter(ImageFilter.MaxFilter(size)), np.float32) / 255.0


def norm(a, lo=2, hi=98):
    x, y = np.percentile(a, lo), np.percentile(a, hi)
    return np.zeros_like(a) if y - x < 1e-6 else np.clip((a - x) / (y - x), 0, 1)


def depth_map(img, width=512):
    """Heuristic depth from a high-contrast ink drawing.

    Three cues, all cheap: dense cross-hatching marks the figure, mid-grey
    marks skin against blown-out or solid-black background, and the subject
    always occupies the centre. Holes the black hair punches into the figure
    get closed by a grey dilation — an unclosed hole dents the surface.
    """
    g = ImageOps.grayscale(img)
    w, h = g.size
    sw = width
    sh = max(1, round(h * sw / w))
    a = np.asarray(g.resize((sw, sh), Image.LANCZOS), np.float32) / 255.0

    detail = norm(blur(np.clip(np.abs(a - blur(a, 3)) * 6.0, 0, 1), 20))
    mid = norm(blur(np.clip(1.0 - np.abs(a - 0.5) * 2.0, 0, 1), 24))

    yy, xx = np.mgrid[0:sh, 0:sw]
    r = np.sqrt(((xx - sw * 0.5) / (sw * 0.58)) ** 2 +
                ((yy - sh * 0.52) / (sh * 0.66)) ** 2)
    central = np.clip(1.0 - r, 0, 1) ** 1.15

    d = norm(0.42 * central + 0.36 * detail + 0.22 * mid)
    d = norm(blur(dilate(d, 19), 12))
    return norm(blur(0.74 * d + 0.26 * central, 6))


def source(name):
    p = os.path.join(SOURCE_DIR, FILES[name])
    if os.path.exists(p):
        return Image.open(p).convert("RGB")
    p = os.path.join(OUT, f"{name}.jpg")
    if os.path.exists(p):
        print(f"  (using assets/{name}.jpg — original not found)")
        return Image.open(p).convert("RGB")
    sys.exit(f"missing source for '{name}'")


def tracked(draw, xy, text, font, fill, tracking=0):
    """PIL has no letter-spacing, so step the pen manually."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def tracked_width(draw, text, font, tracking=0):
    return sum(draw.textlength(c, font=font) + tracking for c in text) - tracking


# ── 1. artwork + depth maps ──────────────────────────────────────────────
def build_artwork():
    print("artwork + depth maps")
    for name in FILES:
        img = source(name)
        w, h = img.size
        s = 1440 / max(w, h)
        exp = img.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else img
        exp.save(os.path.join(OUT, f"{name}.jpg"), quality=82, optimize=True, progressive=True)
        to_im(depth_map(img)).save(os.path.join(OUT, f"{name}-depth.jpg"),
                                   quality=88, optimize=True)
        print(f"  {name:10} {exp.size}")


# ── 2. animated parallax banner ──────────────────────────────────────────
# 890px is roughly how wide GitHub renders a README image, so this is native
# size — no upscaling, no wasted bytes. Every frame is a full photographic
# redraw, so FRAMES and QUALITY are the two knobs that set the file size.
BANNER_W, BANNER_H = 890, 276
MARGIN = 24                    # overscan so the warp never samples off-image
FRAMES = 16
FRAME_MS = 100                 # 1.6s loop
QUALITY = 72
AMP_X, AMP_Y = 11.0, 4.0       # pixels of sway at full depth
# Layout above is the design space; BSCALE only changes export resolution.
# 890px is GitHub's README render width, so 1.0 is sharp at 1x and soft at 2x.
BSCALE = 1.0


def warp(src, dmap, ax, ay):
    """Backward bilinear warp: near pixels travel further than far ones."""
    h, w = dmap.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    disp = (dmap - 0.5) * 2.0
    sx = np.clip(xx + ax * disp, 0, w - 1.001)
    sy = np.clip(yy + ay * disp, 0, h - 1.001)

    x0 = sx.astype(np.int32); x1 = x0 + 1
    y0 = sy.astype(np.int32); y1 = y0 + 1
    fx = (sx - x0)[..., None]
    fy = (sy - y0)[..., None]

    top = src[y0, x0] + (src[y0, x1] - src[y0, x0]) * fx
    bot = src[y1, x0] + (src[y1, x1] - src[y1, x0]) * fx
    return top + (bot - top) * fy


def banner_overlay(w, h, sc=1.0):
    """Static furniture — title, rules, crop marks — drawn once and reused.

    Identical on every frame, so it costs almost nothing in the animation.
    Coordinates are written in the 890x276 design space and scaled by `sc`.
    """
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    def q(v):
        return round(v * sc)

    f_name = ImageFont.truetype(FONT_DISPLAY, q(48))
    # Small type has to survive lossy inter-frame compression, so the role
    # line is set larger and brighter than the design would otherwise want.
    f_role = ImageFont.truetype(FONT_MONO, q(14))
    f_tiny = ImageFont.truetype(FONT_MONO, q(11))

    pad = q(36)
    base_y = h - q(112)       # clears the hairline frame drawn at h - 20

    # Extruded name: stacked offset copies build the side wall.
    name = "ARDHENDU DEBNATH"
    steps = [(13, 13, (7, 7, 7)), (11, 11, (12, 12, 12)), (9, 9, (18, 18, 17)),
             (7, 7, (32, 31, 29)), (5, 5, (58, 56, 52)), (3, 3, (94, 91, 85)),
             (2, 2, (140, 136, 128)), (1, 1, (186, 182, 173))]
    for dx, dy, col in steps:
        tracked(d, (pad + q(dx), base_y + q(dy)), name, f_name, col, 1.5 * sc)
    tracked(d, (pad, base_y), name, f_name, BONE, 1.5 * sc)

    # Role line, blood-coloured separators.
    y = base_y + q(66)
    x = pad + q(2)
    for i, part in enumerate(["MACHINE LEARNING", "ENGINEER", "INDIA"]):
        if i:
            x = tracked(d, (x, y), "  /  ", f_role, BLOOD, 3.4 * sc)
        x = tracked(d, (x, y), part, f_role, (226, 229, 234), 3.4 * sc)

    # Top corners.
    d.rectangle([pad, q(34), pad + q(7), q(41)], fill=BLOOD)
    tracked(d, (pad + q(17), q(32)), "ARDHENDUDEBNATH", f_tiny,
            (150, 156, 165), 2.6 * sc)
    label = "INK & DEPTH"
    lw = tracked_width(d, label, f_tiny, 2.6 * sc)
    tracked(d, (w - pad - lw, q(32)), label, f_tiny, (150, 156, 165), 2.6 * sc)

    # Hairline frame + printer's crop marks.
    lw1 = max(1, round(sc))
    d.rectangle([pad - q(20), q(20), w - pad + q(20), h - q(20)],
                outline=(58, 63, 72), width=lw1)
    for cx, cy, sx, sy in ((pad - q(20), q(20), 1, 1),
                           (w - pad + q(20), q(20), -1, 1),
                           (pad - q(20), h - q(20), 1, -1),
                           (w - pad + q(20), h - q(20), -1, -1)):
        d.line([cx, cy, cx + q(16) * sx, cy], fill=BONE, width=lw1)
        d.line([cx, cy, cx, cy + q(16) * sy], fill=BONE, width=lw1)

    return layer


def build_banner():
    print("animated parallax banner")
    hero = source("hero")
    w, h = hero.size

    BW, BH = round(BANNER_W * BSCALE), round(BANNER_H * BSCALE)
    MG = round(MARGIN * BSCALE)

    # Wide crop biased upward, so the head and raised arm survive.
    sw, sh = BW + MG * 2, BH + MG * 2
    ch = round(w / (sw / sh))
    top = round((h - ch) * 0.34)
    crop = hero.crop((0, top, w, top + ch)).resize((sw, sh), Image.LANCZOS)

    src = np.asarray(crop, np.float32) / 255.0
    dm = depth_map(crop, width=sw)
    dm = np.asarray(Image.fromarray((dm * 255).astype(np.uint8)).resize((sw, sh),
                    Image.LANCZOS), np.float32) / 255.0

    # Static grade layers, identical every frame so WebP deltas stay tiny.
    yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
    nx = (xx / BW - 0.5) * 2.0
    ny = (yy / BH - 0.5) * 2.0
    vignette = np.clip(1.0 - (nx * nx * 0.34 + ny * ny * 0.46), 0, 1)[..., None]
    bed = np.clip(1.0 - 0.72 * np.exp(-(((nx + 0.62) ** 2) * 2.4 +
                                        ((ny - 0.66) ** 2) * 3.0)), 0, 1)[..., None]
    # Darken the top strip so the corner labels read over the blown-out ceiling.
    bed = bed * np.clip(1.0 - 0.52 * np.exp(
        -((yy / (44.0 * BSCALE)) ** 2)), 0, 1)[..., None]
    scan = np.ones((BH, BW, 1), np.float32)
    scan[1::max(2, round(3 * BSCALE))] = 0.82
    rng = np.random.default_rng(7)
    # Grain is the single most expensive thing in the file — keep it faint.
    grain = (rng.random((BH, BW, 1), dtype=np.float32) - 0.5) * 0.015

    overlay = banner_overlay(BW, BH, BSCALE)

    frames = []
    for i in range(FRAMES):
        t = 2 * np.pi * i / FRAMES
        # Figure-eight orbit reads as depth, not as a slide.
        ax = AMP_X * BSCALE * np.sin(t)
        ay = AMP_Y * BSCALE * np.sin(2 * t)

        f = warp(src, dm, ax, ay)[MG:MG + BH, MG:MG + BW]

        # Ink grade: crush toward the bone/void ramp, keep it monochrome.
        lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
        f = np.clip((lum[..., None] - 0.5) * 1.14 + 0.47, 0, 1)
        f = np.clip(f * vignette * bed * scan + grain, 0, 1)

        # Same grade as the WebGL page: monochrome with a faint blood lift
        # through the midtones, so banner and site read as one system.
        rgb = np.repeat(f, 3, axis=2)
        mids = 1.0 - np.abs(f * 2.0 - 1.0)
        rgb = np.clip(rgb + mids * np.array([0.058, 0.006, 0.013], np.float32), 0, 1)
        frames.append(Image.fromarray((rgb * 255).astype(np.uint8), "RGB"))

    frames = [Image.alpha_composite(fr.convert("RGBA"), overlay).convert("RGB")
              for fr in frames]

    webp = os.path.join(OUT, "banner.webp")
    frames[0].save(webp, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=FRAME_MS, loop=0, quality=QUALITY, method=6)
    frames[0].save(os.path.join(OUT, "banner.jpg"), quality=84,
                   optimize=True, progressive=True)
    print(f"  banner.webp  {FRAMES} frames  {os.path.getsize(webp)/1024:.0f} KB")


# ── 3. the three plates as 3D perspective cards ──────────────────────────
def find_coeffs(dst, src_quad):
    """Solve the 8 perspective coefficients mapping dst → src (PIL's direction)."""
    m = []
    for (x, y), (u, v) in zip(dst, src_quad):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(m, np.float64)
    B = np.array(src_quad, np.float64).reshape(8)
    return np.linalg.lstsq(A, B, rcond=None)[0]


def card(img, box_w, box_h, lean, near_right=True):
    """Tilt an image about its vertical axis into a real trapezoid."""
    img = ImageOps.contain(img, (box_w * 2, box_h * 2), Image.LANCZOS).convert("RGBA")
    img = ImageOps.expand(img, border=3, fill=(216, 212, 204, 255))   # bone edge
    sw, sh = img.size

    inset = box_h * lean
    if near_right:
        dst = [(0, inset), (box_w, 0), (box_w, box_h), (0, box_h - inset)]
    else:
        dst = [(0, 0), (box_w, inset), (box_w, box_h - inset), (0, box_h)]
    coeffs = find_coeffs(dst, [(0, 0), (sw, 0), (sw, sh), (0, sh)])

    out = img.transform((box_w, box_h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

    # Shadow cast from the card's own silhouette.
    pad = 46
    canvas = Image.new("RGBA", (box_w + pad * 2, box_h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 205), (pad, pad + 16), out.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(17))
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.paste(out, (pad, pad), out)
    return canvas


def build_plates():
    print("3D plates")
    W, H = 1240, 480
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # name, box w, box h, lean, near edge on right, x, y — y leaves room for
    # each card's cast shadow, which is 46px of padding plus a 16px drop.
    specs = [
        ("deadlift", 250, 330, 0.11, False, 40, 30),
        ("hero",     470, 300, 0.09, False, 318, 56),
        ("flex",     360, 250, 0.10, True,  832, 100),
    ]
    for name, bw, bh, lean, near_right, x, y in specs:
        art = Image.open(os.path.join(OUT, f"{name}.jpg"))
        c = card(art, bw, bh, lean, near_right)
        sheet.alpha_composite(c, (x, y))

    # Seat the cards on the void with a soft floor gradient.
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx / W - 0.5) * 2.0
    ny = (yy / H - 0.5) * 2.0
    bg = np.clip(0.055 - 0.03 * (nx * nx * 0.6 + ny * ny), 0, 1)
    base = Image.fromarray((np.dstack([bg, bg * 1.02, bg * 1.12]) * 255)
                           .astype(np.uint8), "RGB").convert("RGBA")
    out = Image.alpha_composite(base, sheet).convert("RGB")

    p = os.path.join(OUT, "plates.jpg")
    out.save(p, quality=84, optimize=True, progressive=True)
    print(f"  plates.jpg   {os.path.getsize(p)/1024:.0f} KB")


# ── 4. the portrait, graded into the ink world ───────────────────────────
# Crops are fractions of the source frame, tuned to the existing profile
# photo (2250x3001 selfie, head upper-centre). Swap the photo and these are
# the two lines to re-tune.
PORTRAIT_SRC = [
    os.path.join(ROOT, "assets", "img", "profile.JPG"),                     # after merge
    os.path.join(ROOT, "ardhendudebnath", "assets", "img", "profile.JPG"),  # the clone
]
CARD_CROP = (0.161, 0.033, 0.872, 0.700)     # 4:5, head and shoulders
AVATAR_CROP = (0.128, 0.033, 0.906, 0.616)   # 1:1, hair to below the chin


def portrait_depth(img, width=512):
    """Centrality-dominant depth. The subject is the middle of a portrait —
    the restaurant behind him is not, and this is what darkens it away."""
    g = ImageOps.grayscale(img)
    w, h = g.size
    sw = width
    sh = max(1, round(h * sw / w))
    a = np.asarray(g.resize((sw, sh), Image.LANCZOS), np.float32) / 255.0

    detail = norm(blur(np.clip(np.abs(a - blur(a, 3)) * 6.0, 0, 1), 16))
    yy, xx = np.mgrid[0:sh, 0:sw]
    r = np.sqrt(((xx - sw * 0.50) / (sw * 0.48)) ** 2 +
                ((yy - sh * 0.42) / (sh * 0.50)) ** 2)
    central = np.clip(1.0 - r, 0, 1)

    d = norm(0.70 * central + 0.30 * detail)
    return norm(blur(dilate(d, 15), 10))


def ink_portrait(crop, size):
    """Grade a photograph into the same bone-on-void world as the drawings."""
    out_w, out_h = size
    crop = crop.resize((out_w, out_h), Image.LANCZOS)

    g = ImageOps.grayscale(crop)
    a = np.asarray(g, np.float32) / 255.0

    # Local contrast, so skin and hair read as structure rather than as tone.
    a = np.clip(a + (a - blur(a, max(2, out_w // 55))) * 0.85, 0, 1)

    d = portrait_depth(crop)
    d = np.asarray(Image.fromarray((d * 255).astype(np.uint8))
                   .resize((out_w, out_h), Image.LANCZOS), np.float32) / 255.0

    # S-curve, then let depth pull the background down to near-black.
    lum = np.clip((a - 0.5) * 1.38 + 0.47, 0, 1)
    keep = np.clip((d - 0.30) / 0.32, 0, 1)
    keep = keep * keep * (3 - 2 * keep)                 # smoothstep
    lum = lum * (0.05 + 0.95 * keep)

    yy, xx = np.mgrid[0:out_h, 0:out_w].astype(np.float32)
    nx = (xx / out_w - 0.5) * 2.0
    ny = (yy / out_h - 0.5) * 2.0
    lum = lum * np.clip(1.0 - (nx * nx * 0.30 + ny * ny * 0.34), 0, 1)

    scan = np.ones((out_h, out_w), np.float32)
    scan[1::3] = 0.88
    lum = lum * scan
    lum = np.clip(lum + (np.random.default_rng(3).random(
        (out_h, out_w), dtype=np.float32) - 0.5) * 0.022, 0, 1)

    rgb = np.repeat(lum[..., None], 3, axis=2)
    mids = 1.0 - np.abs(lum[..., None] * 2.0 - 1.0)
    rgb = np.clip(rgb + mids * np.array([0.060, 0.006, 0.014], np.float32), 0, 1)
    return Image.fromarray((rgb * 255).astype(np.uint8), "RGB"), d


def build_portrait():
    print("portrait")
    path = next((p for p in PORTRAIT_SRC if os.path.exists(p)), None)
    if not path:
        print("  skipped — profile.JPG not found")
        return
    img = Image.open(path).convert("RGB")
    W, H = img.size

    def frac(box):
        x0, y0, x1, y1 = box
        return img.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))

    plate, depth = ink_portrait(frac(CARD_CROP), (880, 1100))
    plate.save(os.path.join(OUT, "portrait.jpg"), quality=84,
               optimize=True, progressive=True)
    to_im(depth).save(os.path.join(OUT, "portrait-depth.jpg"),
                      quality=88, optimize=True)

    avatar, _ = ink_portrait(frac(AVATAR_CROP), (420, 420))
    avatar.save(os.path.join(OUT, "avatar.jpg"), quality=86,
                optimize=True, progressive=True)
    print(f"  from {os.path.relpath(path, ROOT)}  ({W}x{H})")


if __name__ == "__main__":
    build_artwork()
    build_banner()
    build_plates()
    build_portrait()

    print("\nassets/")
    total = 0
    for f in sorted(os.listdir(OUT)):
        kb = os.path.getsize(os.path.join(OUT, f)) / 1024
        total += kb
        print(f"  {f:22} {kb:8.0f} KB")
    print(f"  {'TOTAL':22} {total:8.0f} KB")
