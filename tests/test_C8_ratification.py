from pathlib import Path

import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
C8_PATH = Path("deeds/C8-take-the-seat-refuse-the-role.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-C8-entitled-standing-sharpening.md")


def test_C8_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    c8 = decisions["C8"]
    assert c8["decision"] == "RATIFY"
    assert c8["git_blob_sha1"] == "c83492946955e26b9a29ddbe88d5783e3c028f68"
    assert git_blob_sha1(C8_PATH) == c8["git_blob_sha1"]
    assert len(decisions) == 18


def test_C8_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-C8-SHARP-001"]
    assert binding["deed"] == "C8"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "4eae5a9c5493ffcd86835ae91ae260d77dffa1f4"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_C8_entitled_standing_rules_are_mandatory():
    normalized = " ".join(SHARPENING_PATH.read_text(encoding="utf-8").split())
    assert "The entitlement comes first" in normalized
    assert "The scripted role must also be evidenced rather than imagined" in normalized
    assert "Enter and refuse in the same attributable motion" in normalized
    assert "Participation is not magic" in normalized
    assert "does not create legal authority" in normalized
    assert "never licenses trespass, impersonation, credential abuse" in normalized
    assert "does not authorize entry by deception or force" in normalized


def test_manifest_loads_C8_only_with_its_sharpening_and_moves_next_to_C11():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 18
    assert state["effective_pending_deed_rulings"] == 2
    assert state["deed_C8_owner_decision"] == "RATIFY"
    assert state["deed_C8_owner_sharpening"] == "TAL-DEED-C8-SHARP-001"
    assert manifest["records"]["deed_C8_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "D3"
    assert "TAL-DEED-C8-SHARP-001" in review["owner_ratified_deed_sharpenings"]
