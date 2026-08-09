from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
B7_PATH = Path("deeds/B7-refuse-the-false-scale.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B7-causal-scale-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_live_record_preserves_B7_ratification():
    record = _record()
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    assert by_id["B7"] == "RATIFY"
    assert len(by_id) == 12


def test_B7_ratification_is_bound_to_frozen_deed_and_causal_scale_sharpening():
    record = _record()
    assert git_blob_sha1(B7_PATH) == "47d8a79503239186b2210bae5106c2994be2ccb2"
    assert git_blob_sha1(SHARPENING_PATH) == "975d969f17b2f2a20e5723539b7709b2816ecd38"

    by_id = {item["id"]: item for item in record["interpretive_bindings"]}
    binding = by_id["TAL-DEED-B7-SHARP-001"]
    assert binding["deed"] == "B7"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "975d969f17b2f2a20e5723539b7709b2816ecd38"


def test_B7_sharpening_keeps_scale_tied_to_causal_force():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "Scale follows causal force" in text
    assert "Do not reject an aggregate merely because its components differ" in text
    assert "Disaggregation is not automatically superior" in text
    assert "reconstructed mechanism makes operative" in text
    assert "stop at unresolved rather than substitute ministerial intuition" in text


def test_manifest_continues_to_load_B7_on_live_only_surface():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 12
    assert state["effective_pending_deed_rulings"] == 8
    assert "B7" in {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert state["deed_B7_owner_decision"] == "RATIFY"
    assert state["deed_B7_owner_sharpening"] == "TAL-DEED-B7-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["pending_deed_units"] == 8
    assert review["next_pending_deed"] == "C3"
    assert "owner_removed_deeds" not in review
    assert "TAL-DEED-B7-SHARP-001" in review["owner_ratified_deed_sharpenings"]
    assert manifest["records"]["deed_B7_interpretive_sharpening"] == str(SHARPENING_PATH)
