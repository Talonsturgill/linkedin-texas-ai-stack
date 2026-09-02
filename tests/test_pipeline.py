from __future__ import annotations

import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_email
import check_config
import check_post
import history_scan
import validate_run


def source(url: str, *, primary: bool = True) -> dict:
    return {
        "url": url,
        "title": "Readable source",
        "publisher": "Issuing office",
        "source_type": "primary" if primary else "independent_reporting",
        "published_at": "2026-08-28",
        "fetched_at_utc": "2026-09-02T12:00:00Z",
    }


def dossier(*, no_target: bool = False) -> dict:
    if no_target:
        return {
            "schema_version": 1,
            "run_date": "2026-09-02",
            "window_days": 21,
            "no_target_this_cycle": True,
            "_validation_note": "Every candidate lacked a complete primary source chain.",
            "selected_mechanism": None,
            "required_post_phrases": [],
            "verified_facts": [],
            "gate_results": {},
            "dropped_mechanisms": [
                {
                    "name": "Candidate queue",
                    "category": "vehicles",
                    "news_trigger": "A recent notice surfaced the queue.",
                    "drop_reason": "The controlling actor could not be verified.",
                    "sources": [source("https://example.com/attempt")],
                }
            ],
        }
    layers = [
        {
            "order": 1,
            "name": "Filing layer",
            "function": "moves the request into review",
            "controlling_actor": "Applicant office",
            "actor_authority": "the published filing rule",
            "post_phrase": "Applicant office",
            "primary_source": source("https://example.com/filing"),
        },
        {
            "order": 2,
            "name": "Grid review layer",
            "function": "tests whether the request can proceed",
            "controlling_actor": "Grid review office",
            "actor_authority": "the published capacity rule",
            "post_phrase": "Grid review office",
            "primary_source": source("https://example.com/grid"),
        },
        {
            "order": 3,
            "name": "Approval layer",
            "function": "issues the final authorization",
            "controlling_actor": "Approval office",
            "actor_authority": "the published approval rule",
            "post_phrase": "Approval office",
            "primary_source": source("https://example.com/approval"),
        },
    ]
    gates = {name: True for name in validate_run.REQUIRED_GATES}
    return {
        "schema_version": 1,
        "run_date": "2026-09-02",
        "window_days": 14,
        "no_target_this_cycle": False,
        "selected_mechanism": {
            "name": "Texas Queue Gate",
            "category": "regulatory",
            "category_label": "REGULATORY",
            "definition": "A staged review path that controls entry to a Texas system.",
            "texas_scope": "Central Texas",
            "news_trigger": {
                "date": "2026-08-28",
                "verbatim_span": "The office published its August notice.",
                "post_anchor": "published its August notice",
                "source": source("https://example.com/notice", primary=False),
            },
            "layers": layers,
            "chokepoint": {
                "layer_order": 2,
                "layer_name": "Grid review layer",
                "controlling_actor": "Grid review office",
                "post_actor_phrase": "Grid review office",
                "binary_decision": "Issue or withhold the capacity letter.",
                "post_decision_phrase": "issue or withhold the capacity letter",
                "why_asymmetric": "No later review starts without the letter.",
                "primary_source_url": "https://example.com/grid",
            },
            "texas_consequence": "The path changes when a Central Texas project may proceed.",
            "structural_read": "The rule makes a technical letter the effective entry gate.",
            "forward_implication": "The next published letter will show whether review advances.",
            "next_check": {
                "what": "the next capacity letter",
                "actor": "Grid review office",
                "date_or_window": "the next published review cycle",
            },
            "public_policy_context": {
                "is_public_policy": False,
                "editorial_mode": "structural_analysis",
                "assessment": "not_applicable",
            },
            "sources": [
                source("https://example.com/notice", primary=False),
                *[row["primary_source"] for row in layers],
            ],
            "verbatim_quotes": [],
        },
        "required_post_phrases": [
            "Texas Queue Gate",
            "published its August notice",
            "Grid review office",
            "issue or withhold the capacity letter",
        ],
        "verified_facts": [
            {
                "claim": "The path has three sourced layers.",
                "source_urls": [
                    "https://example.com/filing",
                    "https://example.com/grid",
                    "https://example.com/approval",
                ],
            }
        ],
        "gate_results": gates,
        "dropped_mechanisms": [],
    }


def valid_post() -> str:
    lines = [
        "Texas Queue Gate surfaced when the office published its August notice.",
        "The mechanism controls when a Central Texas request enters formal review.",
        "",
        "The Texas Queue Gate is a staged review path that ties one request to three connected decisions.",
        "",
        "- Filing layer moves the request into review, Applicant office.",
        "- Grid review layer tests whether the request can proceed, Grid review office.",
        "- Approval layer issues the final authorization, Approval office.",
        "",
        "The chokepoint sits with the Grid review office. It can issue or withhold the capacity letter. No later review begins without that record.",
        "",
    ]
    filler = (
        "The record connects authority to a visible decision and keeps the consequence tied "
        "to the mechanism. The structure matters because timing, evidence, and operating "
        "responsibility remain attached to named offices. A reader can see which action "
        "changes the path and which later steps depend on it."
    )
    while len(check_post.WORD_RE.findall("\n".join(lines))) < 360:
        lines.extend([filler, ""])
    lines.append(
        "Should the Grid review office publish the capacity letter and its reasoning before the next approval step?"
    )
    lines.extend(["", "#TexasAI #TexasGrid #TexasPolicy"])
    return "\n".join(lines)


def art_eval() -> dict:
    scores = {
        "concept": 9.0,
        "focal_hierarchy": 8.5,
        "composition": 8.5,
        "color_value": 8.5,
        "detail_richness": 8.5,
        "craft_finish": 8.5,
        "typography": 9.0,
        "originality": 8.5,
        "story_fidelity": 9.0,
    }
    weighted = round(validate_run.expected_weighted(scores), 3)
    return {
        "schema_version": 1,
        "source": "imagegen",
        "concepts": [{}, {}, {}],
        "selected_concept": "open coupling",
        "style_family": "layered paper relief",
        "palette": ["#08060F", "#EDE6D6", "#E0956A"],
        "hue_family": "indigo-warm",
        "composition": "offset_chokepoint",
        "motifs": ["open coupling"],
        "eval_history": [{"pass": 1, "weighted": weighted, "scores": scores}],
        "eval_final": {"weighted": weighted, "scores": scores, "passed": True},
    }


class ConfigTests(unittest.TestCase):
    def test_repository_contracts_validate(self) -> None:
        self.assertEqual(check_config.validate(), [])

    def test_rubric_weights_sum_to_one(self) -> None:
        rubric = yaml.safe_load((ROOT / "config/rubric.yaml").read_text())["rubric"]
        self.assertAlmostEqual(sum(row["weight"] for row in rubric["criteria"]), 1.0)


class PostTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = yaml.safe_load((ROOT / "config/brand.yaml").read_text())

    def test_valid_mechanism_post_passes(self) -> None:
        report = check_post.validate_post(valid_post(), dossier(), self.config)
        self.assertTrue(report["ok"], report["errors"])
        self.assertGreaterEqual(report["metrics"]["body_words"], 350)
        self.assertLessEqual(report["metrics"]["total_chars"], 3000)

    def test_missing_layer_bullet_fails(self) -> None:
        broken = valid_post().replace(
            "- Approval layer issues the final authorization, Approval office.\n", ""
        )
        report = check_post.validate_post(broken, dossier(), self.config)
        self.assertFalse(report["ok"])
        self.assertTrue(any("layer bullet count" in item for item in report["errors"]))

    def test_unverified_numeral_fails(self) -> None:
        broken = valid_post().replace(
            "The record connects", "A 999 megawatt claim appears. The record connects", 1
        )
        report = check_post.validate_post(broken, dossier(), self.config)
        self.assertTrue(any("numeral is not grounded" in item for item in report["errors"]))

    def test_political_advocacy_fails(self) -> None:
        broken = valid_post().replace(
            "The record connects", "Vote for the candidate. The record connects", 1
        )
        report = check_post.validate_post(broken, dossier(), self.config)
        self.assertTrue(any("advocacy" in item for item in report["errors"]))

    def test_no_target_cannot_have_post(self) -> None:
        report = check_post.validate_post(valid_post(), dossier(no_target=True), self.config)
        self.assertTrue(any("no-target" in item for item in report["errors"]))


class DossierTests(unittest.TestCase):
    def test_target_dossier_passes_structural_validation(self) -> None:
        errors: list[str] = []
        no_target, mechanism = validate_run.validate_dossier(dossier(), errors)
        self.assertFalse(no_target)
        self.assertEqual(mechanism["name"], "Texas Queue Gate")
        self.assertEqual(errors, [])

    def test_no_target_dossier_passes_structural_validation(self) -> None:
        errors: list[str] = []
        no_target, mechanism = validate_run.validate_dossier(
            dossier(no_target=True), errors
        )
        self.assertTrue(no_target)
        self.assertEqual(mechanism, {})
        self.assertEqual(errors, [])

    def test_missing_layer_source_fails(self) -> None:
        value = dossier()
        value["selected_mechanism"]["layers"][0]["primary_source"] = {}
        errors: list[str] = []
        validate_run.validate_dossier(value, errors)
        self.assertTrue(any("primary_source" in item for item in errors))


class ScoreTests(unittest.TestCase):
    def test_score_ship_flag_is_independent_of_prior_package_errors(self) -> None:
        rubric = yaml.safe_load(
            (ROOT / "config/rubric.yaml").read_text(encoding="utf-8")
        )["rubric"]
        criteria = [
            {
                "name": row["name"],
                "weight": row["weight"],
                "score": 9.0,
            }
            for row in rubric["criteria"]
        ]
        report = {
            "criteria": criteria,
            "weighted_total": 9.0,
            "threshold": rubric["ship_threshold"],
            "hard_fail_checks": [
                {"name": row["name"], "passed": True}
                for row in rubric["hard_fail_checks"]
            ],
            "hard_failures": [],
            "ship": True,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "score_report.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            errors = ["an unrelated dossier error"]
            validate_run.validate_score(path, errors)
        self.assertEqual(errors, ["an unrelated dossier error"])


class HistoryTests(unittest.TestCase):
    def test_history_builds_mechanism_and_art_cooldowns(self) -> None:
        records = [
            {
                "branch": "origin/codex/texas-stack-2026-08-29",
                "date": "2026-08-29",
                "suffix": 1,
                "dossier": dossier(),
                "art": {
                    "style_family": "cyanotype",
                    "hue_family": "blue",
                    "composition": "modular_grid",
                    "motifs": ["breaker"],
                },
            }
        ]
        result = history_scan.summarize(records, [], dt.date(2026, 9, 2))
        self.assertEqual(result["recent_mechanisms"][0]["name"], "Texas Queue Gate")
        self.assertEqual(
            result["artwork_cooldowns"]["style_families_last_8"], ["cyanotype"]
        )


class EmailTests(unittest.TestCase):
    def test_target_email_has_visible_immutable_image_link(self) -> None:
        url = (
            "https://raw.githubusercontent.com/Talonsturgill/"
            "linkedin-texas-ai-stack/" + "a" * 40 + "/out/post_image.png"
        )
        body = build_email.render_html(
            post=valid_post(),
            image_url=url,
            dossier=dossier(),
            score={"ship": True, "criteria": []},
            art_eval=art_eval(),
            date="September 2nd, 2026",
            branch="codex/texas-stack-2026-09-02",
            commit="a" * 40,
            editor_note="No unresolved issues.",
        )
        self.assertIn(f'href="{url}"', body)
        self.assertIn(f'src="{url}"', body)
        self.assertIn(url, body)

    def test_no_target_email_still_has_art(self) -> None:
        url = (
            "https://raw.githubusercontent.com/Talonsturgill/"
            "linkedin-texas-ai-stack/" + "b" * 40 + "/out/post_image.png"
        )
        body = build_email.render_html(
            post="",
            image_url=url,
            dossier=dossier(no_target=True),
            score={},
            art_eval=art_eval(),
            date="September 2nd, 2026",
            branch="codex/texas-stack-2026-09-02",
            commit="b" * 40,
            editor_note="No mechanism cleared the gate.",
        )
        self.assertIn("NO DEFENSIBLE TARGET THIS CYCLE", body)
        self.assertIn(f'src="{url}"', body)

    def test_payload_rejects_non_address_recipient(self) -> None:
        with self.assertRaises(ValueError):
            build_email.build_payload(to="me", subject="Draft", html_body="<p>x</p>")


if __name__ == "__main__":
    unittest.main()
