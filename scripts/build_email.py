#!/usr/bin/env python3
"""Build the HTML payload for an unsent The Texas Stack Gmail draft."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

CSS = """
body{margin:0;padding:24px;background:#08060f;color:#191530;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:760px;margin:0 auto;background:#f6f1e4;border:1px solid #cfc2a6;border-radius:14px;overflow:hidden}
.mast{padding:26px 30px;background:#0f0c1c;color:#ede6d6;border-bottom:4px solid #e0956a}
.mast h1{margin:0;font-size:23px}.mast p{margin:7px 0 0;color:#c9b393;font-size:13px}
.body{padding:26px 30px}h2{font-size:16px;margin:28px 0 9px;border-bottom:1px solid #cfc2a6;padding-bottom:7px}
pre.post{white-space:pre-wrap;overflow-wrap:anywhere;background:#fff;border:1px solid #cfc2a6;border-radius:9px;padding:18px;font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace}
.image{text-align:center;margin:20px 0}.image img{max-width:100%;height:auto;border-radius:8px;border:1px solid #cfc2a6}
.link{font-size:12px;overflow-wrap:anywhere;margin-top:8px}.note{background:#ede6d6;border-left:4px solid #4e5fa8;padding:12px 14px;border-radius:5px;line-height:1.5}
.warning{background:#fff4e8;border-left-color:#9a3b2a}.no-target{background:#fff4e8;border-left:4px solid #9a3b2a;padding:15px;font-weight:700}
ul{padding-left:22px}li{margin:7px 0}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:7px;text-align:left;border-bottom:1px solid #cfc2a6;vertical-align:top}
.metric{display:inline-block;margin:3px 8px 3px 0;padding:5px 8px;background:#fff;border:1px solid #cfc2a6;border-radius:6px}
.foot{color:#6d6252;font-size:11px;margin-top:26px}
"""
IMAGE_URL_RE = re.compile(
    r"https://raw\.githubusercontent\.com/Talonsturgill/"
    r"linkedin-texas-ai-stack/[0-9a-f]{40}/out/post_image\.png"
)


def safe(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def source_rows(dossier: dict) -> list[dict]:
    rows: list[dict] = []
    if dossier.get("no_target_this_cycle"):
        for candidate in dossier.get("dropped_mechanisms", []):
            rows.extend(candidate.get("sources") or [])
    else:
        mechanism = dossier.get("selected_mechanism") or {}
        trigger = mechanism.get("news_trigger") or {}
        if isinstance(trigger.get("source"), dict):
            rows.append(trigger["source"])
        for layer in mechanism.get("layers") or []:
            if isinstance(layer.get("primary_source"), dict):
                rows.append(layer["primary_source"])
        rows.extend(mechanism.get("sources") or [])
    deduped: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url", ""))
        if not url.startswith(("https://", "http://")) or url in seen:
            continue
        seen.add(url)
        deduped.append(row)
    return deduped


def art_summary(art_eval: dict) -> str:
    final = art_eval.get("eval_final") or {}
    scores = final.get("scores") or {}
    weakest = ""
    if scores:
        weakest_name = min(scores, key=lambda key: float(scores[key]))
        weakest = (
            f'<span class="metric">Weakest {safe(weakest_name)} '
            f'{safe(scores[weakest_name])}</span>'
        )
    return (
        f'<span class="metric">Source {safe(art_eval.get("source"))}</span>'
        f'<span class="metric">Weighted {safe(final.get("weighted"))} / 10</span>'
        f'<span class="metric">Passes {safe(len(art_eval.get("eval_history") or []))}</span>'
        f'{weakest}'
    )


def render_html(*, post: str, image_url: str, dossier: dict, score: dict,
                art_eval: dict, date: str, branch: str, commit: str,
                editor_note: str) -> str:
    no_target = dossier.get("no_target_this_cycle") is True
    source_items = []
    for row in source_rows(dossier):
        source_items.append(
            f'<li><a href="{safe(row.get("url"))}">'
            f'{safe(row.get("title") or row.get("publisher") or row.get("url"))}</a>'
            f' · {safe(row.get("publisher"))} · {safe(row.get("source_type", "source"))}</li>'
        )
    if not source_items:
        source_items.append("<li>No readable source survived this cycle.</li>")

    image = (
        f'<div class="image"><a href="{safe(image_url)}"><img src="{safe(image_url)}" '
        'alt="The Texas Stack LinkedIn cover"></a>'
        f'<div class="link">Open or save the image · '
        f'<a href="{safe(image_url)}">{safe(image_url)}</a></div></div>'
    )

    score_rows = []
    for row in score.get("criteria", []):
        score_rows.append(
            f"<tr><td>{safe(row.get('name'))}</td><td>{safe(row.get('score'))}</td>"
            f"<td>{safe(row.get('weight'))}</td><td>{safe(row.get('notes'))}</td></tr>"
        )
    score_table = ""
    if score_rows:
        score_table = (
            "<h2>Editorial report card</h2><table><tr><th>Criterion</th><th>Score</th>"
            "<th>Weight</th><th>Notes</th></tr>" + "".join(score_rows) + "</table>"
            f"<p><b>Weighted total</b> {safe(score.get('weighted_total'))} / 10 · "
            f"<b>Threshold</b> {safe(score.get('threshold'))} · "
            f"<b>Ship</b> {safe('yes' if score.get('ship') else 'no')}</p>"
        )

    if no_target:
        dropped = "".join(
            f"<li><b>{safe(row.get('name'))}</b> · {safe(row.get('news_trigger'))} · "
            f"{safe(row.get('drop_reason'))}</li>"
            for row in dossier.get("dropped_mechanisms", [])
        ) or "<li>No candidate reached validation.</li>"
        content = (
            '<div class="no-target">NO DEFENSIBLE TARGET THIS CYCLE</div>'
            f'<p>{safe(dossier.get("_validation_note"))}</p>'
            f"<h2>Dropped mechanisms</h2><ul>{dropped}</ul>{image}"
        )
    else:
        content = (
            f'<h2>Copy this for LinkedIn</h2><pre class="post">{safe(post)}</pre>{image}'
        )

    warning = (
        art_eval.get("source") != "imagegen"
        or not (art_eval.get("eval_final") or {}).get("passed")
        or (not no_target and not score.get("ship"))
    )
    note_class = "note warning" if warning else "note"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="wrap"><div class="mast"><h1>TEXAS AI DOCKET · THE TEXAS STACK</h1>
<p>{safe(date)} · branch {safe(branch)}</p></div><div class="body">
{content}
<h2>Artwork evaluation</h2><p>{art_summary(art_eval)}</p>
<div class="{note_class}"><b>Editor note</b><br>{safe(editor_note).replace(chr(10), '<br>')}</div>
<h2>Sources</h2><ul>{''.join(source_items)}</ul>
{score_table}
<div class="foot">Generated {safe(dt.datetime.now(dt.timezone.utc).isoformat())} ·
commit {safe(commit)} · draft only, never sent.</div>
</div></div></body></html>"""


def build_payload(*, to: str, subject: str, html_body: str) -> dict:
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", to):
        raise ValueError("--to must be a plain email address")
    return {
        "to": to,
        "subject": subject,
        "payload": {
            "mime_type": "text/html",
            "charset": "UTF-8",
            "body": {"content": html_body},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post-md")
    parser.add_argument("--image-url", required=True)
    parser.add_argument("--dossier", required=True)
    parser.add_argument("--score")
    parser.add_argument("--art-eval", default="out/art_eval.json")
    parser.add_argument("--date", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--to", required=True)
    parser.add_argument("--editor-note", default="No unresolved issues.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    if not IMAGE_URL_RE.fullmatch(args.image_url):
        raise ValueError(
            "--image-url must be the commit-pinned The Texas Stack raw image URL"
        )
    dossier = json.loads(Path(args.dossier).read_text(encoding="utf-8"))
    score = (
        json.loads(Path(args.score).read_text(encoding="utf-8"))
        if args.score else {}
    )
    art_eval = json.loads(Path(args.art_eval).read_text(encoding="utf-8"))
    post = (
        Path(args.post_md).read_text(encoding="utf-8").strip()
        if args.post_md else ""
    )
    no_target = dossier.get("no_target_this_cycle") is True
    if not no_target and (not post or not args.score):
        raise ValueError("target email requires --post-md and --score")

    subject = (
        f"Texas AI Docket — The Texas Stack — No Target — {args.date}"
        if no_target
        else f"Texas AI Docket — The Texas Stack Draft — {args.date}"
    )
    body = render_html(
        post=post,
        image_url=args.image_url,
        dossier=dossier,
        score=score,
        art_eval=art_eval,
        date=args.date,
        branch=args.branch,
        commit=args.commit,
        editor_note=args.editor_note,
    )
    payload = build_payload(to=args.to, subject=subject, html_body=body)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"subject": subject, "html_chars": len(body)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

