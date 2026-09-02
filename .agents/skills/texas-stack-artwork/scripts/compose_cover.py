#!/usr/bin/env python3
"""Apply exact Texas AI Docket furniture to generated Texas Stack art."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

SIZE = 1080
SCRIPT_DIR = Path(__file__).resolve().parent
FONT_DIR = SCRIPT_DIR / "fonts"
FONT_URLS = {
    "Fraunces.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/fraunces/"
        "Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf"
    ),
    "JetBrainsMono.ttf": (
        "https://github.com/JetBrains/JetBrainsMono/raw/master/fonts/ttf/"
        "JetBrainsMono-Medium.ttf"
    ),
}
FALLBACK_SERIF = [
    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
FALLBACK_MONO = [
    "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]
CATEGORIES = {
    "FACILITIES", "VEHICLES", "CAPITAL + SOVEREIGNTY", "REGULATORY", "WATCH"
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_font(filename: str, fallbacks: list[str]) -> str:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    destination = FONT_DIR / filename
    if destination.is_file() and destination.stat().st_size > 1000:
        return str(destination)
    try:
        request = urllib.request.Request(
            FONT_URLS[filename], headers={"User-Agent": "TexasStack/1"}
        )
        with urllib.request.urlopen(request, timeout=25) as response:
            data = response.read()
        if len(data) > 1000:
            destination.write_bytes(data)
            return str(destination)
    except Exception:
        pass
    for candidate in fallbacks:
        if Path(candidate).is_file():
            return candidate
    raise RuntimeError(f"No usable font found for {filename}")


def font_pair() -> tuple[str, str]:
    return (
        ensure_font("Fraunces.ttf", FALLBACK_SERIF),
        ensure_font("JetBrainsMono.ttf", FALLBACK_MONO),
    )


def tracked_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    tracking: int,
) -> int:
    return sum(int(draw.textlength(ch, font=font)) + tracking for ch in text) - tracking


def draw_tracked(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    tracking: int,
) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += int(draw.textlength(char, font=font)) + tracking


def fit_tracked(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    max_width: int,
    start_size: int = 18,
) -> tuple[ImageFont.FreeTypeFont, int]:
    for size in range(start_size, 10, -1):
        for tracking in (2, 1, 0):
            font = ImageFont.truetype(font_path, size)
            if tracked_width(draw, text, font, tracking) <= max_width:
                return font, tracking
    raise ValueError(f"text is too long for publication furniture: {text}")


def star_points(cx: float, cy: float, radius: float) -> list[tuple[float, float]]:
    points = []
    for index in range(10):
        angle = math.radians(-90 + 36 * index)
        length = radius if index % 2 == 0 else radius * 0.43
        points.append((cx + math.cos(angle) * length, cy + math.sin(angle) * length))
    return points


def wrap_headline(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    max_width: int,
    max_lines: int = 3,
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    words = " ".join(text.replace("\\n", "\n").splitlines()).split()
    if not 4 <= len(words) <= 9:
        raise ValueError("headline must contain four to nine words")
    for size in range(96, 49, -2):
        font = ImageFont.truetype(font_path, size)
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textlength(candidate, font=font) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        if len(lines) <= max_lines and all(
            draw.textlength(line, font=font) <= max_width for line in lines
        ):
            return lines, font
    raise ValueError("headline cannot fit the cover; shorten it")


def dark_overlay() -> Image.Image:
    y = np.arange(SIZE, dtype=float)
    top = np.where(y < 300, 215 * (1 - y / 300), 0)
    bottom = np.where(y > 575, 238 * ((y - 575) / (SIZE - 575)), 0)
    alpha = np.maximum(top, bottom).clip(0, 238).astype(np.uint8)
    array = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    array[:, :, 0] = 8
    array[:, :, 1] = 6
    array[:, :, 2] = 15
    array[:, :, 3] = alpha[:, None]
    return Image.fromarray(array, "RGBA")


def compose(
    *,
    base_path: Path,
    headline: str,
    category: str,
    date: str,
    place: str,
    prompt_file: Path,
    plan_file: Path,
    eval_file: Path,
    out_path: Path,
) -> Path:
    category = category.upper().strip()
    if category not in CATEGORIES:
        raise ValueError(f"category must be one of {sorted(CATEGORIES)}")
    art_eval = json.loads(eval_file.read_text(encoding="utf-8"))
    source = art_eval.get("source")
    if source not in {"imagegen", "fallback"}:
        raise ValueError("art evaluation source must be imagegen or fallback")

    serif_path, mono_path = font_pair()
    base = Image.open(base_path).convert("RGB")
    canvas = ImageOps.fit(base, (SIZE, SIZE), method=Image.Resampling.LANCZOS)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.035)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), dark_overlay())
    draw = ImageDraw.Draw(canvas)

    wordmark_font = ImageFont.truetype(serif_path, 42)
    small_font = ImageFont.truetype(mono_path, 14)
    footer_font = ImageFont.truetype(mono_path, 14)
    ink = "#F6F1E4"
    gold = "#E0956A"
    dust = "#C9B393"

    draw.polygon(star_points(76, 69, 21), fill=gold)
    draw.text((112, 39), "TEXAS AI DOCKET", font=wordmark_font, fill=ink)

    date_text = date.upper()
    date_font, date_tracking = fit_tracked(
        draw, date_text, mono_path, 410, start_size=16
    )
    date_width = tracked_width(draw, date_text, date_font, date_tracking)
    draw_tracked(
        draw, (SIZE - 64 - date_width, 52), date_text, date_font, dust, date_tracking
    )

    kicker = f"THE TEXAS STACK · {category}"
    kicker_font, kicker_tracking = fit_tracked(
        draw, kicker, mono_path, SIZE - 128, start_size=18
    )
    draw_tracked(draw, (64, 111), kicker, kicker_font, gold, kicker_tracking)
    draw.line((64, 157, SIZE - 64, 157), fill=gold, width=2)

    lines, headline_font = wrap_headline(
        draw, headline.upper(), serif_path, SIZE - 128
    )
    line_height = int(headline_font.size * 0.98)
    total_height = len(lines) * line_height
    headline_y = max(665, 946 - total_height)
    for index, line in enumerate(lines):
        draw.text(
            (64, headline_y + index * line_height),
            line,
            font=headline_font,
            fill=ink,
            stroke_width=1,
            stroke_fill="#08060F",
        )

    draw.line((64, 968, SIZE - 64, 968), fill=dust, width=1)
    place_text = place.upper().strip() or "TEXAS"
    place_font, place_tracking = fit_tracked(
        draw, place_text, mono_path, 540, start_size=14
    )
    draw_tracked(
        draw, (64, 1001), place_text, place_font, dust, place_tracking
    )
    site = "TEXASAIDOCKET.COM"
    site_width = tracked_width(draw, site, footer_font, 1)
    draw_tracked(
        draw, (SIZE - 64 - site_width, 1001), site, footer_font, dust, 1
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, "PNG", optimize=True)
    meta = {
        "schema_version": 1,
        "date": date.upper(),
        "column": "The Texas Stack",
        "kicker": "THE TEXAS STACK",
        "category": category,
        "headline": " ".join(headline.upper().split()),
        "place": place_text,
        "style_family": art_eval.get("style_family"),
        "palette": art_eval.get("palette"),
        "hue_family": art_eval.get("hue_family"),
        "composition": art_eval.get("composition"),
        "motifs": art_eval.get("motifs"),
        "technique_stack": [
            "built-in imagegen" if source == "imagegen" else "deterministic fallback",
            "deterministic typography overlay",
        ],
        "source": source,
        "seed": "imagegen-managed" if source == "imagegen" else 1845,
        "base_sha256": sha256(base_path),
        "prompt_sha256": sha256(prompt_file),
        "plan_sha256": sha256(plan_file),
        "eval_sha256": sha256(eval_file),
        "eval_history": art_eval.get("eval_history"),
        "eval_final": art_eval.get("eval_final"),
        "shortfall_note": art_eval.get("shortfall_note", ""),
        "fallback_reason": art_eval.get("fallback_reason", ""),
        "rendered_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "canvas": [SIZE, SIZE],
    }
    Path(str(out_path) + ".meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--place", default="TEXAS")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--plan-file", required=True)
    parser.add_argument("--eval-file", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = compose(
        base_path=Path(args.base),
        headline=args.headline,
        category=args.category,
        date=args.date,
        place=args.place,
        prompt_file=Path(args.prompt_file),
        plan_file=Path(args.plan_file),
        eval_file=Path(args.eval_file),
        out_path=Path(args.out),
    )
    print(f"Saved {result}")


if __name__ == "__main__":
    main()

