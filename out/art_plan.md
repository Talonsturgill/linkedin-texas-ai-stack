# Pre-production blueprint

Dossier binding. Mechanism PUCT rulemaking petition gate. Chokepoint layer 5, Commission order, the Public Utility Commission of Texas choosing to deny the petition in writing or initiate a rulemaking proceeding. The verified outcome is denial on October 1st, 2026. Layers 1 to 4 (statutory petition right, petition form rule, staff intake and comment window, staff recommendation) are the approach to the switch.

## Three concepts, one decision

1. Railway points study, family points_switch, composition long_approach, motif thrown points. A thick bound sheaf of pages stands on a track at a hand-thrown set of points. The blades are set for a short siding that ends in a buffer stop, while the through line runs on, empty and lit. The viewer understands first that one lever picks between two routes and that this sheaf was routed to the closed one.
2. Stained-glass facets, composition folded_fan, motif ribbon knot. A faceted pane splits into a closed and an open sector around a central gate. Reads as a split, not as a physical route, and the knot motif says nothing about a deadline.
3. Contour landscape, composition crossing_branches, motif wedge stop. Two contour channels cross at a wedge. Abstract and legible as a fork, but it carries no petition and no stopped path.

Selection. Concept 1 is the only one that shows the actual decision (two lawful routes, one lever, a document taken down one of them). Concepts 2 and 3 would work for any binary gate and fail the swap-the-headline test. A pre-existing catalog renderer could not draw this interaction, so the engine is extended with the points_switch renderer and its own test.

## Literal bindings and metaphor limits

- The sheaf stands for the petition. Its page edges are many unnumbered leaves, bound by one strap. No text, number, seal, signature or heading appears on it.
- The lever, blades and buffer stop stand for the written deny or initiate decision. The through line is the other lawful route; it is drawn empty because no rulemaking was opened. It is not shown as forbidden or as a failure of the Commission.
- This is a declared editorial metaphor. It is not a real rail yard, a map, a Texas place or a claim about equipment. No labels, no people, no state outline.

## Medium and palette

Flat-shaded oblique study with soft cast shadows, a feathered crop, no photographic claim. Palette moss_magenta. Moss ground, chalk rails and pages, mid green sleepers, magenta only on the strap, lever and buffer beam so the three controlling objects tie together by color. Red flag colour is not used.

## Focal point and eye path

Focal point. The strapped sheaf at left, largest and lightest mass. Eye path. Sheaf, then the pink blade and lever at the points, then the curved siding to the buffer beam, then the dim glow along the through line. Headline below.

## Detail at three scales

Macro. Sheaf, fork, buffer. Meso. Strap, blade and lever with rod, curving siding rails, sleeper rhythm. Micro. Page-edge hairlines, rail heads and spikes, cast shadows.

## Visual risks

Magenta on moss may read candy-like. Siding may read as decoration if the lever is lost at 300 pixels. The sheaf could dominate and hide the fork. Feather crop must not look like a floating panel. Repairs must change the visible relationship, not only the surface, and after two rejected renders of this concept the next render uses a different interaction.

## Concept change after two rejected renders

Renders 1 and 2 of concept 1 (railway points) scored 7.415 and 7.51 and were rejected with blockers, preserved under the ignored review ledger and in art_eval.json eval_history. The repair for render 2 fixed the glow rectangle and composition but the lever and buffer remained weak decision objects. Per the routine, render 3 replaces the visible interaction instead of polishing it.

Selected concept now: paired bay wall study, family bay_wall, composition low_threshold, motif closed bay, palette glacier_tangerine. A bound sheaf stands at a heavy slab that closes one bay of a wall, with a bar across the slab. The neighbouring bay is open onto an empty lit passage. The viewer understands first that the sheaf has met a closed door while the other route stays open and unused. This is a declared editorial metaphor of the deny route versus the initiate route, with no text, numerals, seals, people or place claims. The three recorded concepts are now railway points (rejected twice), paired bay wall (selected) and stained-glass facets (unused).

Palette roles. Teal wall and slab, chalk pages, tangerine only on the strap and the bar so the sheaf and the door tie together, a cool light in the open bay. Focal point the sheaf against the slab, eye path to the lit opening. Detail. Macro wall with two bays, meso slab panel, hinges, bolts and page edges, micro stone joints and cast shadows. Risks. Wall reads as a floating panel, sheaf hides the slab, lit bay reads as an exit sign rather than an unused route.

## Render accounting

Reviewed pipeline renders. Six, recorded in eval_history with scores 7.415, 7.51, 8.085, 8.435, 8.495 and 8.545. These are the only candidates that were composed, inspected at full size and 300 pixels and scored.

Development previews, reported separately. While building and repairing the two new renderers, 11 full story-scene layer previews were drawn with a debug harness that renders the scene layer only, with no headline, no review and no score. Railway points concept, 7 previews before render 1, 1 before render 2. Paired bay wall concept, 1 before render 3, 1 before render 4 and 1 before render 6, none before render 5. In addition, 2 pipeline render calls before render 1 raised the typography clearance error and saved no image. The previews are kept only in ignored local files, were not reviewed as candidates, and are not part of the six. The cost of the previews was not measured, so no total render or token cost is claimed.

An earlier version of this note said previews happened before renders 1 and 3 only. That was incomplete and is corrected here.

Limits of the selected render 6. Soft crop smear and a faint lintel shadow line. The points_switch renderer for the rejected concept remains in the engine source with its test.

## Metadata rebind after a copy correction

After final acceptance review, the post, texas_consequence, structural_read, forward_implication and next_check in the dossier were corrected, because the record does not show the internal metering proposal proceeding in another project. The dossier hash changed from e4e8df42e4c9fe912f43f7ef35fac7cf496f875a135bed47ed288f76f8fa3e32 to 5e254f4cd8cc521f8fab1c1ec4e7b7e4f3a41c51f79dbf6949daef779dc73232. The art spec, receipt, variety record and evaluation were rebound to it. The base image was re-rendered from the same spec and renderer and came out byte identical, base SHA-256 e0b779d99766011c73082b2852b1ddc4372ecf087d85760e1b1c2c7c2ce23c1c. That is a reproducibility check, not a seventh visual candidate. No art score changed.

## Second metadata rebind after a source provenance repair

A further acceptance audit found that the statute URL recorded for Government Code 2001.021 (https://statutes.capitol.texas.gov/Docs/GV/htm/GV.2001.htm) returns a 250874 byte Angular portal shell with no statute text, and that the earlier archived body was a headless browser rendering of that page rather than a raw fetched body. The dossier now cites the official statute document the portal itself loads, https://tcss.legis.texas.gov/resources/GV/htm/GV.2001.htm, fetched directly, with its hash, size and a provenance note. Its text of Section 2001.021(a) to (d), including "deny the petition in writing, stating its reasons for the denial" and "initiate a rulemaking proceeding", was read in full. No claim changed. The dossier hash is now e9efeec23d35ba458f6a8729c46177530e86b4c85e541c75d4565b0e672ddfb0. The art spec's layer 1 source URL was rebound to match. The base was re-rendered from the same spec and renderer and is byte identical (e0b779d99766011c73082b2852b1ddc4372ecf087d85760e1b1c2c7c2ce23c1c). It is not a new visual candidate, the six reviews and scores are unchanged, and the 11 development previews and 2 failed clearance calls reported above stand. The renderer and the v4 engine are unchanged.
