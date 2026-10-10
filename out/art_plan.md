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

Six pipeline renders were recorded in eval_history (scores 7.415, 7.51, 8.085, 8.435, 8.495, 8.545). Before render 1 and before render 3, the new renderers were built with quick debug previews of the layer alone, without typography or a review. Those previews are development of the renderer code, were not scored, and are disclosed here rather than counted. Render 6 passes the floor with the soft crop smear and a faint lintel shadow line noted as limits. The points_switch renderer for the rejected concept remains in the engine source with its test.
