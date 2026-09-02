#!/usr/bin/env python3
"""Technical and ledger gate for The Texas Stack artwork."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

WEIGHTS = {
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
REQUIRED_META = [
    "date", "column", "kicker", "category", "headline", "style_family",
    "palette", "hue_family", "composition", "motifs", "technique_stack",
    "source", "seed", "base_sha256", "prompt_sha256", "plan_sha256",
    "eval_sha256", "eval_history", "eval_final",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(
    image_path: Path,
    base_path: Path,
    prompt_path: Path,
    plan_path: Path,
    eval_path: Path,
    date: str,
    column: str,
) -> list[str]:
    errors: list[str] = []
    for path in (image_path, base_path, prompt_path, plan_path, eval_path):
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty file {path}")
    if errors:
        return errors

    try:
        with Image.open(image_path) as opened:
            image_format = opened.format
            image_size = opened.size
            pixels = np.asarray(opened.convert("RGB"), dtype=float)
            thumbnail = np.asarray(opened.convert("RGB").resize((128, 128)))
    except Exception as exc:
        return [f"image cannot be opened: {exc}"]
    if image_format != "PNG":
        errors.append(f"format is {image_format}, expected PNG")
    if image_size != (1080, 1080):
        errors.append(f"dimensions are {image_size}, expected 1080 by 1080")
    size_kb = image_path.stat().st_size / 1024
    if not 60 <= size_kb <= 8000:
        errors.append(f"file size {size_kb:.0f} KB is outside 60 to 8000 KB")
    if pixels.std() < 15:
        errors.append(f"pixel standard deviation {pixels.std():.1f} suggests a blank image")
    if len(np.unique(thumbnail.reshape(-1, 3), axis=0)) < 60:
        errors.append("thumbnail has too few distinct colors")

    try:
        art_eval = json.loads(eval_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"art evaluation is invalid: {exc}")
        art_eval = {}
    history = art_eval.get("eval_history") or []
    final = art_eval.get("eval_final") or {}
    scores = final.get("scores") or {}
    if set(scores) != set(WEIGHTS):
        errors.append("art evaluation has the wrong scoring dimensions")
    else:
        weighted = sum(float(scores[name]) * weight for name, weight in WEIGHTS.items())
        if not math.isclose(float(final.get("weighted", -1)), weighted, abs_tol=0.011):
            errors.append("art evaluation weighted score is inconsistent")
        passed = weighted >= 8.5 and min(float(value) for value in scores.values()) >= 7
        if final.get("passed") is not passed:
            errors.append("art evaluation passed flag is inconsistent")
        if art_eval.get("source") == "imagegen" and not passed:
            if len(history) < 6 or not art_eval.get("shortfall_note"):
                errors.append(
                    "below-floor ImageGen art requires six passes and a shortfall note"
                )
    if art_eval.get("source") == "fallback" and not art_eval.get("fallback_reason"):
        errors.append("fallback art is missing its failure reason")

    meta_path = Path(str(image_path) + ".meta.json")
    if not meta_path.is_file():
        errors.append("metadata sidecar is missing")
        return errors
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"metadata sidecar is invalid: {exc}")
        return errors
    for key in REQUIRED_META:
        if meta.get(key) in (None, "", []):
            errors.append(f"metadata missing {key}")
    if meta.get("date") != date.upper():
        errors.append(f"metadata date {meta.get('date')!r} does not match {date.upper()!r}")
    if meta.get("kicker") != column:
        errors.append(f"metadata kicker {meta.get('kicker')!r} does not match {column!r}")
    if meta.get("source") != art_eval.get("source"):
        errors.append("metadata source does not match art evaluation")
    if meta.get("eval_final") != final:
        errors.append("metadata final evaluation does not match art_eval.json")
    for key, path in (
        ("base_sha256", base_path),
        ("prompt_sha256", prompt_path),
        ("plan_sha256", plan_path),
        ("eval_sha256", eval_path),
    ):
        if meta.get(key) != sha256(path):
            errors.append(f"metadata {key} does not match {path.name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--eval", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--column", required=True)
    args = parser.parse_args()
    errors = validate(
        Path(args.image),
        Path(args.base),
        Path(args.prompt),
        Path(args.plan),
        Path(args.eval),
        args.date,
        args.column,
    )
    if errors:
        print("FAIL: artwork")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"PASS: {args.image} is a complete 1080 by 1080 "
        f"{args.column} cover with a valid evaluation ledger"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

