#!/usr/bin/env python3
"""Eigener Chicken-Head-Filmstreifen: 65 Frames, feste Rastwinkel.

MOD bildet 0..3 auf Frames 0/21/43/64 ab. Diese Frames zeigen exakt
auf −135/−45/+45/+135 Grad. Der Sockel und die Beleuchtung bleiben
ortsfest; nur die plastische Griffgeometrie dreht um die Achse.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'lv2/eisenkern.lv2/modgui/assets/eisen-knob.png'
FRAME, SS, FRAMES = 128, 4, 65
SIZE = FRAME * SS
CENTER = SIZE / 2


def bezier(points, count=24):
    result = []
    for i in range(count):
        t = i / (count - 1)
        weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
        result.append(tuple(sum(w*p[j] for w, p in zip(weights, points))
                            for j in (0, 1)))
    return result


def angle(frame):
    stops = ((0, -135), (21, -45), (43, 45), (64, 135))
    for (a, x), (b, y) in zip(stops, stops[1:]):
        if frame <= b:
            return x + (y-x) * (frame-a) / (b-a)
    return 135


def rotate(points, degrees):
    s, c = math.sin(math.radians(degrees)), math.cos(math.radians(degrees))
    return [(CENTER + (x-CENTER)*c - (y-CENTER)*s,
             CENTER + (x-CENTER)*s + (y-CENTER)*c) for x, y in points]


def render(degrees):
    image = Image.new('RGBA', (SIZE, SIZE))
    draw = ImageDraw.Draw(image)
    # Opaque skirt: there must be no transparent crescent on the dark side.
    draw.ellipse((102, 102, 410, 410), fill=(9, 10, 12), outline=(3, 4, 5), width=5)
    draw.ellipse((112, 108, 400, 394), fill=(25, 26, 29))
    draw.arc((116, 112, 396, 394), 190, 315, fill=(91, 94, 100), width=5)
    draw.arc((109, 109, 403, 403), 10, 145, fill=(4, 5, 7), width=8)
    # A single continuous grip with pointed head and rounded short tail.
    right = bezier(((256, 30), (280, 38), (290, 106), (310, 181)))
    right += bezier(((310, 181), (324, 257), (324, 354), (304, 410)))
    tail = bezier(((304, 410), (292, 436), (220, 436), (208, 410)))
    left = [(512-x, y) for x, y in reversed(right)]
    outline = right + tail + left
    rotated = rotate(outline, degrees)
    # Sidewall displaced down-right, then top face: a shallow molded grip.
    draw.polygon([(x+5, y+10) for x, y in rotated], fill=(5, 6, 8))
    mask = Image.new('L', image.size)
    ImageDraw.Draw(mask).polygon(rotated, fill=255)
    face = Image.new('RGBA', image.size)
    pixels = face.load()
    m = mask.load()
    for y in range(SIZE):
        for x in range(SIZE):
            if m[x, y]:
                light = max(0, 1 - math.hypot((x-178)/360, (y-145)/420))
                tone = round(25 + 36*light)
                pixels[x, y] = (tone, tone+1, tone+5, 255)
    image.alpha_composite(face)
    draw = ImageDraw.Draw(image)
    draw.line(rotated + rotated[:1], fill=(12, 13, 16), width=3, joint='curve')
    # Mold seam and narrow ridge highlights, following the complete grip.
    ridge = rotate([(256, 42), (256, 412)], degrees)
    draw.line(ridge, fill=(8, 9, 12), width=7)
    draw.line(rotate([(252, 44), (252, 406)], degrees), fill=(102, 104, 111), width=3)
    draw.line(rotate(right[:20], degrees), fill=(155, 159, 167), width=4, joint='curve')
    # Small fixed upper-left reflection; light does not turn with the knob.
    shine = Image.new('RGBA', image.size)
    ImageDraw.Draw(shine).ellipse((164, 150, 188, 224), fill=(220, 223, 230, 48))
    shine = shine.filter(ImageFilter.GaussianBlur(5))
    image.alpha_composite(Image.composite(shine, Image.new('RGBA', image.size), mask))
    return image.resize((FRAME, FRAME), Image.Resampling.LANCZOS)


def main():
    strip = Image.new('RGBA', (FRAMES * FRAME, FRAME))
    for frame in range(FRAMES):
        strip.paste(render(angle(frame)), (frame * FRAME, 0))
    strip.save(OUTPUT)
    print('geschrieben:', OUTPUT, strip.size)


if __name__ == '__main__':
    main()
