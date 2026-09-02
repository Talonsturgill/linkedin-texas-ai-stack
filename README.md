# The Texas Stack

The Texas Stack is Texas AI Docket's weekly mechanism-anatomy column for LinkedIn. One issue
starts with a current Texas AI news trigger, maps the machinery underneath it layer by layer,
identifies the actor and binary decision at the real chokepoint, and ends with a concrete next
check.

The routine produces a review package rather than publishing:

- source-grounded LinkedIn copy, or an honest no-target report
- original 1080 by 1080 editorial artwork created with built-in ImageGen
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

Every selected mechanism must clear the seven-point accuracy gate documented in the routine.
Quiet weeks ship as no-target drafts rather than forcing a weak anatomy.

## Local checks

    python3 -m pip install -r requirements.txt
    python3 -m unittest discover -s tests -v
    python3 scripts/check_config.py

Run artifacts are ignored on main and committed explicitly on dated branches.

