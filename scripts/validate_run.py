#!/usr/bin/env python3
"""Validate a complete The Texas Stack output package before commit."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml
from PIL import Image

from check_post import validate_post

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_GATES = {
    "news_tie",
    "anatomizable_depth",
    "primary_source_each_layer",
    "texas_consequence",
    "chokepoint_asymmetry",
    "mechanism_not_actor",
    "not_recent_repeat",
    "political_neutrality",
}
ART_WEIGHTS = {
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


def is_web_url(value: object) -> bool:
    try:
        parsed = urlparse(str(value))
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_date(value: object, label: str, errors: list[str]) -> dt.date | None:
    try:
        return dt.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        errors.append(f"{label} must be an ISO date")
        return None


def require_file(path: Path, errors: list[str]) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        errors.append(f"missing or empty file: {path.name}")
        return False
    return True


def load_json(path: Path, label: str, errors: list[str]) -> dict:
    if not require_file(path, errors):
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} JSON is invalid: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must contain an object")
        return {}
    return value


def validate_source(
    row: object,
    label: str,
    errors: list[str],
    *,
    require_primary: bool = False,
) -> None:
    if not isinstance(row, dict):
        errors.append(f"{label} must be an object")
        return
    for field in ("url", "title", "publisher"):
        if not row.get(field):
            errors.append(f"{label} missing {field}")
    if not is_web_url(row.get("url")):
        errors.append(f"{label} URL must be HTTP or HTTPS")
    if require_primary and row.get("source_type") != "primary":
        errors.append(f"{label} source_type must be primary")
    if not row.get("fetched_at_utc"):
        errors.append(f"{label} missing fetched_at_utc")


def expected_weighted(scores: dict) -> float:
    return sum(float(scores[name]) * weight for name, weight in ART_WEIGHTS.items())


def validate_art(out_dir: Path, errors: list[str]) -> dict:
    for filename in ("art_plan.md", "image_prompt.txt"):
        require_file(out_dir / filename, errors)
    base_path = out_dir / "art_base.png"
    final_path = out_dir / "post_image.png"
    if require_file(base_path, errors):
        try:
            with Image.open(base_path) as image:
                width, height = image.size
                if image.format != "PNG":
                    errors.append("art_base.png must be PNG")
                if width != height or min(width, height) < 768:
                    errors.append("art_base.png must be square and at least 768 pixels")
        except Exception as exc:
            errors.append(f"art_base.png is unreadable: {exc}")
    if require_file(final_path, errors):
        try:
            with Image.open(final_path) as image:
                if image.format != "PNG" or image.size != (1080, 1080):
                    errors.append(
                        f"post_image.png must be 1080 by 1080 PNG, got "
                        f"{image.format} {image.size}"
                    )
        except Exception as exc:
            errors.append(f"post_image.png is unreadable: {exc}")

    art_eval = load_json(out_dir / "art_eval.json", "art evaluation", errors)
    if art_eval:
        if art_eval.get("schema_version") != 1:
            errors.append("art evaluation schema_version must be 1")
        source = art_eval.get("source")
        if source not in {"imagegen", "fallback"}:
            errors.append("art evaluation source must be imagegen or fallback")
        concepts = art_eval.get("concepts")
        if not isinstance(concepts, list) or len(concepts) != 3:
            errors.append("art evaluation must record exactly three concepts")
        for field in (
            "selected_concept", "style_family", "hue_family", "composition",
        ):
            if not art_eval.get(field):
                errors.append(f"art evaluation missing {field}")
        palette = art_eval.get("palette")
        if not isinstance(palette, list) or not 2 <= len(palette) <= 7:
            errors.append("art evaluation palette must contain two to seven colors")
        motifs = art_eval.get("motifs")
        if not isinstance(motifs, list) or not motifs:
            errors.append("art evaluation motifs must be nonempty")
        history = art_eval.get("eval_history")
        if not isinstance(history, list) or not history:
            errors.append("art evaluation history must be nonempty")
            history = []
        if len(history) > 6:
            errors.append("art evaluation may record at most six ImageGen passes")
        final = art_eval.get("eval_final") or {}
        scores = final.get("scores") or {}
        if set(scores) != set(ART_WEIGHTS):
            errors.append("art final scores must use the nine configured dimensions")
        else:
            for name, value in scores.items():
                if not isinstance(value, (int, float)) or not 0 <= value <= 10:
                    errors.append(f"art score {name} must be from zero to ten")
            calculated = expected_weighted(scores)
            if not math.isclose(
                float(final.get("weighted", -1)), calculated, abs_tol=0.011
            ):
                errors.append("art final weighted score does not match dimension scores")
            passed = calculated >= 8.5 and min(float(value) for value in scores.values()) >= 7
            if final.get("passed") is not passed:
                errors.append("art final passed flag does not match the score")
            if source == "imagegen" and not passed:
                if len(history) < 6 or not art_eval.get("shortfall_note"):
                    errors.append(
                        "below-floor ImageGen art requires six passes and a shortfall note"
                    )
        if source == "fallback" and not art_eval.get("fallback_reason"):
            errors.append("fallback art requires a fallback_reason")

    meta = load_json(
        Path(str(final_path) + ".meta.json"),
        "artwork metadata",
        errors,
    )
    if meta:
        for field in (
            "date", "column", "kicker", "category", "headline", "style_family",
            "palette", "hue_family", "composition", "motifs", "source",
            "base_sha256", "prompt_sha256", "plan_sha256", "eval_sha256",
            "eval_history", "eval_final",
        ):
            if meta.get(field) in (None, "", []):
                errors.append(f"artwork metadata missing {field}")
        if meta.get("kicker") != "THE TEXAS STACK":
            errors.append("artwork metadata kicker must be THE TEXAS STACK")
        if meta.get("source") not in {"imagegen", "fallback"}:
            errors.append("artwork metadata source must be imagegen or fallback")
        if art_eval and meta.get("eval_final") != art_eval.get("eval_final"):
            errors.append("artwork metadata eval_final must match art_eval.json")
    return art_eval


def validate_dossier(dossier: dict, errors: list[str]) -> tuple[bool, dict]:
    if dossier.get("schema_version") != 1:
        errors.append("dossier schema_version must be 1")
    run_date = parse_date(dossier.get("run_date"), "dossier run_date", errors)
    state = yaml.safe_load((ROOT / "config/state.yaml").read_text(encoding="utf-8"))
    allowed_windows = {
        int(state["news_window_days"]),
        int(state["broadening_window_days"]),
    }
    if dossier.get("window_days") not in allowed_windows:
        errors.append(f"dossier window_days must be one of {sorted(allowed_windows)}")

    no_target = dossier.get("no_target_this_cycle") is True
    mechanism = dossier.get("selected_mechanism") or {}
    if no_target:
        if dossier.get("selected_mechanism"):
            errors.append("no-target dossier cannot contain a selected mechanism")
        if not dossier.get("_validation_note"):
            errors.append("no-target dossier needs _validation_note")
        dropped = dossier.get("dropped_mechanisms")
        if not isinstance(dropped, list) or not dropped:
            errors.append("no-target dossier needs a nonempty dropped_mechanisms list")
        else:
            for index, row in enumerate(dropped, start=1):
                label = f"dropped mechanism {index}"
                if not isinstance(row, dict):
                    errors.append(f"{label} must be an object")
                    continue
                for field in ("name", "category", "news_trigger", "drop_reason"):
                    if not row.get(field):
                        errors.append(f"{label} missing {field}")
                sources = row.get("sources")
                if not isinstance(sources, list) or not sources:
                    errors.append(f"{label} needs attempted sources")
                else:
                    for source_index, source in enumerate(sources, start=1):
                        validate_source(
                            source,
                            f"{label} source {source_index}",
                            errors,
                        )
        return True, {}

    if dossier.get("no_target_this_cycle") is not False:
        errors.append("target dossier must set no_target_this_cycle false")
    for field in (
        "name", "category", "category_label", "definition", "texas_scope",
        "texas_consequence", "structural_read", "forward_implication",
    ):
        if not mechanism.get(field):
            errors.append(f"selected mechanism missing {field}")
    labels = {
        "facilities": "FACILITIES",
        "vehicles": "VEHICLES",
        "capital_sovereignty": "CAPITAL + SOVEREIGNTY",
        "regulatory": "REGULATORY",
    }
    if mechanism.get("category") not in labels:
        errors.append("selected mechanism category is invalid")
    elif mechanism.get("category_label") != labels[mechanism["category"]]:
        errors.append("selected mechanism category_label does not match category")

    trigger = mechanism.get("news_trigger") or {}
    for field in ("date", "verbatim_span", "post_anchor"):
        if not trigger.get(field):
            errors.append(f"news trigger missing {field}")
    trigger_date = parse_date(trigger.get("date"), "news trigger date", errors)
    if run_date and trigger_date and dossier.get("window_days") in allowed_windows:
        age = (run_date - trigger_date).days
        if age < 0:
            errors.append("news trigger is dated after the run date")
        elif age > int(dossier["window_days"]):
            errors.append("news trigger falls outside the selected window")
    validate_source(trigger.get("source"), "news trigger source", errors)

    layers = mechanism.get("layers")
    if not isinstance(layers, list) or not 3 <= len(layers) <= 5:
        errors.append("selected mechanism needs three to five layers")
        layers = []
    seen_names: set[str] = set()
    source_urls: set[str] = set()
    for index, layer in enumerate(layers, start=1):
        label = f"layer {index}"
        if not isinstance(layer, dict):
            errors.append(f"{label} must be an object")
            continue
        if layer.get("order") != index:
            errors.append(f"{label} order must be {index}")
        for field in (
            "name", "function", "controlling_actor", "actor_authority", "post_phrase",
        ):
            if not layer.get(field):
                errors.append(f"{label} missing {field}")
        normalized = str(layer.get("name", "")).casefold()
        if normalized in seen_names:
            errors.append(f"{label} duplicates a layer name")
        seen_names.add(normalized)
        validate_source(
            layer.get("primary_source"),
            f"{label} primary_source",
            errors,
            require_primary=True,
        )
        source = layer.get("primary_source") or {}
        if is_web_url(source.get("url")):
            source_urls.add(str(source["url"]))

    chokepoint = mechanism.get("chokepoint") or {}
    for field in (
        "layer_order", "layer_name", "controlling_actor", "post_actor_phrase",
        "binary_decision", "post_decision_phrase", "why_asymmetric",
        "primary_source_url",
    ):
        if not chokepoint.get(field):
            errors.append(f"chokepoint missing {field}")
    if isinstance(chokepoint.get("layer_order"), int) and layers:
        order = chokepoint["layer_order"]
        if not 1 <= order <= len(layers):
            errors.append("chokepoint layer_order does not identify a dossier layer")
        elif chokepoint.get("layer_name") != layers[order - 1].get("name"):
            errors.append("chokepoint layer_name does not match its dossier layer")
    if (
        is_web_url(chokepoint.get("primary_source_url"))
        and chokepoint.get("primary_source_url") not in source_urls
    ):
        errors.append("chokepoint primary source must be one of the layer sources")

    next_check = mechanism.get("next_check") or {}
    for field in ("what", "actor", "date_or_window"):
        if not next_check.get(field):
            errors.append(f"next_check missing {field}")

    policy = mechanism.get("public_policy_context") or {}
    if policy.get("is_public_policy") is True:
        if policy.get("editorial_mode") != "neutral_accountability":
            errors.append("public-policy mechanism must use neutral_accountability")
        if policy.get("assessment") != "not_applicable":
            errors.append("public-policy mechanism assessment must be not_applicable")
    elif policy.get("editorial_mode") not in {
        "structural_analysis", "neutral_accountability"
    }:
        errors.append("non-policy mechanism needs a supported editorial_mode")

    gate_results = dossier.get("gate_results")
    if not isinstance(gate_results, dict):
        errors.append("gate_results must be an object")
    else:
        missing = REQUIRED_GATES - set(gate_results)
        extra = set(gate_results) - REQUIRED_GATES
        if missing:
            errors.append(f"dossier gates missing {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"dossier gates contain unknown names {', '.join(sorted(extra))}")
        if not all(gate_results.get(name) is True for name in REQUIRED_GATES):
            errors.append("one or more dossier gates are not true")

    required_phrases = dossier.get("required_post_phrases")
    core_phrases = {
        str(mechanism.get("name", "")).casefold(),
        str(trigger.get("post_anchor", "")).casefold(),
        str(chokepoint.get("post_actor_phrase", "")).casefold(),
        str(chokepoint.get("post_decision_phrase", "")).casefold(),
    }
    if not isinstance(required_phrases, list):
        errors.append("required_post_phrases must be a list")
    else:
        normalized = {str(value).casefold() for value in required_phrases}
        for phrase in core_phrases:
            if phrase and phrase not in normalized:
                errors.append(f"required_post_phrases must include {phrase!r}")

    facts = dossier.get("verified_facts")
    if not isinstance(facts, list) or not facts:
        errors.append("target dossier needs verified_facts")
    else:
        for index, fact in enumerate(facts, start=1):
            if not isinstance(fact, dict) or not fact.get("claim"):
                errors.append(f"verified fact {index} lacks a claim")
                continue
            urls = fact.get("source_urls")
            if not isinstance(urls, list) or not urls or not all(
                is_web_url(url) for url in urls
            ):
                errors.append(f"verified fact {index} needs source_urls")
    return False, mechanism


def validate_score(path: Path, errors: list[str]) -> dict:
    error_count_at_entry = len(errors)
    score = load_json(path, "score report", errors)
    if not score:
        return {}
    rubric = yaml.safe_load((ROOT / "config/rubric.yaml").read_text(encoding="utf-8"))["rubric"]
    expected = {row["name"]: float(row["weight"]) for row in rubric["criteria"]}
    rows = score.get("criteria")
    if not isinstance(rows, list):
        errors.append("score criteria must be a list")
        rows = []
    actual: dict[str, float] = {}
    weighted = 0.0
    for row in rows:
        if not isinstance(row, dict):
            errors.append("score criterion must be an object")
            continue
        name = row.get("name")
        if name not in expected:
            errors.append(f"score contains unknown criterion {name!r}")
            continue
        if name in actual:
            errors.append(f"score duplicates criterion {name!r}")
            continue
        value = row.get("score")
        weight = row.get("weight")
        if not isinstance(value, (int, float)) or not 0 <= value <= 10:
            errors.append(f"score for {name} must be zero to ten")
            continue
        if not math.isclose(float(weight), expected[name], abs_tol=1e-9):
            errors.append(f"weight for {name} does not match rubric")
        actual[name] = float(value)
        weighted += float(value) * expected[name]
    if set(actual) != set(expected):
        errors.append("score report must include every rubric criterion exactly once")
    if not math.isclose(
        float(score.get("weighted_total", -1)), weighted, abs_tol=0.011
    ):
        errors.append("score weighted_total does not match criterion scores")
    if float(score.get("threshold", -1)) != float(rubric["ship_threshold"]):
        errors.append("score threshold does not match rubric")
    hard_checks = score.get("hard_fail_checks")
    expected_hard = {
        row["name"] for row in rubric["hard_fail_checks"]
    }
    if not isinstance(hard_checks, list):
        errors.append("score hard_fail_checks must be a list")
        hard_checks = []
    hard_names = {
        row.get("name") for row in hard_checks if isinstance(row, dict)
    }
    if hard_names != expected_hard:
        errors.append("score hard_fail_checks do not match rubric")
    if any(row.get("passed") is not True for row in hard_checks if isinstance(row, dict)):
        errors.append("score report contains a failed hard check")
    if score.get("hard_failures"):
        errors.append("score report contains hard_failures")
    score_is_valid = len(errors) == error_count_at_entry
    shippable = weighted >= float(rubric["ship_threshold"]) and score_is_valid
    if score.get("ship") is not shippable:
        errors.append("score ship flag does not match the validated score")
    return score


def validate(out_dir: Path) -> dict:
    errors: list[str] = []
    dossier = load_json(out_dir / "stack_anatomy.json", "dossier", errors)
    no_target = False
    if dossier:
        no_target, _ = validate_dossier(dossier, errors)

    post_report: dict = {}
    if no_target:
        for filename in ("final_post.md", "post_check.json", "score_report.json"):
            if (out_dir / filename).exists():
                errors.append(f"no-target package must not contain {filename}")
    elif dossier:
        post_path = out_dir / "final_post.md"
        if require_file(post_path, errors):
            config = yaml.safe_load(
                (ROOT / "config/brand.yaml").read_text(encoding="utf-8")
            )
            post_report = validate_post(
                post_path.read_text(encoding="utf-8"), dossier, config
            )
            errors.extend(f"post: {item}" for item in post_report["errors"])
        validate_score(out_dir / "score_report.json", errors)
        check = load_json(out_dir / "post_check.json", "post check", errors)
        if check and check.get("ok") is not True:
            errors.append("persisted post_check.json is not passing")

    art_eval = validate_art(out_dir, errors)
    return {
        "ok": not errors,
        "errors": errors,
        "mode": "no-target" if no_target else "target",
        "post_metrics": post_report.get("metrics", {}),
        "art_source": art_eval.get("source"),
        "art_weighted": (art_eval.get("eval_final") or {}).get("weighted"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="out")
    parser.add_argument("--report")
    args = parser.parse_args()
    result = validate(Path(args.out_dir))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        destination = Path(args.report)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
