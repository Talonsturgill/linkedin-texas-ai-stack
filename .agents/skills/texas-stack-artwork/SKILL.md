---
name: texas-stack-artwork
description: Draw and visually verify original Texas Stack covers in code, with story-bound geometry, measured typography and history-aware variety. Use after the mechanism dossier is final.
---

# Texas Stack artwork

Use procedural code art as the primary path. Python, Pillow and NumPy are sufficient; no image
API or ImageGen lookup is needed. Read the final dossier, post if present, brand and current
history once. Read [code art](references/code-art.md) for production commands and the specification.
Read [art direction](references/art-direction.md) once before scoring; its anchors are required.
Judge composition on the finished cover. The text-free base intentionally reserves quiet space
for measured headline/footer furniture; do not penalize that required space as a missing scene.
ImageGen is optional only
when explicitly requested; then read [ImageGen mode](references/imagegen-mode.md).

## Blueprint and variety

Propose three concepts using procedural_art.py plan. They must use different drawing families,
compositions and primary motifs. Choose the concept that explains this specific controller's
binary decision without inventing an engineering design. Write out/art_plan.md before rendering:
selection rationale, literal dossier bindings, metaphor limits, medium, palette roles, focal point,
eye path, detail at three scales and visual risks. Record the three concepts in art_eval.json.

The engine supplies drawing methods; it does not choose the story's visual idea. A catalog
pattern with a document pasted onto it is insufficient when the decision needs a different
physical interaction. Use the blueprint to design that interaction, extending actual geometry
or adding a genuinely distinct renderer when the toolkit cannot express it.

The engine has fourteen different drawing methods with different geometry. Exclude
styles used in the last eight covers, hue families in four, compositions in two and primary
motifs in ten. Do not rename a used style. The immediately preceding cover must differ on all
four axes. Run variety_check.py against actual recent raster fingerprints. It rejects similar
low-frequency structure and insufficient color change; grain or a new seed cannot clear it.
A failed variety check requires a different treatment, not a lower threshold. If the catalog is
exhausted or poorly suited to a story, extend a genuinely different renderer and test it.

Choose an exact four-to-nine-word headline. prepare_art.py reserves actual glyph space. If it
cannot fit, shorten the cover headline while preserving the verified meaning and rerun layout.
Routine headline fitting is authorized editorial work; do not pause for approval. A layout-only
failure is not a render attempt. Save
the selected art_spec.json with its exact dossier hash and story_binding, and the precise brief
in image_prompt.txt. Keep the base opaque and text-free; the compositor supplies all publication
furniture. Never add invented maps, identities, labels, seals or technical relationships.

## Render, inspect and repair

Render only the chosen concept initially. The renderer measures subject bounds from its actual
alpha mask and records seed, specification hash, renderer hash and base hash in art_render.json.
Run the variety gate, compose using those measured bounds, then inspect both originals at full
size and on the 300-pixel review sheet. Do not assign aesthetic scores before seeing the pixels.

Record all nine observed scores with dimension-specific notes, inspected_scales ["full","300"],
observations, blockers and one concrete edit in .local/art-review.json. review_art.py binds the
review to the actual base and cover bytes. Use --select only with no blockers and a real passing
review. Recompose identically afterward to refresh metadata. A metadata refresh is not a new
render or review. Use --replace-pass for a typography-only re-review of the same base.

The 8.5 weighted floor and minimum dimension of seven are hard gates for procedural art. Seek
9+ through concrete corrections. Stray labels, false geography, illegible type, clipping, subject
collision or a misleading mechanism are blockers even above the floor. Never let code calculate
or pre-fill aesthetic scores. At most six actual rendering attempts, retaining every rejected
review. Select the strongest observed candidate. If none passes, report needs_attention with
honest evidence; do not ship a below-floor generic fallback.

A no-target cover represents incomplete evidence, uses category WATCH and an honest headline;
it does not depict a fictional project. Code-art is recorded as source procedural throughout
the evaluation, metadata and email. It is a normal supported path, not a failure disclosure.

## Handoff

Run scripts/run_checks.py once on the final package. Commit the routine's allowed public art
files, including art_spec.json, art_render.json and art_variety.json for procedural output.
When a story required a renderer extension, include the changed renderer source and its relevant
test in the issue commit so the recorded renderer hash can be reproduced from that exact SHA.
Keep quality thresholds and validation code unchanged during a production art repair.
Keep rejected images, review sheets and private receipts ignored. Preserve the immutable URL
and draft-only delivery contract. A successful rendering alone does not prove publication or
Gmail delivery.
