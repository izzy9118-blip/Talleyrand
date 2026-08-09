from pathlib import Path

import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
D2_PATH = Path("deeds/D2-bank-the-weapon-with-permission-attached.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-D2-bounded-contingency-sharpening.md")


def test_D2_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    d2 = decisions["D2"]
    assert d2["decision"] == "RATIFY"
    assert d2["git_blob_sha1"] == "9aac11883da3deb7d2d13d6177cbeaad1fac464a"
    assert git_blob_sha1(D2_PATH) == d2["git_blob_sha1"]
    assert len(decisions) == 19


def test_D2_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-D2-SHARP-001"]
    assert binding["deed"] == "D2"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "2ec61eee9e9ea618b223035b8a5260a5d8442458"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_D2_bounded_contingency_rules_are_mandatory():
    normalized = " ".join(SHARPENING_PATH.read_text(encoding="utf-8").split())
    assert "Permission remains attached to the measure" in normalized
    assert "A general mandate, prior enthusiasm, silence, assumed necessity" in normalized
    assert "The trigger must be capable of attributable verification" in normalized
    assert "Advance authorization is not automatic execution" in normalized
    assert "High-impact or irreversible measures require" in normalized
    assert "Preparation must not itself create the crisis it anticipates" in normalized
    assert "Forecasts remain graded and revisable" in normalized


def test_manifest_loads_D2_only_with_its_sharpening_and_moves_next_to_D3():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 19
    assert state["effective_pending_deed_rulings"] == 1
    assert state["deed_D2_owner_decision"] == "RATIFY"
    assert state["deed_D2_owner_sharpening"] == "TAL-DEED-D2-SHARP-001"
    assert manifest["records"]["deed_D2_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "D4"
    assert "TAL-DEED-D2-SHARP-001" in review["owner_ratified_deed_sharpenings"]
