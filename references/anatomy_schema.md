# Anatomy dossier contract

out/stack_anatomy.json is the factual boundary for a run. Published copy may simplify the
language, but it may not add facts, actors, layers, dates, numbers, quotations, or causal claims
that are absent from this file.

## Selected-mechanism shape

A target dossier has this shape:

    {
      "schema_version": 1,
      "run_date": "2026-09-02",
      "window_days": 14,
      "no_target_this_cycle": false,
      "selected_mechanism": {
        "name": "canonical mechanism name",
        "category": "facilities",
        "category_label": "FACILITIES",
        "definition": "one plain sentence",
        "texas_scope": "specific Texas place, jurisdiction, grid, institution, or market",
        "news_trigger": {
          "date": "2026-08-28",
          "verbatim_span": "exact visible source text",
          "post_anchor": "short exact phrase the post must contain",
          "source": {
            "url": "https://...",
            "title": "...",
            "publisher": "...",
            "source_type": "primary or independent_reporting",
            "published_at": "2026-08-28",
            "fetched_at_utc": "..."
          }
        },
        "layers": [
          {
            "order": 1,
            "name": "short layer name",
            "function": "what this layer does",
            "controlling_actor": "specific institutional actor",
            "actor_authority": "what gives the actor control",
            "post_phrase": "short exact actor phrase required in the matching bullet",
            "primary_source": {
              "url": "https://...",
              "title": "...",
              "publisher": "...",
              "source_type": "primary",
              "fetched_at_utc": "..."
            }
          }
        ],
        "chokepoint": {
          "layer_order": 3,
          "layer_name": "the selected layer name",
          "controlling_actor": "one actor or one office",
          "post_actor_phrase": "short exact actor phrase required in the post",
          "binary_decision": "the yes or no decision that changes the path",
          "post_decision_phrase": "short exact decision phrase required in the post",
          "why_asymmetric": "why this actor has unusual control",
          "primary_source_url": "https://..."
        },
        "texas_consequence": "specific sector, place, entity, and decision affected",
        "structural_read": "what the machinery produces and the evidence-led position",
        "forward_implication": "what becomes actionable or measurable next",
        "next_check": {
          "what": "specific filing, vote, study, award, meeting, or disclosure",
          "actor": "who controls it",
          "date_or_window": "verified date or honest window"
        },
        "public_policy_context": {
          "is_public_policy": true,
          "editorial_mode": "neutral_accountability",
          "assessment": "not_applicable"
        },
        "sources": [
          {
            "url": "https://...",
            "title": "...",
            "publisher": "...",
            "source_type": "primary",
            "independent_of_subject": true,
            "claims_supported": ["..."],
            "fetched_at_utc": "..."
          }
        ]
      },
      "required_post_phrases": [
        "mechanism name",
        "news trigger post anchor",
        "chokepoint actor phrase",
        "chokepoint decision phrase"
      ],
      "verified_facts": [
        {
          "claim": "one checkable fact",
          "source_urls": ["https://..."]
        }
      ],
      "gate_results": {
        "news_tie": true,
        "anatomizable_depth": true,
        "primary_source_each_layer": true,
        "texas_consequence": true,
        "chokepoint_asymmetry": true,
        "mechanism_not_actor": true,
        "not_recent_repeat": true,
        "political_neutrality": true
      },
      "dropped_mechanisms": []
    }

Allowed categories are facilities, vehicles, capital_sovereignty, and regulatory. A selected
mechanism needs three to five layers. Every layer needs a readable primary source from the current
run. The chokepoint must point to one of those layers and its source URL must match a recorded
source.

For public-policy mechanisms, public_policy_context must use neutral_accountability and
not_applicable. The structural read may assess whether authority is legible, deadlines are usable,
disclosures are adequate, implementation matches the record, or costs are measurable. It may not
tell readers which political outcome to prefer.

## No-target shape

A no-target dossier has no selected_mechanism and uses:

    {
      "schema_version": 1,
      "run_date": "2026-09-02",
      "window_days": 21,
      "no_target_this_cycle": true,
      "_validation_note": "why no mechanism cleared the gate",
      "selected_mechanism": null,
      "required_post_phrases": [],
      "verified_facts": [],
      "gate_results": {},
      "dropped_mechanisms": [
        {
          "name": "candidate mechanism",
          "category": "vehicles",
          "news_trigger": "what surfaced it",
          "drop_reason": "the exact failed gate",
          "sources": [
            {"url": "https://...", "title": "...", "publisher": "..."}
          ]
        }
      ]
    }

The dropped list must be nonempty and specific enough for the editor to see that discovery ran.
No-target still requires an original cover, a pushed branch, and a Gmail draft.

