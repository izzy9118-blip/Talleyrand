from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B1_PATH = Path("deeds/B1-recover-the-design-from-fragments.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B1-no-forced-unity-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_live_v3_record_ratifies_only_B1_and_leaves_fourteen_pending():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 1
    assert result["pending_units"] == 14
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    assert by_id["B1"] == "RATIFY"
    assert all(value == "PENDING_OWNER_RULING" for key, value in by_id.items() if key != "B1")
    assert "A5" not in by_id


def test_B1_ratification_is_bound_to_frozen_deed_and_no_forced_unity_sharpening():
    record = _record()
    assert git_blob_sha1(B1_PATH) == "d9ffaadf3ba4ec15d1b2ab4b7fdc4c1dc873e06d"
    sharpenings = record.get("interpretive_sharpenings")
    assert isinstance(sharpenings, list) and len(sharpenings) == 1
    binding = sharpenings[0]
    assert binding["id"] == "TAL-DEED-B1-SHARP-001"
    assert binding["deed"] == "B1"
    assert binding["deed_git_blob_sha1"] == "d9ffaadf3ba4ec15d1b2ab4b7fdc4c1dc873e06d"
    assert binding["status"] == "OWNER_RATIFIED"
    assert Path(binding["path"]) == SHARPENING_PATH
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"] == "4eb293085c4c5be0f3712717d30df497a7276b85"
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "smallest design or set of interacting designs" in text
    assert "coordination" in text
    assert "exploitation" in text
    assert "convergence" in text
    assert "coincidence" in text
    assert "Connected outcomes do not establish a single" in text
    assert "cannot promote that whole construction to documented fact" in text


def test_manifest_loads_B1_sharpening_and_advances_to_B2():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 7
    assert state["effective_pending_deed_rulings"] == 14
    assert "B1" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B1_owner_decision"] == "RATIFY"
    assert state["deed_B1_owner_sharpening"] == "TAL-DEED-B1-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["active_decision_record"] == str(LIVE_RECORD)
    assert review["pending_deed_units"] == 14
    assert review["next_pending_deed"] == "B2"
    assert manifest["records"]["deed_B1_interpretive_sharpening"] == str(SHARPENING_PATH)
