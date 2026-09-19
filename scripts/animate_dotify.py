#!/usr/bin/env python3
"""Readable animated dot portrait. Dependency: Pillow >= 10.

The dots keep nearly constant area so shadow details are not attenuated twice.
A low-opacity source underlay restores detail at small README display sizes.
The only motion is a periodic lighting sweep; facial geometry never shifts.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageOps


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--cols', type=int, default=110)
    p.add_argument('--frames', type=int, default=48)
    p.add_argument('--duration', type=int, default=90, help='Milliseconds per frame')
    p.add_argument('--detail', type=float, default=0.88, help='Detail retention, 0 to 1')
    p.add_argument('--color', action='store_true')
    p.add_argument('--bg', default='#0b0f14')
    p.add_argument('--dot', default='#e8eef5')
    p.add_argument('--size', type=int, default=660)
    p.add_argument('--underlay', type=float, default=0.22, help='Subtle source underlay, 0 to 1; use 0 for pure dots')
    p.add_argument('--supersample', type=int, default=2, choices=[1, 2, 3])
    args = p.parse_args()
    if not 24 <= args.cols <= 200: p.error('--cols must be 24..200')
    if not 2 <= args.frames <= 120: p.error('--frames must be 2..120')
    if not 128 <= args.size <= 1200: p.error('--size must be 128..1200')
    if not 20 <= args.duration <= 1000: p.error('--duration must be 20..1000')
    if not 0 <= args.detail <= 1 or not 0 <= args.underlay <= 1:
        p.error('--detail and --underlay must be between 0 and 1')
    return args


def prepare_source(path, size, detail):
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert('RGB')
    image = ImageOps.fit(image, (size, size), method=Image.Resampling.LANCZOS)
    # Lift midtones gently without the old contrast/autocontrast highlight clipping.
    gamma = 0.91 - 0.08 * detail
    lut = [round(255 * (i / 255) ** gamma) for i in range(256)]
    image = image.point(lut * 3)
    image = ImageEnhance.Color(image).enhance(0.95)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=95, threshold=3))


def prepare_grid(source, cols, bg, dot, color):
    small = source.resize((cols, cols), Image.Resampling.LANCZOS)
    entries = []
    for y in range(cols):
        for x in range(cols):
            rgb = small.getpixel((x, y))
            lum = (0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]) / 255
            if not color:
                rgb = tuple(round(bg[k] + (dot[k] - bg[k]) * lum) for k in range(3))
            entries.append((x, y, rgb, lum))
    return entries


def make_frame(source, entries, args, bg, phase):
    scale = args.supersample
    size = args.size * scale
    photo = source.resize((size, size), Image.Resampling.LANCZOS)
    if not args.color:
        photo = ImageOps.colorize(ImageOps.grayscale(photo), bg, ImageColor.getrgb(args.dot))
    frame = Image.blend(Image.new('RGB', (size, size), bg), photo, args.underlay)
    draw = ImageDraw.Draw(frame)
    cell = size / args.cols
    for x, y, rgb, lum in entries:
        # Constant centre and high minimum radius preserve eyes, glasses and hair.
        radius = cell * (0.43 + 0.035 * args.detail + 0.008 * lum)
        distance = abs((y / args.cols - phase + 0.5) % 1.0 - 0.5)
        wave = 0.5 + 0.5 * math.cos(math.pi * distance / 0.14) if distance < 0.14 else 0.0
        amount = 0.20 * wave * (0.25 + 0.75 * math.sqrt(lum))
        # A restrained lavender light passes over the portrait without darkening it.
        light = (225, 214, 255)
        fill = tuple(round(min(255, c + max(0, light[k] - c) * amount)) for k, c in enumerate(rgb))
        cx, cy = (x + 0.5) * cell, (y + 0.5) * cell
        draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=fill)
    return frame.resize((args.size, args.size), Image.Resampling.LANCZOS)


def save_gif(frames, out, duration):
    # One palette for the entire loop prevents per-frame colour flicker.
    count = min(8, len(frames))
    sample = Image.new('RGB', (256 * count, 256))
    for j in range(count):
        index = j * len(frames) // count
        sample.paste(frames[index].resize((256, 256)), (256*j, 0))
    palette = sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    quantized = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    out.parent.mkdir(parents=True, exist_ok=True)
    temporary = out.with_name(out.name + '.tmp')
    quantized[0].save(temporary, format='GIF', save_all=True, append_images=quantized[1:],
                      duration=duration, loop=0, disposal=1, optimize=False)
    temporary.replace(out)


def main():
    args = parse_args()
    source = prepare_source(Path(args.input), args.size, args.detail)
    bg, dot = ImageColor.getrgb(args.bg), ImageColor.getrgb(args.dot)
    entries = prepare_grid(source, args.cols, bg, dot, args.color)
    frames = [make_frame(source, entries, args, bg, i / args.frames) for i in range(args.frames)]
    output = Path(args.output)
    save_gif(frames, output, args.duration)
    print(f'Wrote {output}: {len(frames)} frames, {args.cols} columns, {output.stat().st_size / 1024 / 1024:.2f} MiB')


if __name__ == '__main__':
    main()
