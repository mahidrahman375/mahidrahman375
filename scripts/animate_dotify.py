#!/usr/bin/env python3
"""
Create an animated dot-matrix portrait GIF.

The animation starts with a dark/empty canvas and progressively reveals
the portrait's dots from coarse to fine detail.

Usage:
    python scripts/animate_dotify.py \
        assets/profile.png \
        -o assets/portrait-animation.gif
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("-o", "--output", default="assets/portrait-animation.gif")
    p.add_argument("--cols", type=int, default=90)
    p.add_argument("--frames", type=int, default=18)
    p.add_argument("--duration", type=int, default=85,
                   help="milliseconds per frame")
    p.add_argument("--scale", type=int, default=7,
                   help="pixels per dot-cell")
    p.add_argument("--equalize", action="store_true")
    p.add_argument("--detail", type=float, default=0.55)
    p.add_argument("--color", action="store_true")
    p.add_argument("--bg", default=(7, 8, 12))
    return p.parse_args()


def prepare_image(path: str, cols: int, equalize: bool, detail: float):
    img = Image.open(path).convert("RGB")

    # Center crop to keep the face/head-and-shoulders composition.
    w, h = img.size
    target_ratio = 0.86  # width / height
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, (h - new_h) // 2)
        img = img.crop((0, top, w, min(h, top + new_h)))

    gray = ImageOps.grayscale(img)
    if equalize:
        gray = ImageOps.equalize(gray)

    detail = max(0.0, min(1.0, detail))
    blur_radius = max(0.25, 2.4 - 2.0 * detail)
    gray = gray.filter(ImageFilter.GaussianBlur(blur_radius))
    gray = ImageEnhance.Contrast(gray).enhance(1.0 + 1.25 * detail)

    aspect = gray.height / gray.width
    rows = max(1, int(cols * aspect * 0.52))

    rgb_small = img.resize((cols, rows), Image.Resampling.LANCZOS)
    gray_small = gray.resize((cols, rows), Image.Resampling.LANCZOS)

    return rgb_small, gray_small


def make_frame(rgb_small, gray_small, cols, scale, progress, use_color, bg):
    rows = gray_small.height
    w, h = cols * scale, rows * scale
    canvas = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(canvas)

    # Reveal pixels by darkness threshold. As progress grows, more dots appear.
    for y in range(rows):
        for x in range(cols):
            brightness = gray_small.getpixel((x, y)) / 255.0
            darkness = 1.0 - brightness

            # Skip very dark background.
            if darkness < 0.055:
                continue

            # Reveal gradually, with a soft threshold.
            threshold = 0.92 * progress
            if darkness < threshold:
                continue

            strength = max(0.0, min(1.0, (darkness - 0.04) / 0.96))

            # Dots grow slightly as they are revealed.
            base_r = 0.6 + 2.45 * strength
            r = base_r * (0.65 + 0.35 * progress)

            cx = x * scale + scale / 2
            cy = y * scale + scale / 2

            if use_color:
                fill = rgb_small.getpixel((x, y))
            else:
                # Cool-white monochrome.
                v = int(170 + 80 * strength)
                fill = (v, v, min(255, v + 10))

            box = (cx - r, cy - r, cx + r, cy + r)
            draw.ellipse(box, fill=fill)

    return canvas


def main():
    args = parse_args()

    if args.cols < 30:
        raise SystemExit("--cols should be at least 30.")
    if args.frames < 4:
        raise SystemExit("--frames should be at least 4.")

    rgb_small, gray_small = prepare_image(
        args.input,
        args.cols,
        args.equalize,
        args.detail,
    )

    frames = []
    # Ease-in / ease-out makes the reveal feel smoother.
    for i in range(args.frames):
        t = i / (args.frames - 1)
        progress = t * t * (3 - 2 * t)
        frames.append(
            make_frame(
                rgb_small,
                gray_small,
                args.cols,
                args.scale,
                progress,
                args.color,
                tuple(args.bg),
            )
        )

    # Hold the finished portrait for a moment, then let it restart.
    frames.extend([frames[-1]] * 5)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=args.duration,
        loop=0,
        optimize=True,
    )

    print(f"Saved animated portrait: {output}")


if __name__ == "__main__":
    main()
