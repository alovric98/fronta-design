#!/usr/bin/env python3
"""Fronta Design - 13 s vertical (9:16) hook video for a Meta ad.

The kitchen from kuhinja-izvor.jpg is "built from zero": the space starts as a
dark technical drawing, the units are installed piece by piece, the rest of
the room and the details fill in, the LED light switches on, and the last
5 seconds hold the finished kitchen with the closing question.

    python3 render.py                      # renders kuhinja-hook-9x16.mp4
    python3 render.py --preview 2.5 9      # writes preview PNGs for given seconds

Needs: numpy, pillow, opencv-python(-headless), ffmpeg, Newsreader (bundled in
fonts/) and Inter (system font, path in SANS below).
"""
import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from elements import GLOW, GROUPS, DECOR, INSTALL

HERE = Path(__file__).resolve().parent
SRC = HERE / "kuhinja-izvor.jpg"
LOGO_SVG = HERE.parent.parent / "images" / "fronta-logo.svg"
OUT = HERE / "kuhinja-hook-9x16.mp4"

FONT_DIR = HERE / "fonts"
SERIF = FONT_DIR / "Newsreader-Regular.ttf"
SERIF_IT = FONT_DIR / "Newsreader-Italic.ttf"
SANS = Path("/usr/share/fonts/opentype/inter/Inter-Medium.otf")

FPS = 30
DURATION = 13.0
W, H = 1080, 1920

# Brand palette (css/style.css)
BG = np.array([0x1B, 0x1B, 0x1D], np.float32) / 255
TEXT = (0xED, 0xEB, 0xE8)
ACCENT = (0xC5, 0x86, 0x56)
LOGO = (0xC9, 0x97, 0x5C)

# Part of the photo shown on the stage, and where the stage sits.
CROP = (140, 50, 1960, 1530)
STAGE_W = W
STAGE_H = round(W * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0]))
STAGE_Y = 730
ZOOM0 = 1.06                      # slow pull-back during the build
COMP_W = round(STAGE_W * ZOOM0)
COMP_H = round(STAGE_H * ZOOM0)
ZOOM_FOCUS = (0.52, 0.55)         # relative point the pull-back is centred on

T_DRAW = (0.0, 1.3)               # line drawing
T_WIPE = (5.15, 6.35)             # walls, floor and details fill in
T_LIGHT = (6.55, 7.20)            # LED switches on
T_ZOOM_END = 8.0


# ---------------------------------------------------------------- helpers

def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, np.float32) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def sstep(e0, e1, x):
    return float(smoothstep(e0, e1, x))


def ease_out_back(p, s=1.25):
    p = p - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def to_comp(img, interp=cv2.INTER_AREA):
    x0, y0, x1, y1 = CROP
    return cv2.resize(img[y0:y1, x0:x1], (COMP_W, COMP_H), interpolation=interp)


def value_noise(h, w, cell, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32)
    return cv2.resize(g, (w + 3 * cell, h + 3 * cell), interpolation=cv2.INTER_CUBIC)[:h, :w]


# ---------------------------------------------------------------- layers

def draw_label_map(shape):
    """Label map at photo resolution: 0 = room/details, i+1 = GROUPS[i]."""
    h, w = shape
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    for i, (name, g) in enumerate(GROUPS.items()):
        if name.startswith("stool"):
            continue          # added by refine_stools
        for poly in g.get("poly", []):
            d.polygon(poly, fill=i + 1)
    lab = np.array(img)
    return lab


def refine_stools(P8, lab):
    """Tighten stool shells with GrabCut, then add legs drawn as thick lines."""
    names = list(GROUPS)
    h, w = lab.shape
    for name in ("stool_back", "stool_left", "stool_right"):
        idx = names.index(name) + 1
        g = GROUPS[name]
        poly = np.zeros((h, w), np.uint8)
        for p in g["poly"]:
            cv2.fillPoly(poly, [np.array(p, np.int32)], 1)
        ys, xs = np.nonzero(poly)
        x0, x1 = max(xs.min() - 40, 0), min(xs.max() + 40, w)
        y0, y1 = max(ys.min() - 40, 0), min(ys.max() + 40, h)
        pc = poly[y0:y1, x0:x1]
        gc = np.full(pc.shape, cv2.GC_BGD, np.uint8)
        gc[cv2.dilate(pc, np.ones((25, 25), np.uint8)) > 0] = cv2.GC_PR_BGD
        gc[pc > 0] = cv2.GC_PR_FGD
        gc[cv2.erode(pc, np.ones((21, 21), np.uint8)) > 0] = cv2.GC_FGD
        bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        crop = np.ascontiguousarray(P8[y0:y1, x0:x1, ::-1])
        cv2.grabCut(crop, gc, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
        fg = ((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD)).astype(np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        # keep only what the rough polygon allowed (plus a small margin)
        fg &= cv2.dilate(pc, np.ones((9, 9), np.uint8))
        lab[y0:y1, x0:x1][fg > 0] = idx
        legs = Image.fromarray(lab)
        d = ImageDraw.Draw(legs)
        for pts, width in g.get("lines", []):
            d.line(pts, fill=idx, width=width, joint="curve")
        lab[:] = np.array(legs)
    return lab


def cut_decor_footprints(P, lab):
    """Decor standing on a unit stays a wireframe until the details fill in."""
    names = list(GROUPS)
    h, w = lab.shape
    decor = np.zeros((h, w), np.uint8)
    for poly in DECOR.values():
        cv2.fillPoly(decor, [np.array(poly, np.int32)], 1)
    for name in ("counter", "peninsula", "tall", "shelves"):
        idx = names.index(name) + 1
        own = (lab == idx)
        region = own & (decor > 0)
        if not region.any():
            continue
        clean = (own & (decor == 0)).astype(np.float32)
        num = cv2.GaussianBlur(P * clean[..., None], (0, 0), 12)
        den = cv2.GaussianBlur(clean, (0, 0), 12)[..., None] + 1e-4
        est = num / den
        dist = np.linalg.norm(P - est, axis=2)
        foot = region & (dist > 0.11)
        foot = cv2.morphologyEx(foot.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        foot = cv2.dilate(foot, np.ones((5, 5), np.uint8)) > 0
        lab[foot & own] = 0
    return lab


def poly_mask(shape, polys, blur=0.0):
    h, w = shape
    m = np.zeros((h, w), np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.array(p, np.int32)], 255)
    m = m.astype(np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m


def lights_off(P):
    h, w = P.shape[:2]
    yy = np.arange(h, dtype=np.float32)[:, None]
    g_bs = poly_mask((h, w), [GLOW["backsplash"]], 6) * np.clip(1 - (yy - 612) / 175, 0, 1) ** 1.6
    g_bar = poly_mask((h, w), [GLOW["bar"]], 40) * 0.85
    g_strip = poly_mask((h, w), [GLOW["strip"]], 2)[..., None]
    gl = np.maximum(g_bs, g_bar)[..., None]
    lum = (P * np.array([0.299, 0.587, 0.114], np.float32)).sum(2, keepdims=True)
    dim = P * (1 - 0.42 * gl)
    out = dim * (1 - 0.65 * gl) + lum * (1 - 0.42 * gl) * 0.65 * gl
    out = out * (1 - g_strip) + np.array([0.33, 0.32, 0.31], np.float32) * g_strip
    return out * 0.93          # the whole room is a touch darker before the lights


def line_art(P8):
    g = cv2.cvtColor(P8, cv2.COLOR_RGB2GRAY).astype(np.float32)
    g = cv2.bilateralFilter(g, 7, 30, 7)
    blur = cv2.GaussianBlur(255 - g, (0, 0), 4)
    dodge = np.clip(g * 255 / (255 - blur + 1e-3), 0, 255)
    sketch = np.clip((255 - dodge) / 255 * 4.0, 0, 1)
    edges = cv2.Canny(cv2.GaussianBlur(P8, (0, 0), 1.6), 30, 80).astype(np.float32) / 255
    edges = cv2.GaussianBlur(edges, (0, 0), 0.8) * 1.6
    L = smoothstep(0.10, 0.70, np.clip(np.maximum(sketch, edges * 0.9), 0, 1))
    # drop isolated specks (floor texture, oven glass) but keep real lines
    n, lab, stats, _ = cv2.connectedComponentsWithStats((L > 0.25).astype(np.uint8), 8)
    keep = stats[:, cv2.CC_STAT_AREA] >= 60
    keep[0] = False
    return L * keep[lab]


def build_layers():
    P8 = np.array(Image.open(SRC).convert("RGB"))
    P = P8.astype(np.float32) / 255
    h, w = P.shape[:2]

    lab = draw_label_map((h, w))
    lab = refine_stools(P8, lab)
    lab = cut_decor_footprints(P, lab)

    L = {}
    L["on"] = to_comp(P)
    L["off"] = to_comp(lights_off(P))
    lines = to_comp(line_art(P8))
    L["lines"] = np.clip(lines * 1.35, 0, 1)

    names = list(GROUPS)
    masks = {}
    for i, name in enumerate(names):
        masks[name] = to_comp((lab == i + 1).astype(np.float32))
    L["rest"] = np.clip(1 - sum(masks.values()), 0, 1)
    L["masks"] = masks

    # Reveal order for the drawing: diagonal sweep with an organic edge.
    # Both the drawing and the room fill-in grow outward from the kitchen corner.
    yy, xx = np.mgrid[0:COMP_H, 0:COMP_W].astype(np.float32)
    cx = (1080 - CROP[0]) / (CROP[2] - CROP[0]) * COMP_W
    cy = (840 - CROP[1]) / (CROP[3] - CROP[1]) * COMP_H
    r = np.hypot((xx - cx) / COMP_W, (yy - cy) / COMP_W)
    r = r / r.max()
    L["draw_t"] = 0.84 * r + 0.16 * value_noise(COMP_H, COMP_W, 48, 3)

    L["wipe_t"] = 0.92 * r + 0.08 * value_noise(COMP_H, COMP_W, 110, 7)

    # Bounding boxes so moving groups only touch their own area.
    L["bbox"] = {}
    for name, m in masks.items():
        ys, xs = np.nonzero(m > 0.002)
        L["bbox"][name] = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return L


# ---------------------------------------------------------------- stage frame

ACCENT_F = np.array(ACCENT, np.float32) / 255
LINE_F = np.array(TEXT, np.float32) / 255


def ghost(L, t):
    """Dark technical drawing, drawn on progressively."""
    p = np.clip((t - T_DRAW[0]) / (T_DRAW[1] - T_DRAW[0]), 0, 1)
    prog = (0.30 + 0.70 * (1 - (1 - p) ** 1.5)) * 1.12
    dt = L["draw_t"]
    vis = np.clip((prog - dt) / 0.035, 0, 1)
    head = np.clip(1 - np.abs(prog - dt - 0.015) / 0.03, 0, 1) * (prog < 1.1) * 0.8
    lines = L["lines"] * vis
    hint = smoothstep(0.0, 0.25, prog - dt)[..., None] * 0.085
    img = BG + L["off"] * hint
    col = LINE_F * (1 - head[..., None]) + ACCENT_F * 1.15 * head[..., None]
    img = img * (1 - lines[..., None] * 0.9) + col * lines[..., None] * 0.9
    return img


def group_state(name, t):
    for n, start, dur, off in INSTALL:
        if n == name:
            p = np.clip((t - start) / dur, 0, 1)
            return p, off
    raise KeyError(name)


def paste_group(frame, real, mask, bbox, dx, dy, opacity):
    x0, y0, x1, y1 = bbox
    pad = int(max(abs(dx), abs(dy))) + 2
    X0, Y0 = max(x0 - pad, 0), max(y0 - pad, 0)
    X1, Y1 = min(x1 + pad, COMP_W), min(y1 + pad, COMP_H)
    m = mask[y0:y1, x0:x1] * opacity
    src = np.dstack([real[y0:y1, x0:x1] * m[..., None], m])
    M = np.float32([[1, 0, x0 - X0 + dx], [0, 1, y0 - Y0 + dy]])
    out = cv2.warpAffine(src, M, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    a = out[..., 3:4]
    region = frame[Y0:Y1, X0:X1]
    frame[Y0:Y1, X0:X1] = region * (1 - a) + out[..., :3]


def stage_frame(L, t):
    light = light_level(t)
    real = L["off"] * (1 - light) + L["on"] * light
    if t >= T_LIGHT[1] + 0.05:
        frame = L["on"].copy()
    else:
        frame = ghost(L, t)
        # walls, floor and decor fill in
        q = (t - T_WIPE[0]) / (T_WIPE[1] - T_WIPE[0]) * 1.25
        a = smoothstep(-0.20, 0.0, q - L["wipe_t"]) * L["rest"]
        frame = frame * (1 - a[..., None]) + real * a[..., None]
        for name in GROUPS:
            p, (ox, oy) = group_state(name, t)
            if p <= 0:
                continue
            mask = L["masks"][name]
            if p >= 1:
                frame = frame * (1 - mask[..., None]) + real * mask[..., None]
                continue
            # motion blur: average a few sub-frame positions
            subs = 4
            acc = np.zeros_like(frame)
            for k in range(subs):
                tk = t - (k / subs) * (1 / FPS)
                pk, _ = group_state(name, tk)
                e = ease_out_back(pk)
                op = sstep(0.0, 0.3, pk)
                f = frame.copy()
                if op > 0:
                    paste_group(f, real, mask, L["bbox"][name], ox * ZOOM0 * (1 - e),
                                oy * ZOOM0 * (1 - e), op)
                acc += f
            frame = acc / subs
    # slow pull-back, finishing exactly at full frame
    z = 1 + (ZOOM0 - 1) * (1 - ease_out_cubic(min(t / T_ZOOM_END, 1.0)))
    s = (1 / ZOOM0) * z
    fx, fy = ZOOM_FOCUS[0] * COMP_W, ZOOM_FOCUS[1] * COMP_H
    tx = STAGE_W * ZOOM_FOCUS[0] - fx * s
    ty = STAGE_H * ZOOM_FOCUS[1] - fy * s
    if z > 1:
        tx = min(0.0, max(STAGE_W - COMP_W * s, tx))
        ty = min(0.0, max(STAGE_H - COMP_H * s, ty))
        M = np.float32([[s, 0, tx], [0, s, ty]])
        out = cv2.warpAffine(frame, M, (STAGE_W, STAGE_H), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
    else:
        out = cv2.resize(frame, (STAGE_W, STAGE_H), interpolation=cv2.INTER_AREA)
    return np.clip(out, 0, 1)


def light_level(t):
    a, b = T_LIGHT
    if t < a:
        return 0.0
    if t < a + 0.07:
        return 0.55
    if t < a + 0.14:
        return 0.12
    return 0.12 + 0.88 * sstep(a + 0.14, b, t)


# ---------------------------------------------------------------- text & logo

def svg_logo(height):
    """Rasterise images/fronta-logo.svg (simple M/c/l/z paths) with PIL."""
    svg = LOGO_SVG.read_text()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    paths = re.findall(r'<path d="([^"]+)"', svg)
    scale = height / vb[3] * 4
    polys = []
    for d in paths:
        toks = re.findall(r"[MmCcLlZz]|-?\d+\.?\d*", d)
        i, cmd, cur, start, pts = 0, None, (0.0, 0.0), (0.0, 0.0), []
        while i < len(toks):
            if re.match(r"[MmCcLlZz]", toks[i]):
                cmd = toks[i]; i += 1
                if cmd in "Zz":
                    polys.append(pts); pts = []; cur = start
                    continue
            nums = lambda n: [float(v) for v in toks[i:i + n]]
            if cmd in "Mm":
                x, y = nums(2); i += 2
                cur = (x, y) if cmd == "M" else (cur[0] + x, cur[1] + y)
                start = cur; pts = [cur]
                cmd = "L" if cmd == "M" else "l"
            elif cmd in "Ll":
                x, y = nums(2); i += 2
                cur = (x, y) if cmd == "L" else (cur[0] + x, cur[1] + y)
                pts.append(cur)
            elif cmd in "Cc":
                v = nums(6); i += 6
                if cmd == "c":
                    v = [v[0] + cur[0], v[1] + cur[1], v[2] + cur[0], v[3] + cur[1],
                         v[4] + cur[0], v[5] + cur[1]]
                p0 = cur
                for k in range(1, 13):
                    u = k / 12
                    bx = ((1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * v[0]
                          + 3 * (1 - u) * u ** 2 * v[2] + u ** 3 * v[4])
                    by = ((1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * v[1]
                          + 3 * (1 - u) * u ** 2 * v[3] + u ** 3 * v[5])
                    pts.append((bx, by))
                cur = (v[4], v[5])
    # transform="translate(0,150) scale(0.1,-0.1)" then viewBox offset
    size = (int(vb[2] * scale) + 2, int(vb[3] * scale) + 2)
    img = Image.new("L", size, 0)
    d = ImageDraw.Draw(img)
    for pts in polys:
        d.polygon([((x * 0.1 - vb[0]) * scale, (150 - y * 0.1 - vb[1]) * scale) for x, y in pts],
                  fill=255)
    img = img.resize((size[0] // 4, size[1] // 4), Image.LANCZOS)
    out = Image.new("RGBA", img.size, LOGO + (0,))
    out.putalpha(img)
    return out


def text_image(lines, size):
    """lines: [(text, font_path, colour)] -> RGBA image, left aligned."""
    fonts = [ImageFont.truetype(str(fp), size) for _, fp, _ in lines]
    lh = round(size * 1.14)
    img = Image.new("RGBA", (W, lh * len(lines) + size + TEXT_PAD), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, ((txt, _, col), f) in enumerate(zip(lines, fonts)):
        d.text((0, TEXT_PAD + i * lh), txt, font=f, fill=col + (255,))
    return img, lh


def tracked(text, font, tracking):
    widths = [font.getlength(c) for c in text]
    return widths, sum(widths) + tracking * (len(text) - 1)


def build_overlay():
    """Static pieces of the frame (logo row, footer) and the text blocks."""
    ov = {}
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo = svg_logo(50)
    lx, ly = 72, LOGO_Y - logo.height // 2
    base.alpha_composite(logo, (lx, ly))
    f = ImageFont.truetype(str(SANS), 24)
    tx = lx + logo.width + 20
    widths, _ = tracked("FRONTA DESIGN", f, 24 * 0.2)
    d = ImageDraw.Draw(base)
    x = tx
    for c, cw in zip("FRONTA DESIGN", widths):
        d.text((x, LOGO_Y), c, font=f, fill=LOGO + (255,), anchor="lm")
        x += cw + 24 * 0.2
    fs = ImageFont.truetype(str(SANS), 26)
    d.text((W // 2, STAGE_Y + STAGE_H + 70), "frontadesign.hr", font=fs,
           fill=TEXT + (120,), anchor="mm")
    ov["base"] = base

    # one size for both headline blocks, fitted to the longest line
    build = [("Od skice", SERIF, TEXT), ("do montaže", SERIF, TEXT),
             ("do zadnjeg detalja.", SERIF_IT, ACCENT)]
    final = [("Želiš iskoristiti svaki kutak", SERIF, TEXT),
             ("svog doma na najbolji način?", SERIF, TEXT),
             ("Onda si na pravom mjestu.", SERIF_IT, ACCENT)]
    size = 86
    while True:
        widest = max(ImageFont.truetype(str(fp), size).getlength(tx_) for tx_, fp, _ in build + final)
        if widest <= W - 2 * 72:
            break
        size -= 1
    ov["size"] = size
    ov["build"] = [text_image([ln], size)[0] for ln in build]
    ov["final"] = [text_image([ln], size)[0] for ln in final]
    ov["lh"] = round(size * 1.14)
    return ov


LOGO_Y = 322
HEAD_Y = 420
TEXT_PAD = 40
BUILD_TIMES = [-1.0, 1.35, 5.25]   # first line is on screen from frame 0
FINAL_TIMES = [8.00, 8.15, 8.45]


def place_text(canvas, img, y, alpha, rise):
    if alpha <= 0:
        return
    a = img.copy()
    a.putalpha(a.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(a, (72, int(round(y + rise)) - TEXT_PAD))


def compose(L, ov, t):
    canvas = Image.new("RGBA", (W, H), tuple(int(c * 255) for c in BG) + (255,))
    stage = (stage_frame(L, t) * 255 + 0.5).astype(np.uint8)
    canvas.paste(Image.fromarray(stage), (0, STAGE_Y))
    canvas.alpha_composite(ov["base"])
    lh = ov["lh"]
    out_a = 1 - sstep(7.70, 8.05, t)
    for i, (img, t0) in enumerate(zip(ov["build"], BUILD_TIMES)):
        a = sstep(t0, t0 + 0.4, t) * out_a
        rise = 26 * (1 - ease_out_cubic(np.clip((t - t0) / 0.5, 0, 1))) - 18 * (1 - out_a)
        place_text(canvas, img, HEAD_Y + i * lh, a, rise)
    for i, (img, t0) in enumerate(zip(ov["final"], FINAL_TIMES)):
        a = sstep(t0, t0 + 0.45, t)
        rise = 26 * (1 - ease_out_cubic(np.clip((t - t0) / 0.55, 0, 1)))
        place_text(canvas, img, HEAD_Y + i * lh, a, rise)
    return canvas.convert("RGB")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", type=float)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    L = build_layers()
    ov = build_overlay()

    if args.preview is not None:
        for t in args.preview:
            compose(L, ov, t).save(HERE / f"preview-{t:05.2f}.png")
        return

    n = int(round(DURATION * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
           "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "128k", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        t = i / FPS
        # the last 5 s are fully static once the text has settled
        if t >= FINAL_TIMES[-1] + 0.5 and last is not None:
            proc.stdin.write(last)
            continue
        frame = compose(L, ov, t).tobytes()
        if t >= FINAL_TIMES[-1] + 0.5:
            last = frame
        proc.stdin.write(frame)
        if i % 30 == 0:
            print(f"{t:4.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", args.out)


if __name__ == "__main__":
    main()
