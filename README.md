# The Texas Stack

The Texas Stack is Texas AI Docket's weekly mechanism-anatomy column for LinkedIn. One issue
starts with a current Texas AI news trigger, maps the machinery underneath it layer by layer,
identifies the actor and binary decision at the real chokepoint, and ends with a concrete next
check.

The routine produces a review package rather than publishing:

- source-grounded LinkedIn copy, or an honest no-target report
- original 1080 by 1080 editorial artwork drawn in code with a history-aware variety engine
- an immutable commit-pinned image URL
- a pushed dated branch and optional draft pull request
- an unsent Gmail draft with copy, image, sources, score, and editor notes

The column runs weekly on Friday. The automation prompt points to the versioned routine in
prompts/texas_stack_routine.md so behavior changes remain reviewable in Git.

## Editorial unit

The unit is one mechanism, never a general market survey:

- facilities
- vehicles
- capital and sovereignty
- regulatory

Every selected mechanism must clear the eight-point accuracy gate documented in the routine.
Quiet weeks ship as no-target drafts rather than forcing a weak anatomy.

## Local checks

    python3 -m pip install -r requirements.txt
    python3 -m unittest discover -s tests -v
    python3 scripts/check_config.py
    python3 scripts/check_skill.py .agents/skills/texas-stack-artwork

Run artifacts are ignored on main and committed explicitly on dated branches.

For a bounded migration replay, fetch an existing issue commit, install the requirements and run:

    python3 scripts/smoke_test.py --artifact-ref FULL_COMMIT_SHA --work-dir .local/smoke-UNIQUE --verify-image

This tests the package and its immutable image without generating a new issue or writing Gmail.
Cloud routines need Python/Pillow/NumPy rendering, a verified connected-account recipient and
Gmail HTML/label readback. Missing capabilities must remain explicit; a green replay alone does
not prove the complete weekly workflow. The saved scheduler owns the execution time; the
repository uses America/Chicago for issue dates.

The code-art engine has thirteen distinct drawing families. It excludes the last eight styles,
four hue families, two compositions and ten primary motifs, then checks low-frequency image
structure and actual colors against recent covers. The immediately preceding cover must differ
on all four semantic axes. Originality still receives a full-size and 300-pixel visual review;
the same 8.5 score floor applies. See the artwork skill for the production commands.
