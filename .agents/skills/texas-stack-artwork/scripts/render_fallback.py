#!/usr/bin/env python3
"""Render the disclosed emergency fallback for The Texas Stack."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from compose_cover import compose

SIZE = 1080


def rgb(value: str) -> tuple[int, int, int]:
    clean = value.lstrip("#")
    return tuple(int(clean[index:index + 2], 16) for index in (0, 2, 4))


def background(seed: int = 1845) -> Image.Image:
    rng = np.random.default_rng(seed)
    top = np.array(rgb("#08060F"), dtype=float)
    bottom = np.array(rgb("#2B2447"), dtype=float)
    array = np.zeros((SIZE, SIZE, 3), dtype=float)
    for y in range(SIZE):
        amount = (y / (SIZE - 1)) ** 1.15
        array[y, :, :] = top * (1 - amount) + bottom * amount

    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    glow = np.exp(-(((xx - 545) / 320) ** 2 + ((yy - 500) / 250) ** 2))
    gold = np.array(rgb("#E0956A"), dtype=float)
    array = array * (1 - glow[..., None] * 0.22) + gold * glow[..., None] * 0.22
    array = np.clip(array + rng.normal(0, 4.2, (SIZE, SIZE, 1)), 0, 255).astype(np.uint8)
    image = Image.fromarray(array, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")

    # A five-layer apparatus with one disconnected coupling. It is intentionally generic and
    # exists only so a connector failure never produces an image-less email.
    centers = [(220, 470), (380, 390), (545, 500), (710, 410), (860, 515)]
    colors = ["#4E5FA8", "#6E7A5A", "#E4D8C3", "#8C5A3C", "#C9B393"]
    for index, ((cx, cy), color) in enumerate(zip(centers, colors)):
        radius = 92 if index == 2 else 70
        for ring in range(5, 0, -1):
            current = radius * ring / 5
            fill = (*rgb(color), 28 + ring * 20)
            draw.ellipse(
                (cx - current, cy - current, cx + current, cy + current),
                fill=fill,
                outline=(*rgb("#EDE6D6"), 80),
                width=2,
            )
        for spoke in range(8):
            angle = spoke * math.tau / 8
            draw.line(
                (
                    cx,
                    cy,
                    cx + math.cos(angle) * radius,
                    cy + math.sin(angle) * radius,
                ),
                fill=(*rgb("#EDE6D6"), 75),
                width=2,
            )
    for left, right in zip(centers, centers[1:]):
        x1, y1 = left
        x2, y2 = right
        if left == centers[2]:
            draw.line((x1 + 90, y1, x2 - 105, y2), fill=(*rgb("#E0956A"), 65), width=7)
            draw.ellipse((x2 - 112, y2 - 14, x2 - 84, y2 + 14), outline=rgb("#E0956A"), width=4)
        else:
            draw.line((x1 + 68, y1, x2 - 68, y2), fill=(*rgb("#C9B393"), 140), width=5)
    for x in range(80, SIZE, 48):
        draw.line((x, 230, x + 120, 720), fill=(*rgb("#EDE6D6"), 15), width=1)
    return image.filter(ImageFilter.GaussianBlur(0.35))


def fallback_eval(reason: str) -> dict:
    scores = {
        "concept": 6.8,
        "focal_hierarchy": 7.5,
        "composition": 7.4,
        "color_value": 7.6,
        "detail_richness": 7.0,
        "craft_finish": 7.3,
        "typography": 8.4,
        "originality": 6.5,
        "story_fidelity": 6.4,
    }
    weights = {
        "concept": 0.18,
        "focal_hierarchy": 0.13,
        "composition": 0.13,
        "color_value": 0.13,
        "detail_richness": 0.12,
        "craft_finish": 0.10,
        "typography": 0.09,
        "originality": 0.08,
        "story_fidelity": 0.04,
    }
    weighted = round(sum(scores[key] * weights[key] for key in weights), 3)
    final = {"weighted": weighted, "scores": scores, "passed": False}
    return {
        "schema_version": 1,
        "source": "fallback",
        "concepts": [
            {
                "name": "layered apparatus",
                "metaphor": "five connected components with one open coupling",
            },
            {
                "name": "quiet switchyard",
                "metaphor": "a system held in a neutral waiting state",
            },
            {
                "name": "stacked ledger",
                "metaphor": "separate pages aligned by one decision edge",
            },
        ],
        "selected_concept": "layered apparatus",
        "style_family": "deterministic layered apparatus fallback",
        "palette": [
            "#08060F", "#2B2447", "#4E5FA8", "#6E7A5A", "#E4D8C3", "#E0956A"
        ],
        "hue_family": "indigo-warm",
        "composition": "central_apparatus",
        "motifs": ["open coupling", "five abstract layers"],
        "eval_history": [
            {
                "pass": 1,
                "weighted": weighted,
                "scores": scores,
                "weakest": "story_fidelity",
                "observation": "Emergency generic apparatus cannot carry story-specific fidelity.",
                "targeted_fix": "ImageGen must be restored on the next run.",
            }
        ],
        "eval_final": final,
        "fallback_reason": reason,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headline", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--place", default="TEXAS")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base-out")
    parser.add_argument("--eval-out")
    args = parser.parse_args()

    out_path = Path(args.out)
    base_path = (
        Path(args.base_out)
        if args.base_out
        else out_path.with_name("art_base.png")
    )
    eval_path = (
        Path(args.eval_out)
        if args.eval_out
        else out_path.with_name("art_eval.json")
    )
    base_path.parent.mkdir(parents=True, exist_ok=True)
    background().save(base_path, "PNG", optimize=True)
    eval_path.write_text(
        json.dumps(fallback_eval(args.reason), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    compose(
        base_path=base_path,
        headline=args.headline,
        category=args.category,
        date=args.date,
        place=args.place,
        prompt_file=Path(args.prompt_file),
        plan_file=Path(args.plan_file),
        eval_file=eval_path,
        out_path=out_path,
    )
    print(f"Saved disclosed fallback cover {out_path}")


if __name__ == "__main__":
    main()

