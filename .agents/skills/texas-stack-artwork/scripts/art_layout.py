"""Measured typography and illustration space shared by planning and composition."""
from __future__ import annotations

import itertools
from PIL import Image, ImageDraw, ImageFont

SIZE = 1080


def headline_layout(text: str, font_path: str) -> dict:
    words = ' '.join(text.upper().split()).split()
    if not 4 <= len(words) <= 9:
        raise ValueError('headline must contain four to nine words')
    draw = ImageDraw.Draw(Image.new('RGB', (SIZE, SIZE)))
    candidates = []
    for count in (2, 3):
        for cuts in itertools.combinations(range(1, len(words)), count - 1):
            stops = (0, *cuts, len(words))
            lines = [' '.join(words[a:b]) for a, b in zip(stops, stops[1:])]
            for size in range(108, 71, -2):
                font = ImageFont.truetype(font_path, size)
                boxes = [draw.textbbox((0, 0), line, font=font, anchor='lt') for line in lines]
                widths = [b[2] - b[0] for b in boxes]
                heights = [b[3] - b[1] for b in boxes]
                height = sum(heights) + 16 * (count - 1)
                if max(widths) > 952 or height > 252:
                    continue
                # Prefer two lines, useful size and balanced lines; penalize a lonely last word.
                cost = (108-size)*1.4 + (count-2)*32 + (max(widths)-min(widths))/20
                cost += 24 if len(lines[-1].split()) == 1 else 0
                candidates.append((cost, lines, size, heights))
                break
    if not candidates:
        raise ValueError('headline cannot fit legibly; shorten it')
    _, lines, size, heights = min(candidates, key=lambda c: c[0])
    top = 938 - sum(heights) - 16*(len(lines)-1)
    y = top
    positions = []
    font = ImageFont.truetype(font_path, size)
    boxes = []
    for line, height in zip(lines, heights):
        bearing = draw.textbbox((0, 0), line, font=font, anchor='lt')[0]
        position = [64-bearing, y]
        positions.append(position)
        boxes.append(list(draw.textbbox(tuple(position), line, font=font, anchor='lt')))
        y += height + 16
    return dict(schema_version=1,headline=' '.join(words),font_size=size,lines=lines,
                positions=positions,text_boxes=boxes,headline_top=top,
                subject_zone=[64,196,1016,top-40],canvas=[SIZE,SIZE])


def validate_subject_box(box: list[int], layout: dict) -> None:
    if len(box) != 4 or any(isinstance(v, bool) or not isinstance(v, int) for v in box):
        raise ValueError('subject box must be four integer canvas coordinates')
    l,t,r,b = box
    if not (0 <= l < r <= SIZE and 0 <= t < b <= SIZE):
        raise ValueError('subject box must be inside the 1080 square canvas')
    zone = layout['subject_zone']
    if l < zone[0] or t < zone[1] or r > zone[2] or b > zone[3]:
        raise ValueError('subject overlaps publication furniture or its clearance; repair framing')
