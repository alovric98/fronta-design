#!/usr/bin/env python3
"""Export the image layers used by the HyperFrames composition.

Cuts kuhinja-izvor.jpg into the pieces the video animates: the line drawing,
every kitchen unit (elements.py), the room/details layer, and the photo with
the LED light off and on. Run once after changing the photo or elements.py:

    python3 layers.py        # writes hyperframes/assets/layers/*

Needs: numpy, pillow, opencv-python-headless.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from elements import DECOR, GLOW, GROUPS

HERE = Path(__file__).resolve().parent
SRC = HERE / "kuhinja-izvor.jpg"
OUT = HERE / "hyperframes" / "assets" / "layers"

# Part of the photo shown on the stage (photo pixels) and the export size:
# 1.2x the 1080 px stage so the slow pull-back stays sharp.
CROP = (140, 50, 1960, 1530)
EXPORT_W = 1296
EXPORT_H = round(EXPORT_W * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0]))

TEXT = np.array([0xED, 0xEB, 0xE8], np.float32) / 255
ACCENT = np.array([0xC5, 0x86, 0x56], np.float32) / 255


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, np.float32) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def to_stage(img):
    x0, y0, x1, y1 = CROP
    return cv2.resize(img[y0:y1, x0:x1], (EXPORT_W, EXPORT_H), interpolation=cv2.INTER_AREA)


def poly_mask(shape, polys, blur=0.0):
    m = np.zeros(shape, np.uint8)
    for p in polys:
        cv2.fillPoly(m, [np.array(p, np.int32)], 255)
    m = m.astype(np.float32) / 255
    return cv2.GaussianBlur(m, (0, 0), blur) if blur else m


def label_map(P8, P):
    """0 = room/details, i+1 = GROUPS[i] (later groups win overlaps)."""
    h, w = P.shape[:2]
    names = list(GROUPS)
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    for i, (name, g) in enumerate(GROUPS.items()):
        if not name.startswith("stool"):
            for poly in g["poly"]:
                d.polygon(poly, fill=i + 1)
    lab = np.array(img)

    # Stools: GrabCut tightens the shell polygons, legs are thick lines.
    for name in ("stool_back", "stool_left", "stool_right"):
        idx = names.index(name) + 1
        g = GROUPS[name]
        poly = poly_mask((h, w), g["poly"]).astype(np.uint8)
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
        fg &= cv2.dilate(pc, np.ones((9, 9), np.uint8))
        lab[y0:y1, x0:x1][fg > 0] = idx
        legs = Image.fromarray(lab)
        d = ImageDraw.Draw(legs)
        for pts, width in g.get("lines", []):
            d.line(pts, fill=idx, width=width, joint="curve")
        lab = np.array(legs)

    # Decor standing on a unit stays part of the room layer, so it appears
    # with the details instead of riding in with the counter or shelves.
    decor = poly_mask((h, w), list(DECOR.values())) > 0
    for name in ("counter", "peninsula", "tall", "shelves"):
        idx = names.index(name) + 1
        own = lab == idx
        region = own & decor
        if not region.any():
            continue
        clean = (own & ~decor).astype(np.float32)
        est = (cv2.GaussianBlur(P * clean[..., None], (0, 0), 12)
               / (cv2.GaussianBlur(clean, (0, 0), 12)[..., None] + 1e-4))
        foot = (region & (np.linalg.norm(P - est, axis=2) > 0.11)).astype(np.uint8)
        foot = cv2.morphologyEx(foot, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        foot = cv2.dilate(foot, np.ones((5, 5), np.uint8)) > 0
        lab[foot & own] = 0
    return lab


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
    return np.clip(out * 0.93, 0, 1)   # the room is a touch darker before the lights


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
    _, lab, stats, _ = cv2.connectedComponentsWithStats((L > 0.25).astype(np.uint8), 8)
    keep = stats[:, cv2.CC_STAT_AREA] >= 60
    keep[0] = False
    return L * keep[lab]


def save_rgba(path, rgb, alpha):
    a = np.clip(alpha, 0, 1)
    # colour under fully transparent pixels is never seen; zero it to keep files small
    img = np.dstack([np.clip(rgb, 0, 1) * (a > 0)[..., None], a])
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), "RGBA").save(path, optimize=True)


def main():
    P8 = np.array(Image.open(SRC).convert("RGB"))
    P = P8.astype(np.float32) / 255
    OUT.mkdir(parents=True, exist_ok=True)

    on = to_stage(P)
    off = to_stage(lights_off(P))
    Image.fromarray((on * 255 + 0.5).astype(np.uint8)).save(OUT / "on.jpg", quality=93)
    Image.fromarray((off * 255 + 0.5).astype(np.uint8)).save(OUT / "off.jpg", quality=93)

    lines = np.clip(to_stage(line_art(P8)) * 1.35, 0, 1)
    save_rgba(OUT / "lines.png", TEXT, lines * 0.9)
    save_rgba(OUT / "lines-accent.png", np.minimum(ACCENT * 1.15, 1), lines)

    lab = label_map(P8, P)
    covered = np.zeros((EXPORT_H, EXPORT_W), np.float32)
    for i, name in enumerate(GROUPS):
        m = to_stage((lab == i + 1).astype(np.float32))
        covered += m
        # grow 1 px so neighbouring units overlap instead of leaving a seam
        save_rgba(OUT / f"{name}.png", off, cv2.dilate(m, np.ones((3, 3), np.float32)))
    room = np.clip(1 - covered, 0, 1)
    save_rgba(OUT / "room.png", off, cv2.dilate(room, np.ones((3, 3), np.float32)))
    print(f"wrote {OUT} ({EXPORT_W}x{EXPORT_H})")


if __name__ == "__main__":
    main()
