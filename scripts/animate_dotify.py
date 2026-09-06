from PIL import Image, ImageDraw, ImageEnhance, ImageOps
import argparse
import math
import os


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def center_crop(img, target_ratio):
    w, h = img.size
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img


def prepare_image(img, cols, equalize=True, contrast=1.8, brightness=1.15):
    # Convert to grayscale
    img = ImageOps.grayscale(img)

    # Enhance contrast
    img = ImageEnhance.Contrast(img).enhance(contrast)

    # Slightly increase brightness
    img = ImageEnhance.Brightness(img).enhance(brightness)

    # Histogram equalization
    if equalize:
        img = ImageOps.equalize(img)

    # Resize according to dot columns
    w, h = img.size
    aspect = h / w

    rows = max(1, int(cols * aspect * 0.55))

    img = img.resize((cols, rows), Image.Resampling.LANCZOS)

    return img


def create_dot_frame(
    gray,
    frame_progress,
    scale,
    dot_color,
    background,
    min_radius=0.18,
    max_radius=0.52
):
    cols, rows = gray.size

    width = cols * scale
    height = rows * scale

    canvas = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(canvas)

    for y in range(rows):
        for x in range(cols):

            brightness = gray.getpixel((x, y)) / 255.0

            # Make the portrait stronger.
            # Dark areas remain dark, brighter facial areas
            # become brighter dots.
            brightness = max(0.0, min(1.0, brightness))

            # Gamma makes facial details more visible.
            brightness = brightness ** 0.72

            # Dot visibility
            visibility = smoothstep(frame_progress)

            # Keep enough dots visible even during animation.
            effective = brightness * visibility

            if effective < 0.035:
                continue

            cx = int((x + 0.5) * scale)
            cy = int((y + 0.5) * scale)

            radius = scale * (
                min_radius +
                (max_radius - min_radius) * effective
            )

            # Increase dot brightness based on image brightness.
            dot_strength = int(35 + 220 * effective)

            if dot_color == "color":
                # Cool white / blue-white appearance
                r = dot_strength
                g = min(255, int(dot_strength * 0.96))
                b = min(255, int(dot_strength * 1.08))
                color = (r, g, b)
            else:
                color = (
                    dot_strength,
                    dot_strength,
                    dot_strength
                )

            draw.ellipse(
                (
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius
                ),
                fill=color
            )

    return canvas


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("input")
    parser.add_argument(
        "-o",
        "--output",
        default="assets/portrait-animation.gif"
    )

    parser.add_argument("--cols", type=int, default=100)
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--duration", type=int, default=100)
    parser.add_argument("--scale", type=int, default=7)

    parser.add_argument(
        "--detail",
        type=float,
        default=0.65
    )

    parser.add_argument(
        "--equalize",
        action="store_true"
    )

    parser.add_argument(
        "--color",
        action="store_true"
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # Load image
    # --------------------------------------------------

    img = Image.open(args.input).convert("RGB")

    # --------------------------------------------------
    # Crop to portrait
    # --------------------------------------------------

    img = center_crop(img, 1.0)

    # --------------------------------------------------
    # Improve contrast
    # --------------------------------------------------

    gray = prepare_image(
        img,
        args.cols,
        equalize=args.equalize,
        contrast=1.9,
        brightness=1.18
    )

    # --------------------------------------------------
    # Background and dot color
    # --------------------------------------------------

    background = (3, 4, 7)

    dot_color = "color" if args.color else "white"

    # --------------------------------------------------
    # Generate animation
    # --------------------------------------------------

    frames = []

    # Start with a small number of visible dots
    # and gradually reveal the full portrait.
    for i in range(args.frames):

        progress = i / max(1, args.frames - 1)

        # Slightly accelerate the reveal
        progress = smoothstep(progress)

        frame = create_dot_frame(
            gray,
            progress,
            args.scale,
            dot_color,
            background
        )

        frames.append(frame)

    # --------------------------------------------------
    # Hold final portrait
    # --------------------------------------------------

    for _ in range(8):
        frames.append(frames[-1].copy())

    # --------------------------------------------------
    # Save GIF
    # --------------------------------------------------

    os.makedirs(
        os.path.dirname(args.output) or ".",
        exist_ok=True
    )

    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=args.duration,
        loop=0,
        optimize=False
    )

    print(
        f"Saved animated portrait to {args.output}"
    )


if __name__ == "__main__":
    main()
