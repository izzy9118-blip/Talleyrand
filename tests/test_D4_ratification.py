from pathlib import Path

import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
D4_PATH = Path("deeds/D4-disclose-the-mechanism.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-D4-accountable-mechanism-sharpening.md")


def test_D4_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    d4 = decisions["D4"]
    assert d4["decision"] == "RATIFY"
    assert d4["git_blob_sha1"] == "1f4c8cd2b8063443b1a549ac31c0fd7c66389fd9"
    assert git_blob_sha1(D4_PATH) == d4["git_blob_sha1"]
    assert len(decisions) == 20


def test_D4_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-D4-SHARP-001"]
    assert binding["deed"] == "D4"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "57ab36c4ee9fb95e64925e71cb5a382f1eb04689"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_D4_accountable_disclosure_rules_are_mandatory():
    normalized = " ".join(SHARPENING_PATH.read_text(encoding="utf-8").split())
    assert "properly authorized accountable recipient" in normalized
    assert "Report the mechanism at proposition level" in normalized
    assert "Distinguish what was intended, what actually occurred" in normalized
    assert "Lawful confidentiality remains lawful" in normalized
    assert "Disclosure does not cure the mechanism" in normalized
    assert "The operator does not certify the operator" in normalized
    assert "A disclosed mechanism can still be wrong" in normalized


def test_manifest_loads_D4_with_its_sharpening_and_closes_review():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 20
    assert state["effective_pending_deed_rulings"] == 0
    assert state["deed_D4_owner_decision"] == "RATIFY"
    assert state["deed_D4_owner_sharpening"] == "TAL-DEED-D4-SHARP-001"
    assert manifest["records"]["deed_D4_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["status"] == "OWNER_REVIEW_COMPLETE"
    assert manifest["records"]["owner_ratification_dossier_active"] is None
    assert manifest["records"]["owner_ratification_template_active"] is None
    assert review["next_pending_deed"] is None
    assert "TAL-DEED-D4-SHARP-001" in review["owner_ratified_deed_sharpenings"]


def test_D4_completion_does_not_self_certify_or_activate_talleyrand():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["voice_state"]["license_granted"] is False
    assert manifest["status"]["runtime"] == "NOT_OPERATIONAL"
    assert manifest["status"]["semantic_completion"] == "INCOMPLETE"
    assert manifest["status"]["completeness"] == "PENDING_PROBE"
    assert manifest["sanctum_contract"]["registry_state"] == "not_yet_established"
    assert manifest["status"]["self_certification"] == "PROHIBITED"
