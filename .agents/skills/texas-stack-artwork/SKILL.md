---
name: texas-stack-artwork
description: Create and visually verify original ImageGen covers for the final Texas Stack dossier, with measured typography and image-bound evaluation. Not for research, post writing or other publications.
---

# Texas Stack artwork

Read the final dossier, post if present, brand and current history once. Read
[art direction](references/art-direction.md) for concept selection and score anchors. Use
[visual system](references/visual-system.md) only when choosing a medium or palette.
Commands below are relative to the repository; helper scripts live in this skill's scripts/.

## Blueprint before pixels

Develop three genuinely different concepts, not three colors of one object. Record their
half-second read and supporting dossier fact. Pick the concept that makes this specific decision
legible without a caption. Reject attractive generic technology and invented infrastructure.
Write out/art_plan.md with selection rationale, register, medium, two to six hex colors/roles,
focal point, eye path, detail at three scales and visual risks. Explicitly check style, hue,
composition and primary motif against .local/history.json. Do not rename a repeated look.
None may appear in its corresponding forbidden list.

Choose the exact four-to-nine-word headline before generating. Measure its real typography:

    python3 .agents/skills/texas-stack-artwork/scripts/prepare_art.py --headline "EXACT SHORT HEADLINE HERE" --out out/art_layout.json

Use that file's subject_zone in the ImageGen brief. It reserves actual glyph space, not an
approximate lower band. Write the exact no-text brief to out/image_prompt.txt: use case,
metaphor and evidence limits, medium/materials, composition and subject bounds, light, palette,
macro/meso/micro detail, then exclusions. Usually 180–300 words is enough. Full opaque square;
no text, numbers, seals, logos, portraits, invented maps or technical relationships.

## Generate, compose, inspect

Use the built-in ImageGen tool only. Copy its raster to out/art_base.png. Save rejected passes
in .local. Inspect the full base for story fidelity and actual object bounds. Convert those
bounds to 1080-canvas coordinates and pass the observed subject box below; do not copy planned
coordinates as if they were measured. Include every story-bearing object, not its shadows.
Create provisional out/art_eval.json with schema_version 1, source imagegen, three concepts,
selected_concept, style_family, palette, hue_family, composition, motifs, empty eval_history and
provisional eval_final. Do not fabricate scores before inspection.

    python3 .agents/skills/texas-stack-artwork/scripts/compose_cover.py --base out/art_base.png --headline "EXACT SHORT HEADLINE HERE" --category REGULATORY --date "September 25th, 2026" --place TEXAS --layout out/art_layout.json --subject-box LEFT TOP RIGHT BOTTOM --prompt-file out/image_prompt.txt --plan-file out/art_plan.md --eval-file out/art_eval.json --out out/post_image.png

Use actual category/date/place. The compositor rejects transparency, silent cropping and subject
collision. It balances headline lines and darkens only the type regions. Repair text with a
shorter accurate headline and re-plan before asking ImageGen to repair art. Never render type
inside ImageGen. Exact publication furniture remains TEXAS AI DOCKET, THE TEXAS STACK, category,
Chicago date, headline and TEXASAIDOCKET.COM, on a 1080-square PNG.

    python3 .agents/skills/texas-stack-artwork/scripts/review_art.py --base out/art_base.png --cover out/post_image.png --sheet .local/art-review.png

Inspect the sheet for thumbnail comparison and each original at full size. Inspect once per
changed image; do not emit the same full-size image repeatedly. Score what is visible using the
reference anchors. Write .local/art-review.json with all nine scores and dimension-specific notes,
inspected_scales ["full","300"], observations, blockers (empty only if none), and the exact
edit_prompt for a follow-up pass. Record the actual generation:

    python3 .agents/skills/texas-stack-artwork/scripts/review_art.py --base out/art_base.png --cover out/post_image.png --eval out/art_eval.json --review .local/art-review.json --select

Omit --select for rejected passes. The helper computes the score and binds the review to image
hashes; it does not judge art. Recompose with identical arguments afterward to refresh metadata;
pixels must remain identical. Re-run QA through scripts/run_checks.py. A changed image needs a
new inspection; a metadata refresh does not. For a typography-only revision, use --replace-pass N after inspecting it; this preserves the
previous review without counting a fictitious ImageGen pass. To restore an earlier candidate,
restore its base and cover, inspect again, then use --replace-pass N --select.

## Repair and stop

8.5 weighted and every dimension at least 7 are floors, not quality targets. Seek 9+ with specific
visual evidence, never score inflation. At most six real ImageGen passes. Select the best observed
pass, not automatically the last. Name one weakest defect per edit; preserve working composition,
materials and source invariants. Regenerate only for a failed concept. Stop when there are no
concrete high-value defects left. Stray labels, false geography, illegible type, subject collision
or a broken mechanism depiction are blockers even above the floor. Preserve all actual scores.
Only a six-pass aesthetic miss without those blockers may use the routine's disclosed-shortfall
exception. No fallback to cosmetically pass a failed image.

No-target still receives original art about incomplete evidence, category WATCH, and an honest
headline. Do not depict a fictional project. The only fallback conditions are unavailable built-in
ImageGen or two consecutive unusable tool calls. Then use scripts/render_fallback.py --help,
record the failure and disclose it in the editor note. Never call an external image API or ask
for credentials.
