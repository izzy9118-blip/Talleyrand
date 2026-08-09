from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1, validate_in_progress_record


LIVE_RECORD = Path("ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml")
B4_PATH = Path("deeds/B4-locate-the-seam.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B4-evidenced-seam-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_B1_through_B4_remain_ratified_after_later_owner_acts():
    record = _record()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] >= 4
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    for did in ("B1", "B2", "B3", "B4"):
        assert by_id[did] == "RATIFY"
    assert "A5" not in by_id


def test_B4_ratification_is_bound_to_frozen_deed_and_evidenced_seam_sharpening():
    record = _record()
    assert git_blob_sha1(B4_PATH) == "f2666f50d2b955fa157a46b20236935cd90d06dd"
    assert git_blob_sha1(SHARPENING_PATH) == "603964b3142c1b91803a0b5b017992bc905d63e2"

    by_id = {item["id"]: item for item in record["interpretive_sharpenings"]}
    binding = by_id["TAL-DEED-B4-SHARP-001"]
    assert binding["deed"] == "B4"
    assert binding["deed_git_blob_sha1"] == "f2666f50d2b955fa157a46b20236935cd90d06dd"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "603964b3142c1b91803a0b5b017992bc905d63e2"
    assert binding["status"] == "OWNER_RATIFIED"


def test_B4_sharpening_requires_evidence_causation_and_no_manufactured_seam():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "A seam is an evidenced divergence" in normalized
    assert "None of them proves a seam by itself" in normalized
    assert "state the transmission" in normalized
    assert "real decision node" in normalized
    assert "NO_WORKABLE_SEAM" in normalized
    assert "displacement does not make that person truthful" in normalized
    assert "cross-board seam exists only where an" in normalized
    assert "Proximity, simultaneity" in normalized


def test_manifest_continues_to_load_B4_sharpening():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert "B4" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B4_owner_decision"] == "RATIFY"
    assert state["deed_B4_owner_sharpening"] == "TAL-DEED-B4-SHARP-001"
    review = manifest["ratification_review_state"]
    assert "TAL-DEED-B4-SHARP-001" in review["owner_ratified_deed_sharpenings"]
    assert manifest["records"]["deed_B4_interpretive_sharpening"] == str(SHARPENING_PATH)
