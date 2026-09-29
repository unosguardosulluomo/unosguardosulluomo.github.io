"""Apply the standard Uno Sguardo sull'Uomo watermark to an editorial image."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


TEXT = "UNO SGUARDO SULL'UOMO"


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--quality", type=int, default=90)
    return parser.parse_args()


def font_for(width):
    size = max(22, round(width / 45))
    candidates = (
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def add_watermark(image):
    canvas = image.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = font_for(canvas.width)
    left, top, right, bottom = draw.textbbox((0, 0), TEXT, font=font)
    text_width, text_height = right - left, bottom - top
    padding_x = max(14, round(canvas.width * 0.012))
    padding_y = max(9, round(canvas.height * 0.010))
    margin = max(16, round(min(canvas.size) * 0.018))
    x = canvas.width - margin - text_width - 2 * padding_x
    y = canvas.height - margin - text_height - 2 * padding_y
    draw.rounded_rectangle(
        (x, y, canvas.width - margin, canvas.height - margin),
        radius=max(8, padding_y),
        fill=(0, 0, 0, 112),
    )
    draw.text((x + padding_x, y + padding_y - top), TEXT, font=font, fill=(255, 255, 255, 220))
    return Image.alpha_composite(canvas, overlay).convert("RGB")


def main():
    args = arguments()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    watermarked = add_watermark(Image.open(args.input))
    suffix = output.suffix.lower()
    if suffix == ".webp":
        watermarked.save(output, "WEBP", quality=args.quality, method=6)
    elif suffix in (".jpg", ".jpeg"):
        watermarked.save(output, "JPEG", quality=args.quality, optimize=True)
    else:
        watermarked.save(output, "PNG", optimize=True)
    print(f"{output} {watermarked.width}x{watermarked.height}")


if __name__ == "__main__":
    main()
