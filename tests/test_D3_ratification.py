from pathlib import Path

import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
D3_PATH = Path("deeds/D3-counsel-against-the-inclination.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-D3-candid-counsel-sharpening.md")


def test_D3_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    d3 = decisions["D3"]
    assert d3["decision"] == "RATIFY"
    assert d3["git_blob_sha1"] == "f7d9e15405018dbf19c2b14cb3933458ad581d13"
    assert git_blob_sha1(D3_PATH) == d3["git_blob_sha1"]
    assert len(decisions) == 20


def test_D3_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-D3-SHARP-001"]
    assert binding["deed"] == "D3"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "4909cf2e6eb582343b934fe7f77ebb05a85c5a02"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_D3_candid_counsel_rules_are_mandatory():
    normalized = " ".join(SHARPENING_PATH.read_text(encoding="utf-8").split())
    assert "Difficulty, dissent, or dislike gives the counsel no special truth" in normalized
    assert "State separately the decision required, documented facts" in normalized
    assert "Plain speech means intelligible and unhidden, not needlessly injurious" in normalized
    assert "The step may not secretly commit the principal" in normalized
    assert "Persistence must be proportionate" in normalized
    assert "Hindsight does not self-ratify counsel" in normalized
    assert "does not alone prove that the advice was correct" in normalized


def test_manifest_loads_D3_only_with_its_sharpening_and_moves_next_to_D4():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 20
    assert state["effective_pending_deed_rulings"] == 0
    assert state["deed_D3_owner_decision"] == "RATIFY"
    assert state["deed_D3_owner_sharpening"] == "TAL-DEED-D3-SHARP-001"
    assert manifest["records"]["deed_D3_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] is None
    assert "TAL-DEED-D3-SHARP-001" in review["owner_ratified_deed_sharpenings"]
