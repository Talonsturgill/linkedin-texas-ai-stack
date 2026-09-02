# The Texas Stack automation

This repository owns one product, the weekly The Texas Stack LinkedIn draft for Texas AI
Docket. Each run anatomizes one current Texas AI mechanism, creates an original square cover,
pushes a review branch, and leaves a complete unsent Gmail draft. It never posts to LinkedIn and
never sends mail.

## Start here

1. Read prompts/ROUTINE_PROMPT.txt and prompts/texas_stack_routine.md in full.
2. Read config/brand.yaml, config/sources.yaml, config/state.yaml, config/rubric.yaml, and
   references/anatomy_schema.md.
3. Read examples/voice_anchor.md for voice only.
4. Use the texas-stack-artwork skill after the mechanism dossier is final.

The versioned routine is authoritative. Keep the scheduler prompt thin.

## Boundaries

- Draft only. Gmail draft creation and updates are allowed. Sending is never allowed.
- Never post to LinkedIn, merge a pull request, force-push, or push directly to main.
- Use a unique codex/texas-stack-YYYY-MM-DD[-NN] branch for every run.
- Do not modify sibling TexasAIDocket, TexasAIDispatch, TexasAIScanner, or Texas Desk repos.
  They may be read for public brand and record context only.
- Never store credentials, mailbox addresses, private messages, connector responses, or Gmail
  draft identifiers in Git. Delivery payloads and receipts belong under ignored .local/.
- Every factual claim must trace to a fetched page recorded in out/stack_anatomy.json.
- Every layer requires a primary source. A search result snippet is discovery, not evidence.
- Every numeral in published copy must already appear in the verified dossier.
- Do not rank or advocate for candidates, parties, campaigns, ballot measures, or preferred
  political outcomes. Public policy may be covered only as neutral, sourced accountability
  reporting about authority, procedure, implementation, disclosure, and measurable effects.
- A no-target week is honest output. It still gets original artwork, a pushed branch, and a Gmail
  draft explaining what was checked.
- Actual built-in ImageGen is the primary art path. A deterministic fallback is a disclosed fire
  exit for tool failure, not an aesthetic shortcut.

## Verification

Use Python 3.11 or newer.

    python3 -m pip install -r requirements.txt
    python3 -m unittest discover -s tests -v
    python3 scripts/check_config.py
    python3 /Users/t/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
      .agents/skills/texas-stack-artwork

For a completed target run, also execute:

    python3 scripts/check_post.py --post out/final_post.md \
      --dossier out/stack_anatomy.json --report out/post_check.json
    python3 scripts/validate_run.py --out-dir out

Never describe a skipped check as passed. Inspect both art_base.png and post_image.png at full
size and thumbnail size. The 8.5 artwork score is a floor, not a substitute for visual judgment.

