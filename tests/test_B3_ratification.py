from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B3_PATH = Path("deeds/B3-assess-the-person-as-material.md")
B3_RATIFICATION = Path("ratification/2026-08-08-B3-capacity-pricing-ratification.yaml")
SOURCE_SHARPENING = Path("deeds/amendments/2026-08-06-session-sharpenings.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_live_v3_record_ratifies_B1_B2_B3_and_leaves_twelve_pending():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 3
    assert result["pending_units"] == 12
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    for did in ("B1", "B2", "B3"):
        assert by_id[did] == "RATIFY"
    assert all(
        decision == "PENDING_OWNER_RULING"
        for did, decision in by_id.items()
        if did not in {"B1", "B2", "B3"}
    )
    assert "A5" not in by_id


def test_B3_ratification_is_bound_to_frozen_deed_and_exact_capacity_pricing_source():
    record = _record()
    assert git_blob_sha1(B3_PATH) == "d370b2a98e2e2f620b258a068ead4b1383c1d05d"
    assert git_blob_sha1(SOURCE_SHARPENING) == "619180d35bf4c8559b653068d8f7c9ff477507f7"

    by_id = {item["id"]: item for item in record["interpretive_sharpenings"]}
    binding = by_id["TAL-DEED-B3-SHARP-001"]
    assert binding["deed"] == "B3"
    assert binding["deed_git_blob_sha1"] == "d370b2a98e2e2f620b258a068ead4b1383c1d05d"
    assert binding["path"] == str(B3_RATIFICATION)
    assert git_blob_sha1(B3_RATIFICATION) == binding["git_blob_sha1"] == "cdcfb4dc570ea89dba298ecf665d5be79f20149e"
    assert binding["source_path"] == str(SOURCE_SHARPENING)
    assert binding["source_git_blob_sha1"] == "619180d35bf4c8559b653068d8f7c9ff477507f7"
    assert binding["component"] == "B3 — the capacity-pricing requirement"
    assert binding["status"] == "OWNER_RATIFIED"


def test_B3_capacity_pricing_record_adopts_only_B3_component():
    record = yaml.safe_load(B3_RATIFICATION.read_text(encoding="utf-8"))
    assert record["id"] == "TAL-DEED-B3-SHARP-001"
    assert record["authority"] == "REPOSITORY_OWNER_DIRECTIVE"
    assert record["source_sharpening"]["adoption_scope"] == "B3_CAPACITY_PRICING_COMPONENT_ONLY"
    assert record["source_sharpening"]["discovery_component_effect"] == "NO_NEW_RULING"
    assert record["rule"]["principle"] == "CAPACITY_MUST_BE_PRICED_BEFORE_PERSON_LEDGER_ASSIGNMENT"
    assert "states what a person wants without pricing" in record["rule"]["statement"]


def test_manifest_loads_B3_capacity_pricing_and_advances_to_B4():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 9
    assert state["effective_pending_deed_rulings"] == 12
    assert "B3" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B3_owner_decision"] == "RATIFY"
    assert state["deed_B3_owner_sharpening"] == "TAL-DEED-B3-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["pending_deed_units"] == 12
    assert review["next_pending_deed"] == "B4"
    assert "TAL-DEED-B3-SHARP-001" in review["owner_ratified_deed_sharpenings"]
    assert manifest["records"]["deed_B3_capacity_pricing_ratification"] == str(B3_RATIFICATION)
