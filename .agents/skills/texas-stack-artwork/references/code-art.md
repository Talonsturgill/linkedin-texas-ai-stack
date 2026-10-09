# Code-art production

Commands are relative to the repository. Install requirements once in the existing ignored venv.
The engine uses supersampled Pillow drawing, layered shadows and seeded NumPy texture, then
Lanczos reduction. This keeps rendering portable in Claude Linux without an external image API.
The implementation follows [Pillow drawing](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html)
and [image resampling](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize).
The design separates deterministic geometry from surface variation; a seed identifies a render,
and changing it alone is insufficient evidence of variety.

    python3 .agents/skills/texas-stack-artwork/scripts/procedural_art.py plan --dossier out/stack_anatomy.json --history .local/history.json --out .local/art-concepts.json
    python3 .agents/skills/texas-stack-artwork/scripts/prepare_art.py --headline "EXACT SHORT HEADLINE HERE" --out out/art_layout.json

Choose one concept and copy that complete object to out/art_spec.json. Write the blueprint and
precise brief before pixels. The plan records render_family, style_family, hue_family, palette,
composition, motifs, seed, dossier_sha256 and story_binding. Bindings carry the actual layer names,
functions, controllers, primary URLs, gate order and binary decision. Preserve those exact facts.
No-target uses the explicit incomplete-evidence binding instead. Choose a medium and motif that
fit the meaning of the decision; a mathematically novel but irrelevant scene cannot pass.
Read the actual chokepoint before reviewing a cover. A verified written-approval decision uses
story_treatment written_authorization: a blank folded sheet physically intersects the selected
gate. Its abstract ink rules imply writing without fabricating a signature, wording or seal.
Other decisions must not acquire that paper cue just because a headline sounds like permission.

    python3 .agents/skills/texas-stack-artwork/scripts/procedural_art.py render --spec out/art_spec.json --layout out/art_layout.json --dossier out/stack_anatomy.json --out out/art_base.png --receipt out/art_render.json
    python3 .agents/skills/texas-stack-artwork/scripts/variety_check.py --spec out/art_spec.json --history .local/history.json --image out/art_base.png --out out/art_variety.json

Use scripts/history_scan.py --fetch during preflight to refresh all dated issue refs. The history
scanner fingerprints the actual last eight committed bases, including old ImageGen
issues. It records the public comparison snapshot in art_variety.json. Structure distance must
be at least 0.18 against each; color distance against the immediate predecessor must be at least
0.22. These are operational rejection thresholds, not a human-perception guarantee. Visual
inspection can reject a cover even after this check passes. QA independently reproduces the
distances and cooldown decisions from the committed comparison snapshot.

Prepare provisional art_eval.json with source procedural, exactly three concepts, selected_concept,
all selected spec style fields including render_family and seed, empty eval_history and eval_final,
and renderer_sha256 from art_render.json, spec_sha256 and variety_sha256. Do not invent scores.
Use subject_box from the renderer receipt; these bounds come from the actual drawing mask.

    python3 .agents/skills/texas-stack-artwork/scripts/compose_cover.py --base out/art_base.png --headline "EXACT SHORT HEADLINE HERE" --category REGULATORY --date "October 9th, 2026" --place TEXAS --layout out/art_layout.json --subject-box LEFT TOP RIGHT BOTTOM --prompt-file out/image_prompt.txt --plan-file out/art_plan.md --eval-file out/art_eval.json --out out/post_image.png
    python3 .agents/skills/texas-stack-artwork/scripts/review_art.py --base out/art_base.png --cover out/post_image.png --sheet .local/art-review.png

Inspect both originals and the 300-pixel sheet. Write the observed review described in SKILL.md.

    python3 .agents/skills/texas-stack-artwork/scripts/review_art.py --base out/art_base.png --cover out/post_image.png --eval out/art_eval.json --review .local/art-review.json --select

Recompose with the same arguments to refresh the evaluation hash in metadata. For a failed
concept or insufficient variety, select another unused family/motif/composition, update the
blueprint and spec, rerender, recheck variety and inspect the new pixels. For a code defect,
fix the renderer and preserve the old render's hash and review. At most six real attempts.
Changing typography uses --replace-pass on the same base. No automatic score inflation.

For a read-only migration or renderer test, scripts/artwork_smoke.py renders three candidates
in a fresh ignored directory and creates review sheets. It deliberately does not score or
publish them. Production normally renders one chosen concept first to avoid redundant work.
Use --selected-candidate 1, 2 or 3 to test that same production behavior in a fresh context.
