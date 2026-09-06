#!/usr/bin/env python3
"""Animated dot-matrix portrait generator."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--cols", type=int, default=72)
    p.add_argument("--frames", type=int, default=16)
    p.add_argument("--duration", type=int, default=90)
    p.add_argument("--detail", type=float, default=0.62)
    p.add_argument("--color", action="store_true")
    p.add_argument("--bg", default="#0b0f14")
    p.add_argument("--dot", default="#e8eef5")
    p.add_argument("--size", type=int, default=720)
    return p.parse_args()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def prepare_source(path: Path, size: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = max(0, (h - side) // 2 - side // 12)
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.28)
    img = ImageEnhance.Sharpness(img).enhance(1.35)
    img = ImageOps.autocontrast(img, cutoff=2)
    return img


def luminance(px: tuple[int, int, int]) -> float:
    r, g, b = px
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def sample_grid(img: Image.Image, cols: int) -> list[list[tuple[int, int, int]]]:
    small = img.resize((cols, cols), Image.Resampling.LANCZOS)
    small = small.filter(ImageFilter.GaussianBlur(radius=0.35))
    pix = small.load()
    return [[pix[x, y] for x in range(cols)] for y in range(cols)]


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_frame(
    grid: list[list[tuple[int, int, int]]],
    *,
    cols: int,
    canvas: int,
    bg: tuple[int, int, int],
    default_dot: tuple[int, int, int],
    detail: float,
    color: bool,
    t: float,
    frame_i: int,
    nframes: int,
) -> Image.Image:
    img = Image.new("RGB", (canvas, canvas), bg)
    draw = ImageDraw.Draw(img)
    cell = canvas / cols
    max_r = cell * 0.42

    for y in range(cols):
        for x in range(cols):
            rgb = grid[y][x]
            lum = luminance(rgb)
            # Bright skin/highlights = larger dots on a dark canvas
            strength = lum ** (1.05 - detail * 0.45)
            if strength < 0.12:
                continue

            wave = 0.5 + 0.5 * math.sin(
                (x * 0.31 + y * 0.27) + t * math.tau
            )
            pulse = 0.78 + 0.22 * wave
            scan = 0.12 * math.sin((y / cols) * math.pi * 4 + t * math.tau)
            radius = max_r * strength * pulse * (1.0 + scan * 0.15)
            if radius < 0.6:
                continue

            cx = (x + 0.5) * cell
            cy = (y + 0.5) * cell
            # Subtle drift so the portrait feels alive
            cx += math.sin(t * math.tau + y * 0.15) * cell * 0.06
            cy += math.cos(t * math.tau * 0.8 + x * 0.12) * cell * 0.05

            if color:
                # Lift dark source colors so they read on a dark canvas
                # Boost midtones so skin reads on dark background
                boosted = mix(rgb, (255, 255, 255), 0.08 + 0.12 * lum)
                fill = mix(bg, boosted, min(1.0, 0.45 + 0.55 * strength))
            else:
                a = 0.25 + 0.75 * strength
                fill = mix(bg, default_dot, a)

            r = radius
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    # Soft vignette via overlay ring (keeps edges from looking clipped)
    overlay = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(18):
        alpha = int(18 + i * 6)
        inset = i * 3
        od.rectangle(
            (inset, inset, canvas - 1 - inset, canvas - 1 - inset),
            outline=(*bg, alpha),
        )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def main() -> None:
    args = parse_args()
    src = prepare_source(Path(args.input), args.size)
    grid = sample_grid(src, args.cols)
    bg = hex_to_rgb(args.bg)
    dot = hex_to_rgb(args.dot)

    frames: list[Image.Image] = []
    for i in range(args.frames):
        t = i / args.frames
        frames.append(
            make_frame(
                grid,
                cols=args.cols,
                canvas=args.size,
                bg=bg,
                default_dot=dot,
                detail=args.detail,
                color=args.color,
                t=t,
                frame_i=i,
                nframes=args.frames,
            )
        )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=args.duration,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {out} ({args.frames} frames, {args.cols} cols)")


if __name__ == "__main__":
    main()
