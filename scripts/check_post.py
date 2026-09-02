#!/usr/bin/env python3
"""Deterministic hard gate for a The Texas Stack LinkedIn post."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

WORD_RE = re.compile(r"\b[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?\b")
NUMBER_RE = re.compile(r"(?<![A-Za-z])\$?\d[\d,]*(?:\.\d+)?")
LINK_RE = re.compile(r"(?:https?://|www\.)", re.I)
FIRST_PERSON_RE = re.compile(r"\b(?:I|me|my|mine|we|us|our|ours)\b", re.I)
POLITICAL_ADVOCACY_RE = re.compile(
    r"\b(?:vote\s+(?:for|against)|elect|re-elect|defeat|endorse|"
    r"best\s+candidate|worst\s+candidate|support\s+the\s+candidate|"
    r"oppose\s+the\s+candidate)\b",
    re.I,
)
EMOJI_RE = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "]+"
)


def split_post(text: str) -> tuple[str, list[str], str]:
    lines = text.strip().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    tag_line = lines[-1].strip() if lines else ""
    tokens = tag_line.split()
    tags = tokens if tokens and all(token.startswith("#") for token in tokens) else []
    body_lines = lines[:-1] if tags else lines
    return "\n".join(body_lines).strip(), tags, tag_line


def canonical_number(token: str) -> str:
    value = token.replace("$", "").replace(",", "")
    if "." in value:
        value = value.rstrip("0").rstrip(".")
    return value.lstrip("0") or "0"


def dossier_numbers(dossier: dict) -> set[str]:
    blob = json.dumps(dossier, ensure_ascii=False, sort_keys=True)
    return {canonical_number(match.group(0)) for match in NUMBER_RE.finditer(blob)}


def allowed_quotes(dossier: dict) -> set[str]:
    mechanism = dossier.get("selected_mechanism") or {}
    rows = mechanism.get("verbatim_quotes") or []
    return {
        str(row.get("text", ""))
        for row in rows
        if isinstance(row, dict) and row.get("text")
    }


def validate_post(post_text: str, dossier: dict, config: dict) -> dict:
    errors: list[str] = []
    body, tags, tag_line = split_post(post_text)
    platform = config["platform"]
    mechanism = dossier.get("selected_mechanism") or {}
    layers = mechanism.get("layers") or []
    body_words = WORD_RE.findall(body)
    total_chars = len(post_text.strip())
    lowered = body.casefold()

    low_words, high_words = platform["body_words"]
    if not low_words <= len(body_words) <= high_words:
        errors.append(
            f"body word count {len(body_words)} outside {low_words} to {high_words}"
        )
    if total_chars > platform["total_chars_max"]:
        errors.append(
            f"total character count {total_chars} exceeds {platform['total_chars_max']}"
        )

    for token in config["house_rules"]["punctuation"]["forbidden"]:
        if token in body:
            errors.append(f"forbidden punctuation {token!r} appears in body")
    if any(token in body for token in ("“", "”", "‘", "’")):
        errors.append("curly quotes are forbidden; use straight quotes")
    if EMOJI_RE.search(body):
        errors.append("emoji appears in body")
    if FIRST_PERSON_RE.search(body):
        errors.append("first-person language appears in body")
    if POLITICAL_ADVOCACY_RE.search(body):
        errors.append("candidate or electoral advocacy appears in body")
    if LINK_RE.search(body):
        errors.append("post body contains a link; sources belong in the email")

    for phrase in config.get("banned_phrases", []):
        if phrase.casefold() in lowered:
            errors.append(f"banned phrase appears: {phrase}")
    nonempty = [line.strip() for line in body.splitlines() if line.strip()]
    first_line = nonempty[0].casefold() if nonempty else ""
    for opener in config.get("banned_openers", []):
        if first_line.startswith(opener.casefold()):
            errors.append(f"banned opener appears: {opener}")

    expected_tags = platform["hashtag_count"]
    if len(tags) != expected_tags:
        errors.append(f"hashtag count {len(tags)} does not equal {expected_tags}")
    whitelist = set(config["hashtags"]["whitelist"])
    for tag in tags:
        if tag not in whitelist:
            errors.append(f"hashtag is not approved: {tag}")
    if len(tags) != len(set(tags)):
        errors.append("hashtag line contains duplicates")
    if "#" in body:
        errors.append("hashtags may appear only on the final line")

    if not nonempty or not nonempty[-1].endswith("?"):
        errors.append("body must end with a specific chokepoint question")
    hook = " ".join(nonempty[:2])
    if len(hook) > platform["hook_chars_max"]:
        errors.append(
            f"first two nonempty lines are {len(hook)} characters, above "
            f"{platform['hook_chars_max']}"
        )

    if dossier.get("no_target_this_cycle"):
        errors.append("a no-target dossier cannot have a final post")
    name = str(mechanism.get("name", "")).strip()
    trigger = mechanism.get("news_trigger") or {}
    trigger_anchor = str(trigger.get("post_anchor", "")).strip()
    for label, value in (
        ("mechanism name", name),
        ("news trigger anchor", trigger_anchor),
    ):
        if not value or value.casefold() not in hook.casefold():
            errors.append(f"{label} is missing from the first two lines")

    required_phrases = dossier.get("required_post_phrases") or []
    for phrase in required_phrases:
        if str(phrase).casefold() not in lowered:
            errors.append(f"required dossier phrase is missing: {phrase}")

    bullet_lines = [line.strip() for line in body.splitlines() if line.strip().startswith("- ")]
    min_bullets, max_bullets = platform["layer_bullets"]
    if not min_bullets <= len(bullet_lines) <= max_bullets:
        errors.append(
            f"layer bullet count {len(bullet_lines)} outside {min_bullets} to {max_bullets}"
        )
    if len(bullet_lines) != len(layers):
        errors.append(
            f"layer bullet count {len(bullet_lines)} does not match dossier layer count "
            f"{len(layers)}"
        )
    for index, layer in enumerate(layers):
        if index >= len(bullet_lines):
            break
        bullet = bullet_lines[index].casefold()
        for label, value in (
            ("layer name", layer.get("name")),
            ("layer actor phrase", layer.get("post_phrase")),
        ):
            if not value or str(value).casefold() not in bullet:
                errors.append(f"{label} missing from bullet {index + 1}")

    chokepoint = mechanism.get("chokepoint") or {}
    for label, value in (
        ("chokepoint actor", chokepoint.get("post_actor_phrase")),
        ("chokepoint decision", chokepoint.get("post_decision_phrase")),
    ):
        if not value or str(value).casefold() not in lowered:
            errors.append(f"{label} phrase is missing from body")

    quotes = allowed_quotes(dossier)
    for quoted in re.findall(r'"([^"\n]+)"', body):
        if quoted not in quotes:
            errors.append(f"quote is not verbatim in dossier: {quoted[:80]}")

    allowed_numbers = dossier_numbers(dossier)
    for match in NUMBER_RE.finditer(body):
        raw = match.group(0)
        if canonical_number(raw) not in allowed_numbers:
            errors.append(f"numeral is not grounded in dossier: {raw}")

    gate_results = dossier.get("gate_results")
    if not isinstance(gate_results, dict) or not gate_results:
        errors.append("dossier gate_results are missing")
    elif not all(value is True for value in gate_results.values()):
        errors.append("not every dossier gate result is true")

    policy = mechanism.get("public_policy_context") or {}
    if policy.get("is_public_policy") is True:
        if policy.get("editorial_mode") != "neutral_accountability":
            errors.append("public-policy mechanism must use neutral_accountability")
        if policy.get("assessment") != "not_applicable":
            errors.append("public-policy mechanism cannot receive an editorial rating")

    return {
        "ok": not errors,
        "errors": errors,
        "metrics": {
            "body_words": len(body_words),
            "total_chars": total_chars,
            "hook_chars": len(hook),
            "layer_bullets": len(bullet_lines),
            "hashtags": tags,
            "tag_line": tag_line,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", required=True)
    parser.add_argument("--dossier", required=True)
    parser.add_argument("--config", default="config/brand.yaml")
    parser.add_argument("--report")
    args = parser.parse_args()
    post = Path(args.post).read_text(encoding="utf-8")
    dossier = json.loads(Path(args.dossier).read_text(encoding="utf-8"))
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    report = validate_post(post, dossier, config)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

