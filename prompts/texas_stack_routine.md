# The Texas Stack weekly routine

Produce one sourced Texas AI mechanism anatomy and original cover, then a review branch,
draft PR and unsent Gmail draft. One mechanism, not a roundup or actor profile. Follow AGENTS.md.
Never send email, post to LinkedIn, merge, force-push, or push main. Maintenance work does not
invoke this routine's publication authorization.

## Context and spend discipline

Use the cloned repository root, not a workstation-specific path. Keep the saved scheduler prompt
as the pointer in prompts/ROUTINE_PROMPT.txt. Load only tools needed for the current phase;
discover an unavailable capability once, with at most one corrected query after a syntax error.
Do not load whole connector catalogs, unrelated documentation connectors or widget tools.

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
credentials, web, Gmail draft and Python/Pillow/NumPy rendering capability. No image API is needed.
Before discovery, fetch two representative configured primary hosts from different issuers and
record HTTP status, actual body byte count and timestamp privately. A coordinated proxy policy
denial is a missing network capability. Report needs_attention and repair that capability before
research; do not turn blocked infrastructure into a completed no-target result. Claude's Custom
network allowlist uses config/cloud_network_domains.txt plus the default package-host list.
Keep additional access limited to public issuer/source hosts required for this routine.
Fetch origin/main and remote codex/texas-stack-* branches. The default deployment revision is
origin/main; a saved routine may point to an exact validated review-branch commit while its PR
is unmerged. Record that revision in .local/run_state.json and use it as the issue branch base.
Start a unique codex/texas-stack-YYYY-MM-DD[-NN] from the deployment revision;
never overwrite a prior run. Create ignored .local and out. Run:

    python3 scripts/history_scan.py --fetch --date "$TODAY" --out .local/history.json

Read that ledger. Exclude the last six mechanisms unless a new trigger exposes a different chain
or chokepoint. The --fetch option refreshes every dated issue ref, including in a fresh cloud
clone; never accept a partial local branch list as the complete artwork history. Retrieve the
authenticated Gmail profile once; keep the address only in connector
arguments and .local/gmail_payload.json. Never log it, credentials, message contents or draft
identifiers. A draft listing proves mailbox access, not the authenticated account address.
If the connector has no profile endpoint, use only an independently verified connected-account
binding supplied privately by the environment; never infer identity from a draft recipient or
message sender. Without that binding, record gmail_recipient_unverified and do not write a draft.

For Claude's connector without a profile tool, TEXAS_STACK_GMAIL_BINDING supplies the privately
verified profile binding and an unsent mailbox challenge. Run scripts/gmail_binding.py --out
.local/gmail_binding.json without displaying the file or environment value. Read the exact
marker_subject draft with full HTML and labels once, preserve the connector result privately
as .local/gmail_binding_readback.json, then run scripts/gmail_binding.py --out
.local/gmail_binding.json --readback .local/gmail_binding_readback.json. Continue only when
mailbox_challenge_verified is true. The marker was issued through the authenticated profile
connector into that mailbox's draft store; it verifies the cross-connector binding without
using a sender or recipient field. A missing or changed marker fails closed. Keep these
fields and readbacks under ignored .local; never include them in a public run receipt.

Record capabilities before research: fetched web evidence, GitHub access, procedural rendering,
verified self-recipient, Gmail draft create/update and full HTML/label readback. If the active
request explicitly requires built-in ImageGen and the tool is absent, report that boundary.
The normal Claude routine uses code-generated artwork and never searches for ImageGen.
Missing infrastructure is not a no-target research result. A missing
profile or readback capability is a delivery limitation, never a passed gate. Report such a
limitation before expensive work; do not invent a replacement connector or request credentials.

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
before rendering, semantic cooldowns and actual raster variety checks, exact code-art brief and
render specification, measured typography, full-size and 300-pixel inspection, image-bound
evaluations and technical QA. Use the procedural primary path; built-in ImageGen is optional
only when explicitly requested. The 8.5 weighted floor and minimum dimension of 7 remain fixed.
If the cover headline cannot fit, shorten it within the skill's word limit while preserving
the verified meaning, then retry layout. This routine authorizes ordinary headline fitting;
do not ask for approval or count a layout-only failure as a rendering.
Use targeted repairs up to six actual renderings;
do not create extra passes just to exhaust a budget. Known visual blockers cannot pass on score.
Procedural artwork has no below-floor exception. Repair or report needs_attention if six attempts
cannot pass. A changed seed, palette label or grain layer cannot substitute for a new visual
treatment. Do not use the generic emergency fallback as production artwork.
Choose the visual idea before selecting a catalog row. The planner's random ordering is not a
quality ranking. An incomplete-evidence bridge or written-document barrier can use the eligible
editorial_scene family. If two pattern-based concepts fail, replace the visible interaction with
an unused coherent scene or extend an actual renderer. A third generic pattern is insufficient.
Do not stop after two failures while an eligible scene and repair budget remain. For a failed
render boundary, preserve the rejected base before rerendering; never run variety against a stale
base. Inspect the complete cover at full size and 300 pixels before recording its final scores.

## 5. Validate and publish artifacts

    python3 scripts/run_checks.py --out-dir out

This runs post, complete-run, unit, configuration, skill and artwork checks, retaining detailed
logs in .local/checks. Read failed logs only; never label a missing/skipped check passed. After an
edit, run its affected narrow check; run the complete command once on the final package. Do not
repeat its passing component checks unless an input or implementation changed.

Review diff, prose/privacy scan and status. Explicitly force-add only these ignored run artifacts:
stack_anatomy.json, art_plan.md, art_layout.json, image_prompt.txt, art_base.png, art_eval.json,
post_image.png and post_image.png.meta.json under out/. Procedural runs also include art_spec.json,
art_render.json and art_variety.json. Target runs also include final_post.md,
post_check.json and score_report.json. Keep rejected renders, review sheets and private receipts
in .local. If a story required an actual renderer extension, also commit only that renderer
source and its relevant test, after the complete package checks pass. This preserves the exact
renderer hash in the public reproduction chain. Do not alter quality thresholds or validators
to make an art repair pass. Commit with The Texas Stack and ISO date, push the dated branch with bounded retries,
and open a draft PR into main when gh is available. Add codex and codex-automation labels only
when available. Never merge. Unconfigured checks/labels are unavailable, not successful.

Resolve the exact commit and fetch:

    https://raw.githubusercontent.com/Talonsturgill/linkedin-texas-ai-stack/COMMIT/out/post_image.png

Require HTTP success, PNG content, 1080 square and exact committed byte identity; bounded CDN
retries only. This must succeed before the Gmail draft references the image.

## 6. Gmail draft and readback

Use scripts/build_email.py with --dossier, --art-eval, --image-url, --date, --branch, --commit,
--to, --editor-note, --out .local/gmail_payload.json; target runs also supply --post-md and --score.
Use --recipient-binding .local/gmail_binding.json instead of --to when the private mailbox
challenge supplied the verified recipient. The builder reads it without displaying the address.
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
procedural/ImageGen/legacy-fallback source, art score, verified URL, validation and draft state. Do not expose the
address or draft identifier. State that nothing was sent, posted or merged.

## Maintenance replay

When the user explicitly authorizes a fresh end-to-end test, execute every routine phase on a
new dated review branch and use build_email.py --test-mode. That draft has an [Automation Test]
subject prefix. Preserve existing production drafts. Keep all research, quality, immutable URL
and full HTML/DRAFT/no-SENT gates. This explicit test authorization is distinct from the
read-only replay below and does not authorize sends, posts, merges or main pushes.

A migration test is not a new weekly issue. Fetch the requested existing issue ref and use:

    python3 scripts/smoke_test.py --artifact-ref FULL_COMMIT_SHA --work-dir .local/smoke-UNIQUE --verify-image

Install requirements once in an ignored venv if needed. This extracts only the allowlisted issue
artifacts into a fresh ignored directory, runs all checks once and verifies immutable image bytes.
It does not switch branches, research a story, generate artwork, publish or contact Gmail.
Read its summary and failed logs only. Test connectors separately with a bounded, explicit scope.
Passing a replay does not prove fresh artwork generation or Gmail draft writes. Record those
untested boundaries. Context occupancy and remaining budget are not billable token counters;
report measured cost only when usage or billing evidence actually exposes it.
