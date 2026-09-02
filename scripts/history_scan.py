#!/usr/bin/env python3
"""Build mechanism and artwork cooldown ledgers from prior run branches."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

BRANCH_RE = re.compile(
    r"(?:origin/)?codex/texas-stack-(\d{4}-\d{2}-\d{2})(?:-(\d+))?$"
)


def git_output(repo: Path, *args: str, required: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if required and result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout if result.returncode == 0 else ""


def show_json(repo: Path, ref: str, path: str) -> dict | None:
    raw = git_output(repo, "show", f"{ref}:{path}", required=False)
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def stack_records(repo: Path) -> list[dict]:
    raw = git_output(
        repo,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/remotes/origin/codex/texas-stack-*",
        required=False,
    )
    records: list[dict] = []
    for ref in filter(None, (line.strip() for line in raw.splitlines())):
        match = BRANCH_RE.search(ref)
        if not match:
            continue
        dossier = show_json(repo, ref, "out/stack_anatomy.json")
        meta = show_json(repo, ref, "out/post_image.png.meta.json")
        records.append({
            "branch": ref,
            "date": match.group(1),
            "suffix": int(match.group(2) or 1),
            "dossier": dossier,
            "art": meta,
        })
    records.sort(key=lambda row: (row["date"], row["suffix"]), reverse=True)
    return records


def sibling_art_records(repo: Path) -> list[dict]:
    if not (repo / ".git").is_dir():
        return []
    raw = git_output(
        repo,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/remotes/origin/codex/texas-desk-*",
        required=False,
    )
    records: list[dict] = []
    for ref in filter(None, (line.strip() for line in raw.splitlines())):
        meta = show_json(repo, ref, "out/post_image.png.meta.json")
        if not meta:
            continue
        records.append({
            "branch": f"texas-desk:{ref}",
            "date": str(meta.get("date", "")),
            "art": meta,
        })
    return records


def nonempty(records: list[dict], key: str, limit: int) -> list[str]:
    values: list[str] = []
    for record in records:
        art = record.get("art") or {}
        value = art.get(key)
        if isinstance(value, str) and value.strip() and value not in values:
            values.append(value)
        if len(values) >= limit:
            break
    return values


def primary_motifs(records: list[dict], limit: int) -> list[str]:
    values: list[str] = []
    for record in records:
        motifs = (record.get("art") or {}).get("motifs") or []
        if motifs:
            motif = str(motifs[0]).strip()
            if motif and motif not in values:
                values.append(motif)
        if len(values) >= limit:
            break
    return values


def summarize(records: list[dict], sibling_art: list[dict], today: dt.date) -> dict:
    mechanisms: list[dict] = []
    for record in records:
        dossier = record.get("dossier") or {}
        selected = dossier.get("selected_mechanism") or {}
        if dossier.get("no_target_this_cycle") or not selected.get("name"):
            continue
        mechanisms.append({
            "name": selected["name"],
            "category": selected.get("category"),
            "chokepoint": (selected.get("chokepoint") or {}).get("layer_name"),
            "run_date": record["date"],
            "branch": record["branch"],
        })
        if len(mechanisms) >= 6:
            break

    all_art = [
        record for record in records if record.get("art")
    ] + sibling_art
    return {
        "schema_version": 1,
        "as_of": today.isoformat(),
        "recent_mechanisms": mechanisms,
        "artwork_cooldowns": {
            "style_families_last_8": nonempty(all_art, "style_family", 8),
            "hue_families_last_4": nonempty(all_art, "hue_family", 4),
            "compositions_last_2": nonempty(all_art, "composition", 2),
            "primary_motifs_last_10": primary_motifs(all_art, 10),
        },
        "stack_branches_scanned": len(records),
        "sibling_art_ledgers_scanned": len(sibling_art),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sibling-art-repo", default="../LinkedInTexasAIDesk")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    sibling = Path(args.sibling_art_repo)
    if not sibling.is_absolute():
        sibling = (repo / sibling).resolve()
    today = dt.date.fromisoformat(args.date)
    result = summarize(
        stack_records(repo),
        sibling_art_records(sibling),
        today,
    )
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"history: {len(result['recent_mechanisms'])} recent mechanisms, "
        f"{result['stack_branches_scanned']} stack branches, "
        f"{result['sibling_art_ledgers_scanned']} sibling art ledgers"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

