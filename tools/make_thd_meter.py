#!/usr/bin/env python3
"""Derive the Eisenkern THD meter face from the transferred GS76 asset."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'lv2/eisenkern.lv2/modgui/assets'
SOURCE = ASSETS / 'thd-meter-base.png'
OUTPUT = ASSETS / 'thd-meter-face.png'


def font(size, bold=False):
    suffix = 'Bold.ttf' if bold else '.ttf'
    candidates = (
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-' + suffix,
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def centered(draw, y, text, face, fill=(28, 26, 22, 255)):
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((260 - (box[2] - box[0])) / 2, y), text, font=face, fill=fill)


def main():
    image = Image.open(SOURCE).convert('RGBA')
    draw = ImageDraw.Draw(image)
    # The GS76 source face is retained as thd-meter-base.png. Repaint only the
    # centre legend. Interpolate each affected row from clean pixels on both
    # sides so the original vertical/radial backlight remains continuous.
    pixels = image.load()
    for y in range(93, 130):
        left, right = pixels[65, y], pixels[195, y]
        for x in range(70, 191):
            t = (x - 65) / 130.0
            pixels[x, y] = tuple(round(a + (b - a) * t)
                                 for a, b in zip(left, right))
    centered(draw, 98, 'THD', font(11, bold=True))
    centered(draw, 114, '%', font(9))
    image.save(OUTPUT)
    print('geschrieben:', OUTPUT)


if __name__ == '__main__':
    main()
