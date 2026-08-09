from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B6_PATH = Path("deeds/B6-set-the-quantum-and-the-clock.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B6-quantum-clock-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_B1_through_B4_and_B6_remain_ratified_after_later_owner_acts():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] >= 5
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    for did in ("B1", "B2", "B3", "B4", "B6"):
        assert by_id[did] == "RATIFY"
    assert "A5" not in by_id


def test_B6_ratification_is_bound_to_frozen_deed_and_quantum_clock_sharpening():
    record = _record()
    assert git_blob_sha1(B6_PATH) == "d805b0ad39ba8f5e56c43300ae5a119ee109412e"
    assert git_blob_sha1(SHARPENING_PATH) == "b09ee65e71f2026be496eec662227b9a5322d1b3"

    by_id = {item["id"]: item for item in record["interpretive_sharpenings"]}
    binding = by_id["TAL-DEED-B6-SHARP-001"]
    assert binding["deed"] == "B6"
    assert binding["deed_git_blob_sha1"] == "d805b0ad39ba8f5e56c43300ae5a119ee109412e"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "b09ee65e71f2026be496eec662227b9a5322d1b3"
    assert binding["status"] == "OWNER_RATIFIED"


def test_B6_sharpening_preserves_the_deep_simple_rule():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "Judge quantum and clock together" in text
    assert "minimum sufficient measure, not the smallest imaginable measure" in text
    assert "too much and too little" in text
    assert "too early and too late" in text
    assert "Time changes the required quantum" in text
    assert "right moment may reduce the amount required" in text
    assert "least sufficient cost" in text
    assert "not a doctrine of always doing less" in text


def test_manifest_continues_to_load_B6_sharpening():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert "B6" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B6_owner_decision"] == "RATIFY"
    assert state["deed_B6_owner_sharpening"] == "TAL-DEED-B6-SHARP-001"
    review = manifest["ratification_review_state"]
    assert "TAL-DEED-B6-SHARP-001" in review["owner_ratified_deed_sharpenings"]
    assert manifest["records"]["deed_B6_interpretive_sharpening"] == str(SHARPENING_PATH)
