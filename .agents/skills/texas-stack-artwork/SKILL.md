---
name: texas-stack-artwork
description: Create the original 1080 by 1080 cover for The Texas Stack after a mechanism dossier is final. Use built-in ImageGen for story-specific mechanism art, run the deduplicated visual evaluation loop, then apply exact Texas AI Docket typography. Do not use for research, post writing, logos, or other Texas AI Docket products.
---

# The Texas Stack Artwork

Create one original editorial image that makes the selected mechanism legible at a glance. This is
real generated artwork, not a procedural template. A deterministic fallback is a disclosed fire
exit only when the built-in image tool fails.

## Inputs

Read:

- out/stack_anatomy.json
- out/final_post.md when the run has a target
- config/brand.yaml
- .local/history.json
- references/visual-system.md

Do not add infrastructure, geography, insignia, documents, labels, actors, numbers, or physical
relationships that the dossier does not support.

## Plan before rendering

Write out/art_plan.md before any image call. Include:

1. three different concepts, each with a mechanism-specific metaphor and half-second read
2. the selected concept and why it is truer than the other two
3. emotional register
4. style family and proof that it clears the history cooldown
5. two to six colors with hex values and roles
6. a coordinate map for focal point, quiet top band, quiet lower headline band, and eye path
7. macro, meso, and micro detail
8. risks such as visual cliché, false geography, weak hierarchy, or type collision

The selected primary motif, style family, hue family, and composition may not appear in the
corresponding forbidden list in .local/history.json.

## Built-in ImageGen path

Write out/image_prompt.txt in this order:

- Use case: infographic-diagram or stylized-concept
- Asset type: square LinkedIn editorial cover background
- Primary request: the selected visual metaphor
- Scene/backdrop: the mechanism's verified Texas material world
- Subject: the layered machinery and the one chokepoint
- Style/medium: the selected editorial medium
- Composition/framing: one focal point, uncluttered top 18 percent, uncluttered lower 30 percent
- Lighting/mood: the chosen register
- Color palette: the planned two to six colors
- Materials/textures: medium-specific tactile detail
- Constraints: one-to-one square, no words, no letters, no numbers, no logos, no seals, no
  watermarks, no invented maps, no generated portrait or likeness
- Avoid: the exclusions in config/brand.yaml and references/visual-system.md

Invoke the built-in imagegen tool. Do not use a CLI, API key, or external image service. Copy the
selected result to out/art_base.png and retain discarded passes under ignored .local/ only.

Inspect each generated image at full size. Reject stray text, fake labels, logos, watermarks,
false Texas geography, cliché tech imagery, malformed objects, flat empty acreage, or weak focal
hierarchy.

## Self-healing evaluation

Score the composed cover from zero to ten:

- concept, weight 0.18
- focal_hierarchy, weight 0.13
- composition, weight 0.13
- color_value, weight 0.13
- detail_richness, weight 0.12
- craft_finish, weight 0.10
- typography, weight 0.09
- originality, weight 0.08
- story_fidelity, weight 0.04

The pass condition is a weighted score of at least 8.5 with no dimension below 7. The threshold is
the floor. A first pass should ship unchanged only when inspection genuinely supports it.

For a miss, name the weakest dimension and one targeted correction. Use an ImageGen edit when the
concept and composition should remain fixed. Regenerate when the metaphor or layout is the defect.
Repeat up to six ImageGen passes while visible improvement remains available. Each follow-up must
make one focused change and repeat the no-text and no-logo invariants.

Record exactly what was seen, not what the prompt requested, in out/art_eval.json. It contains:

- schema_version 1
- source, imagegen or fallback
- the three concepts
- selected_concept
- style_family, palette, hue_family, composition, and motifs
- eval_history with one entry per actual visual pass
- eval_final copied from the selected pass
- shortfall_note only when six real ImageGen passes still miss the floor
- fallback_reason only when fallback was required

## Exact publication furniture

After each candidate base is selected, create a provisional art_eval.json and run:

    python3 .agents/skills/texas-stack-artwork/scripts/compose_cover.py \
      --base out/art_base.png \
      --headline "<FOUR TO NINE WORD HEADLINE>" \
      --category "<CATEGORY OR WATCH>" \
      --date "<MONTH DTH, YYYY>" \
      --place "<VERIFIED TEXAS PLACE OR TEXAS>" \
      --prompt-file out/image_prompt.txt \
      --plan-file out/art_plan.md \
      --eval-file out/art_eval.json \
      --out out/post_image.png

Inspect the composed cover at full size and 300 pixels. Update art_eval.json with the observed
scores, then rerun the compositor so its metadata sidecar matches the final evaluation exactly.
Typography repairs use the compositor or a shorter accurate headline. Do not ask ImageGen to
render publication text.

Run:

    python3 .agents/skills/texas-stack-artwork/scripts/qa_check.py \
      --image out/post_image.png \
      --base out/art_base.png \
      --prompt out/image_prompt.txt \
      --plan out/art_plan.md \
      --eval out/art_eval.json \
      --date "<MONTH DTH, YYYY>" \
      --column "THE TEXAS STACK"

## No-target art

A no-target run still uses built-in ImageGen. The subject is the column's watch continuing while
the machinery is quiet, incomplete, or obscured. Use category WATCH and an honest short headline.
Do not imply a real event, actor, map, or document that the no-target dossier did not verify.

## Fallback

Fallback is allowed only when built-in ImageGen is unavailable or two consecutive calls fail to
return a usable image. Run:

    python3 .agents/skills/texas-stack-artwork/scripts/render_fallback.py \
      --headline "<HEADLINE>" \
      --category "<CATEGORY OR WATCH>" \
      --date "<DATE>" \
      --place "<PLACE>" \
      --prompt-file out/image_prompt.txt \
      --plan-file out/art_plan.md \
      --reason "<EXACT IMAGEGEN FAILURE>" \
      --out out/post_image.png

Disclose the failure in the editor note. A merely imperfect ImageGen render is not tool failure
and does not authorize fallback.
