# Art direction and evaluation

A cover should feel commissioned for this story. A generic gate, five floating slabs or glowing
network with new labels does not satisfy that goal. Use a gate only when its construction and
interaction express a distinctive sourced constraint. Never use decoration as proof of a mechanism.

## Three directions, one decision

Explore three different readings: a concrete material interaction; an editorial scene or still
life grounded in the record; and an unexpected scale/negative-space composition. These are prompts,
not mandatory styles. State each in one sentence, including what the viewer understands first.
Choose by fidelity, immediate legibility and distinction from recent covers. Select one strong
idea; do not merge three concepts into a busy illustration.

Tie each visible story-bearing element to a dossier fact or explicitly declared metaphor. Do not
pretend to show a real site, actual signed document, pipe network, actor or equipment layout without
source support. Distinguish a stalled approval from a failed machine and proposed capacity from
operating infrastructure. Abstract does not mean empty: show an intelligible interaction.

## Craft decisions

Specify a point of view, lighting direction, focal scale and material behavior. Choose a dominant
hue, contrasting value and one restrained accent; fixed brand furniture does not require darkening
the whole scene. Reserve quiet space using art_layout.json. One dominant object should read at
300 pixels; supporting details should reward full-size inspection. Texture must arise from the
medium: paper fibers, machined seams, ink pooling or worn surfaces, not a generic grain filter.

Use asymmetry and deliberate negative space when they clarify the relationship. Keep physical
joins and occlusion plausible. Avoid symmetrical flowcharts as the default. A sophisticated image
can be sparse, but each remaining element must carry a specific role. Do not add miniature junk
to inflate the detail score.

## Scoring anchors

Scores apply to the composed cover, after full-base and full-cover inspection. For every dimension,
write one observed strength and, below 9, the visible limitation. The score is editorial judgment,
not a measured multiplier or scientific benchmark.

| Dimension | Weight | A score near 9 requires |
|---|---:|---|
| concept | .18 | This mechanism's distinctive decision reads immediately; swapping the headline would break the fit. |
| focal_hierarchy | .13 | One unmistakable focal point; the next eye movement explains the dependency. |
| composition | .13 | Deliberate scale and negative space, no important cropping, balanced type and image. |
| color_value | .13 | Clear value separation at thumbnail; controlled palette without crushed image detail. |
| detail_richness | .12 | Coherent large form, meaningful assembly detail and convincing material close up. |
| craft_finish | .10 | Clean silhouettes, believable joins/light, no synthetic glitches or accidental voids. |
| typography | .09 | Correct furniture and comfortable spacing; headline readable at 300 pixels with no object interference. |
| originality | .08 | Distinct idea and treatment relative to recent issues; more than a palette/medium swap. |
| story_fidelity | .04 | Every implied relationship is supported or clearly metaphorical, with no invented fact. |

7 means serviceable but visibly weak; 8 means good with a named unresolved defect; 9 means strong
and publication-ready; 10 is exceptional and rare. Do not assign all dimensions the same number
or award points for intentions in the prompt. A crisp but generic diagram can score well on craft
and still fail concept/originality. Known visual blockers override the weighted result.

## Recovery choice

- Wrong mechanism or generic idea: replace the concept, keep the verified evidence boundary.
- Good idea, poor framing: targeted ImageGen edit with exact quiet-zone bounds.
- Correct art, awkward line break: adjust headline and compositor before spending on ImageGen.
- Broken surface, extra pseudo-text or malformed joint: edit that defect only.
- Good image at the floor with an obvious defect: repair; do not stop because metadata is green.

Use side-by-side review sheets to compare contenders at equal scale. Keep the stronger earlier
pass if a later edit regresses it. An unchanged render must not receive a better score without a
new, documented reason; never generate extra passes solely to satisfy an exception counter.
