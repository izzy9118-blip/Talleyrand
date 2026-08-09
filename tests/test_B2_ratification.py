from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B2_PATH = Path("deeds/B2-price-the-coalition-in-beliefs.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B2-coalition-belief-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_live_v3_record_ratifies_B1_and_B2_and_leaves_thirteen_pending():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 2
    assert result["pending_units"] == 13
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    assert by_id["B1"] == "RATIFY"
    assert by_id["B2"] == "RATIFY"
    assert all(
        value == "PENDING_OWNER_RULING"
        for key, value in by_id.items()
        if key not in {"B1", "B2"}
    )
    assert "A5" not in by_id


def test_B2_ratification_is_bound_to_frozen_deed_and_member_reconstruction_sharpening():
    record = _record()
    assert git_blob_sha1(B2_PATH) == "89b82d33f5fe365e457e8867148281f35ae314fa"
    sharpenings = record.get("interpretive_sharpenings")
    assert isinstance(sharpenings, list)
    by_id = {item["id"]: item for item in sharpenings}
    assert set(by_id) == {"TAL-DEED-B1-SHARP-001", "TAL-DEED-B2-SHARP-001"}
    binding = by_id["TAL-DEED-B2-SHARP-001"]
    assert binding["deed"] == "B2"
    assert binding["deed_git_blob_sha1"] == "89b82d33f5fe365e457e8867148281f35ae314fa"
    assert binding["status"] == "OWNER_RATIFIED"
    assert Path(binding["path"]) == SHARPENING_PATH
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"] == "2c8c38b0f63f9c9da7a1ac20f9ce2e52591b3bfe"
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "reconstruct each member separately" in text
    assert "least costly **truthful** change" in text
    assert "does not presume that every coalition is merely apparent" in text
    assert "dated leak prediction remains mandatory" in text


def test_B2_sharpening_preserves_nonbelief_causes_of_adherence():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    for term in (
        "coercion",
        "dependence",
        "obligation",
        "material interest",
        "institutional lock-in",
        "fear",
        "lack of alternatives",
    ):
        assert term in text
    assert "what observable conduct should change" in text
    assert "by what date that change should become visible" in text


def test_manifest_loads_B2_sharpening_and_advances_to_B3():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 8
    assert state["effective_pending_deed_rulings"] == 13
    ratified = {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert {"B1", "B2"}.issubset(ratified)
    assert state["deed_B2_owner_decision"] == "RATIFY"
    assert state["deed_B2_owner_sharpening"] == "TAL-DEED-B2-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["active_decision_record"] == str(LIVE_RECORD)
    assert review["pending_deed_units"] == 13
    assert review["next_pending_deed"] == "B3"
    assert manifest["records"]["deed_B2_interpretive_sharpening"] == str(SHARPENING_PATH)
