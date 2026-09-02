#!/usr/bin/env python3
"""Validate the versioned contracts for The Texas Stack."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str, errors: list[str]) -> dict:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing {relative}")
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{relative} is not valid YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{relative} must contain a mapping")
        return {}
    return value


def is_url(value: object) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate() -> list[str]:
    errors: list[str] = []
    brand = load("config/brand.yaml", errors)
    state = load("config/state.yaml", errors)
    rubric_file = load("config/rubric.yaml", errors)
    sources = load("config/sources.yaml", errors)

    expected_state = {
        "brand_name": "Texas AI Docket",
        "column_name": "The Texas Stack",
        "kicker": "THE TEXAS STACK",
        "timezone": "America/Chicago",
        "news_window_days": 14,
        "broadening_window_days": 21,
        "branch_prefix": "codex/texas-stack",
        "repository": "Talonsturgill/linkedin-texas-ai-stack",
        "artifact_size": [1080, 1080],
    }
    for key, expected in expected_state.items():
        if state.get(key) != expected:
            errors.append(f"config/state.yaml {key} must be {expected!r}")

    schedule = state.get("schedule") or {}
    if schedule.get("cadence") != "weekly" or schedule.get("day") != "Friday":
        errors.append("schedule must be weekly on Friday")
    if schedule.get("local_time") != "08:00":
        errors.append("schedule local_time must be 08:00")

    brand_block = brand.get("brand") or {}
    if brand_block.get("name") != "Texas AI Docket":
        errors.append("brand name must be Texas AI Docket")
    if brand_block.get("column") != "The Texas Stack":
        errors.append("brand column must be The Texas Stack")
    visual = brand.get("visual") or {}
    category_labels = visual.get("category_labels") or {}
    expected_categories = {
        "facilities", "vehicles", "capital_sovereignty", "regulatory"
    }
    if set(category_labels) != expected_categories:
        errors.append("visual category labels must cover the four mechanism categories")

    platform = brand.get("platform") or {}
    if platform.get("body_words") != [350, 475]:
        errors.append("platform body_words must be 350 to 475")
    if platform.get("total_chars_max") != 3000:
        errors.append("platform total_chars_max must be 3000")
    if platform.get("hashtag_count") != 3:
        errors.append("platform hashtag_count must be exactly 3")

    hashtags = (brand.get("hashtags") or {}).get("whitelist") or []
    if len(hashtags) < 8 or len(hashtags) != len(set(hashtags)):
        errors.append("hashtag whitelist must contain at least eight unique values")
    if any(not isinstance(tag, str) or not tag.startswith("#") for tag in hashtags):
        errors.append("every approved hashtag must begin with #")

    rubric = rubric_file.get("rubric") or {}
    criteria = rubric.get("criteria") or []
    weights = [row.get("weight") for row in criteria if isinstance(row, dict)]
    if not weights or not all(isinstance(value, (int, float)) for value in weights):
        errors.append("rubric criteria need numeric weights")
    elif not math.isclose(sum(weights), 1.0, abs_tol=1e-9):
        errors.append(f"rubric weights sum to {sum(weights)}, expected 1.0")
    names = [row.get("name") for row in criteria if isinstance(row, dict)]
    if len(names) != len(set(names)):
        errors.append("rubric criterion names must be unique")
    hard_names = {
        row.get("name") for row in rubric.get("hard_fail_checks", [])
        if isinstance(row, dict)
    }
    for required in {
        "seven_point_gate", "mechanism_and_trigger", "layer_fidelity",
        "specific_chokepoint", "fact_trace", "political_neutrality",
        "linkedin_constraints", "house_style",
    }:
        if required not in hard_names:
            errors.append(f"rubric missing hard fail {required}")

    policy = sources.get("source_policy") or {}
    if policy.get("primary_required_per_layer") is not True:
        errors.append("sources must require a primary source per layer")
    if policy.get("fetched_pages_only") is not True:
        errors.append("sources must require fetched pages")
    seed_sources = sources.get("seed_sources") or {}
    if not seed_sources:
        errors.append("config/sources.yaml needs seed sources")
    for group, rows in seed_sources.items():
        if not isinstance(rows, list) or not rows:
            errors.append(f"source group {group} must be nonempty")
            continue
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict) or not is_url(row.get("url")):
                errors.append(f"source group {group} item {index} needs an HTTPS URL")
            if not isinstance(row, dict) or not row.get("outlet"):
                errors.append(f"source group {group} item {index} needs an outlet")

    routine = (ROOT / "prompts/texas_stack_routine.md").read_text(encoding="utf-8")
    for phrase in (
        "built-in ImageGen", "Gmail draft", "no-target", "codex/texas-stack",
        "America/Chicago", "8.5",
    ):
        if phrase not in routine:
            errors.append(f"master routine missing required phrase {phrase!r}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL: configuration")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("PASS: The Texas Stack configuration contracts are internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())

