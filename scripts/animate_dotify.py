from PIL import Image, ImageDraw, ImageEnhance, ImageOps, ImageFilter
import argparse
import numpy as np
import os


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def center_crop(img, ratio=1.0):
    w, h = img.size
    current = w / h

    if current > ratio:
        new_w = int(h * ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def prepare_image(img, cols):
    # Grayscale
    gray = ImageOps.grayscale(img)

    # Do NOT use histogram equalization.
    # It was responsible for blowing out the face.
    gray = ImageEnhance.Contrast(gray).enhance(1.35)

    # Very mild smoothing keeps the dot pattern clean.
    gray = gray.filter(ImageFilter.GaussianBlur(0.35))

    w, h = gray.size

    # Compensate for GitHub/HTML pixel aspect ratio.
    rows = max(1, int(cols * (h / w) * 0.55))

    return gray.resize(
        (cols, rows),
        Image.Resampling.LANCZOS
    )


def make_frame(
    gray,
    progress,
    scale,
    background=(3, 5, 8)
):
    cols, rows = gray.size

    canvas = Image.new(
        "RGB",
        (cols * scale, rows * scale),
        background
    )

    draw = ImageDraw.Draw(canvas)

    arr = np.asarray(gray, dtype=np.float32) / 255.0

    # Slight gamma adjustment.
    # Keeps facial midtones visible without blowing out highlights.
    arr = np.power(arr, 0.90)

    reveal = smoothstep(progress)

    for y in range(rows):
        for x in range(cols):

            value = float(arr[y, x])

            # Remove only the very darkest background.
            value = np.clip(
                (value - 0.055) / 0.945,
                0.0,
                1.0
            )

            # Animation reveal.
            visible = value * reveal

            if visible < 0.06:
                continue

            cx = (x + 0.5) * scale
            cy = (y + 0.5) * scale

            # Smaller dots = much cleaner face.
            radius = scale * (
                0.10 +
                0.36 * (visible ** 0.95)
            )

            # Soft cool-white dot appearance.
            strength = int(
                95 + 155 * min(1.0, visible)
            )

            color = (
                strength,
                min(255, strength + 3),
                min(255, strength + 12)
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

    parser = argparse.ArgumentParser(
        description="Generate an animated dot-matrix portrait."
    )

    parser.add_argument("input")
    parser.add_argument(
        "-o",
        "--output",
        default="assets/portrait-animation.gif"
    )

    parser.add_argument(
        "--cols",
        type=int,
        default=120
    )

    parser.add_argument(
        "--frames",
        type=int,
        default=24
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=90
    )

    parser.add_argument(
        "--scale",
        type=int,
        default=5
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    image = Image.open(args.input).convert("RGB")

    # --------------------------------------------------
    # Crop
    # --------------------------------------------------

    image = center_crop(image, 1.0)

    # --------------------------------------------------
    # Prepare
    # --------------------------------------------------

    gray = prepare_image(
        image,
        args.cols
    )

    # --------------------------------------------------
    # Animation
    # --------------------------------------------------

    frames = []

    for i in range(args.frames):

        progress = i / max(
            1,
            args.frames - 1
        )

        frame = make_frame(
            gray,
            progress,
            args.scale
        )

        frames.append(frame)

    # Hold final portrait
    for _ in range(10):
        frames.append(frames[-1].copy())

    # --------------------------------------------------
    # Save
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
        f"Saved: {args.output}"
    )


if __name__ == "__main__":
    main()
