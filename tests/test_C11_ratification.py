from pathlib import Path

import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
C11_PATH = Path("deeds/C11-supply-the-spine.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-C11-sovereign-support-sharpening.md")


def test_C11_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    c11 = decisions["C11"]
    assert c11["decision"] == "RATIFY"
    assert c11["git_blob_sha1"] == "51ebfcd57dfe5c93b7e9df9a3ea67e2d74a36948"
    assert git_blob_sha1(C11_PATH) == c11["git_blob_sha1"]
    assert len(decisions) == 17


def test_C11_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-C11-SHARP-001"]
    assert binding["deed"] == "C11"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "b5c873d31a24a34d92dbff8afbf5a833684faaa4"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_C11_sovereign_support_rules_are_mandatory():
    normalized = " ".join(SHARPENING_PATH.read_text(encoding="utf-8").split())
    assert "does not treat another sovereign person or institution as material" in normalized
    assert "Do not diagnose fear merely because the ally declines" in normalized
    assert "Internal voices remain sovereign authors" in normalized
    assert "never licenses recruiting subordinates against their leadership" in normalized
    assert "contrary internal advice remains visible" in normalized
    assert "Pressure is bounded by alliance and law" in normalized
    assert "C11 does not force unity" in normalized


def test_manifest_loads_C11_only_with_its_sharpening_and_moves_next_to_D2():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 17
    assert state["effective_pending_deed_rulings"] == 3
    assert state["deed_C11_owner_decision"] == "RATIFY"
    assert state["deed_C11_owner_sharpening"] == "TAL-DEED-C11-SHARP-001"
    assert manifest["records"]["deed_C11_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "D2"
    assert "TAL-DEED-C11-SHARP-001" in review["owner_ratified_deed_sharpenings"]
