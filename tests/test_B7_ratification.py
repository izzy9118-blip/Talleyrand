from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B7_PATH = Path("deeds/B7-refuse-the-false-scale.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B7-causal-scale-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_live_v3_record_ratifies_through_B7_and_leaves_nine_pending():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 6
    assert result["pending_units"] == 9
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    for did in ("B1", "B2", "B3", "B4", "B6", "B7"):
        assert by_id[did] == "RATIFY"
    assert all(
        decision == "PENDING_OWNER_RULING"
        for did, decision in by_id.items()
        if did not in {"B1", "B2", "B3", "B4", "B6", "B7"}
    )
    assert by_id["C2"] == "PENDING_OWNER_RULING"
    assert "A5" not in by_id


def test_B7_ratification_is_bound_to_frozen_deed_and_causal_scale_sharpening():
    record = _record()
    assert git_blob_sha1(B7_PATH) == "47d8a79503239186b2210bae5106c2994be2ccb2"
    assert git_blob_sha1(SHARPENING_PATH) == "975d969f17b2f2a20e5723539b7709b2816ecd38"

    by_id = {item["id"]: item for item in record["interpretive_sharpenings"]}
    binding = by_id["TAL-DEED-B7-SHARP-001"]
    assert binding["deed"] == "B7"
    assert binding["deed_git_blob_sha1"] == "47d8a79503239186b2210bae5106c2994be2ccb2"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "975d969f17b2f2a20e5723539b7709b2816ecd38"
    assert binding["status"] == "OWNER_RATIFIED"


def test_B7_sharpening_keeps_scale_tied_to_causal_force():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "Scale follows causal force" in text
    assert "Do not reject an aggregate merely because its components differ" in text
    assert "Disaggregation is not automatically superior" in text
    assert "reconstructed mechanism makes operative" in text
    assert "stop at unresolved rather than substitute ministerial intuition" in text


def test_manifest_loads_B7_sharpening_and_advances_to_C2():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 12
    assert state["effective_pending_deed_rulings"] == 9
    assert "B7" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B7_owner_decision"] == "RATIFY"
    assert state["deed_B7_owner_sharpening"] == "TAL-DEED-B7-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["pending_deed_units"] == 9
    assert review["next_pending_deed"] == "C2"
    assert "TAL-DEED-B7-SHARP-001" in review["owner_ratified_deed_sharpenings"]
    assert manifest["records"]["deed_B7_interpretive_sharpening"] == str(SHARPENING_PATH)
