# The Texas Stack weekly routine

Produce one sourced Texas AI mechanism anatomy and original cover, then a review branch,
draft PR and unsent Gmail draft. One mechanism, not a roundup or actor profile. Follow AGENTS.md.
Never send email, post to LinkedIn, merge, force-push, or push main. Maintenance work does not
invoke this routine's publication authorization.

## Context and spend discipline

Read each contract once per run, when needed. Research: config/state.yaml, config/sources.yaml
and references/anatomy_schema.md. Writing: config/brand.yaml, config/rubric.yaml and
examples/voice_anchor.md. Artwork: .agents/skills/texas-stack-artwork/SKILL.md only after the
factual dossier is final. Reuse already-loaded content. Do not dump scripts, complete HTML,
connector responses, binary data or historical issues into context.

Default to one researcher. Batch discovery queries across four lanes; do not launch four
full-context scouts. If explicitly delegated, assign nonoverlapping candidates with a compact
brief and source references, and return at most 300 words per scout. Never research the same
candidate concurrently. Archive fetched source bodies under ignored .local/sources; report URL,
issuer, date, relevant section and the short evidence span needed for the decision. Read further
context whenever qualifications or interpretation are unclear. Summaries are indexes, not evidence.

Keep .local/run_state.json with run date, branch, phase, selected mechanism, artifact hashes and
unresolved failures, without private account fields. Resume unchanged work after interruptions;
revalidate changed artifacts and current external delivery state. Do not reuse prior-run source
fetches as current evidence. Record actual usage when the environment exposes it; do not invent
savings from instruction length. Stop extra discovery once every lane has been checked and the
strongest fully verified candidate is selected.

## 0. Preflight

Use America/Chicago dates. Check clean repository, origin, GitHub authentication without printing
credentials, web, Gmail draft and built-in ImageGen capability. Fetch origin/main and remote
codex/texas-stack-* branches. Start a unique codex/texas-stack-YYYY-MM-DD[-NN] from origin/main;
never overwrite a prior run. Create ignored .local and out. Run:

    python3 scripts/history_scan.py --date "$TODAY" --out .local/history.json

Read that ledger. Exclude the last six mechanisms unless a new trigger exposes a different chain
or chokepoint. Retrieve the Gmail profile once; keep the address only in the connector arguments
and .local/gmail_payload.json. Never log it, credentials, message contents or draft identifiers.

If web/GitHub fails, preserve local evidence and make a candid needs-attention draft when Gmail
is available. If Gmail alone fails, finish the branch and report that boundary. Never claim an
unverified external action succeeded.

## 1. Discovery funnel

Search the fourteen-day trigger window in every lane:

- facilities: power, cooling, water, fiber, campuses, chips and robotics facilities.
- vehicles: contracts, procurement, grants, incentives and loan programs.
- capital_sovereignty: financing, ownership, utility/co-op capital and control rights.
- regulatory: permits, interconnection, data rules and implementation decisions.

Use current agency, utility, county and procurement calendars as search leads, not facts.
Search snippets only discover leads. Fetch each promising trigger before spending on layer research.
Deduplicate by mechanism and decision. Drop stale, repeated, actor-only or non-Texas leads early;
do not fetch a full layer chain for an already disqualified lead. Maintain short disposition rows
with attempted sources and exact failed gate. Qualified alternatives are not failed candidates.

Compare the best candidates on primary-source completeness, specific Texas consequence and one
controller's binary decision. Deepen the strongest first, then the next if it fails. Before calling
a finalist qualified, fetch primary evidence for every claimed layer. Capture its definition,
trigger date and verbatim span, three to five connected layers, functions/controllers/authority,
source URLs, chokepoint, consequence, history comparison and neutrality screen. Never fill a
missing link by inference. Scope and exceptions belong beside the claim, not in an omitted appendix.

## 2. Accuracy gate and dossier

Re-fetch each unique selected primary URL once for final verification; a document supporting
several layers needs one fetch, with separate evidence pointers per layer. Inspect the controlling
text, not just an abstract or title. Keep fetch timestamp, URL and source-body hash in the dossier;
retain full bodies locally. Seek independent trigger corroboration and disclose its absence.

Write out/stack_anatomy.json to references/anatomy_schema.md. Set all eight gates separately:
news_tie, anatomizable_depth, primary_source_each_layer, texas_consequence, chokepoint_asymmetry,
mechanism_not_actor, not_recent_repeat, political_neutrality. One named institution/office must
control an explicit yes/no decision. Record evidence gaps and distinguish announced, proposed,
required and completed actions. Every published fact and numeral must trace to the dossier.

Political neutrality is a hard gate: no candidate, party, campaign or ballot advocacy and no
preferred political outcome. Assess authority, procedure, implementation, disclosure and measurable
effects. Explain competing sourced effects without scoring the policy or actor.

If no candidate qualifies, broaden once to twenty-one days and repeat the gate. If none survives,
write the honest no-target shape with nonempty dropped_mechanisms, sources and reasons. Continue
to original art and Gmail; omit post and editorial score files. Never lower a gate.

## 3. Post and editorial review

From the final dossier, write out/final_post.md in this order: two-line mechanism/trigger hook;
one-sentence definition; one block of three to five layer bullets; exact chokepoint; structural
read; concrete next check; debatable chokepoint question; exactly three approved hashtags.

Apply config/brand.yaml: 350–475 body words, at most 3,000 total characters, first two nonempty
lines at most 210 characters with exact mechanism name and trigger anchor. Each bullet includes
its layer name and post_phrase. Include all required_post_phrases. Straight quotes only; no
links, first person, banned prose, emoji, em/en dash, double hyphen, colon or semicolon.

    python3 scripts/check_post.py --post out/final_post.md --dossier out/stack_anatomy.json --report out/post_check.json

Repair failures. Write out/score_report.json with every exact configured criterion, weight,
observed score and evidence note, every hard-fail result, correct weighted total and ship flag.
The floor remains 8.0 with all hard gates passed. At most three editorial passes and two
score-driven revisions; rerun the post check after edits. If factual support fails, use no-target.

## 4. Art

Follow .agents/skills/texas-stack-artwork/SKILL.md. Required: three distinct concepts, blueprint
before rendering, cooldown checks, exact prompt, actual built-in ImageGen, measured typography,
full-size and 300-pixel inspection, image-bound evaluations and technical QA. The 8.5 weighted
floor and minimum dimension of 7 remain fixed. Use targeted repairs up to six actual generations;
do not create extra passes just to exhaust a budget. Known visual blockers cannot pass on score.
The existing six-pass aesthetic-shortfall exception requires explicit disclosure and never excuses
invented evidence, stray labels or unreadable typography. Fallback is only for tool unavailability
or two consecutive unusable tool results, not aesthetic disappointment.

## 5. Validate and publish artifacts

    python3 scripts/run_checks.py --out-dir out

This runs post, complete-run, unit, configuration, skill and artwork checks, retaining detailed
logs in .local/checks. Read failed logs only; never label a missing/skipped check passed. After an
edit, run its affected narrow check; run the complete command once on the final package.

Review diff, prose/privacy scan and status. Explicitly force-add only these ignored run artifacts:
stack_anatomy.json, art_plan.md, art_layout.json, image_prompt.txt, art_base.png, art_eval.json,
post_image.png and post_image.png.meta.json under out/. Target runs also include final_post.md,
post_check.json and score_report.json. Keep rejected renders, review sheets and private receipts
in .local. Commit with The Texas Stack and ISO date, push the dated branch with bounded retries,
and open a draft PR into main when gh is available. Add codex and codex-automation labels only
when available. Never merge. Unconfigured checks/labels are unavailable, not successful.

Resolve the exact commit and fetch:

    https://raw.githubusercontent.com/Talonsturgill/linkedin-texas-ai-stack/COMMIT/out/post_image.png

Require HTTP success, PNG content, 1080 square and exact committed byte identity; bounded CDN
retries only. This must succeed before the Gmail draft references the image.

## 6. Gmail draft and readback

Use scripts/build_email.py with --dossier, --art-eval, --image-url, --date, --branch, --commit,
--to, --editor-note, --out .local/gmail_payload.json; target runs also supply --post-md and --score.
Use the connected profile address in memory, never a placeholder or printed shell argument.
The builder owns section order: header, post/no-target, image and visible URL, sources, editorial
score if present, artwork score, editor note, branch/commit footer. Note every evidence gap,
recovery, broadened window, missing lane, fallback or aesthetic shortfall concisely.

List drafts, then exact-subject search for this date rather than dumping the whole mailbox.
Update the newest exact match or create if absent; report duplicate count without deleting any.
Never call send. Read back subject, connected recipient privately, full HTML/post, inline image,
visible clickable immutable URL, all sources, scores, note, branch/commit, DRAFT and absence of
SENT. Inspect the rendered email if markup/layout changed or loading is uncertain. Store private
receipts under .local. Report mechanism/no-target, category, branch, exact commit, draft PR,
ImageGen/fallback source, art score, verified URL, validation and draft state. Do not expose the
address or draft identifier. State that nothing was sent, posted or merged.
