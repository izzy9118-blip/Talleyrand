from copy import deepcopy
from pathlib import Path
import shutil

import pytest
import yaml

from ratification_guard import (
    PASS_STATUS,
    RatificationGuardError,
    git_blob_sha1,
    validate_decision_record,
    validate_dossier,
    validate_in_progress_record,
)


def _template():
    return yaml.safe_load(Path("ratification/owner-decision.v12.template.yaml").read_text(encoding="utf-8"))


def _one_decision_progress():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V12-TEST"
    record["status"] = "OWNER_DECISIONS_IN_PROGRESS"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-09"
    record["deed_decisions"][0]["decision"] = "RATIFY"
    return record


def _completed_all_ratify():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V12-COMPLETE-TEST"
    record["status"] = "OWNER_DECISIONS_RECORDED"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-09"
    for item in record["deed_decisions"]:
        item["decision"] = "RATIFY"
    return record


def _copy_validation_surface(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree("deeds", root / "deeds")
    shutil.copytree("method", root / "method")
    shutil.copytree("ratification", root / "ratification")
    shutil.copytree("amendments", root / "amendments")
    shutil.copy("keel.md", root / "keel.md")
    return root


def test_live_ratification_closure_is_v13_exact_and_nonoperative():
    result = validate_dossier(".")
    assert result["status"] == PASS_STATUS
    assert result["closure"] == "TAL-RAT-CLOSURE-2026-08-09-013"
    assert result["active_dossier"] is None
    assert result["pending_deed_decisions"] == 0
    assert result["ratified_deed_decisions"] == 20
    assert result["live_ratified_deeds"] == 20


def test_closure_contains_every_live_deed_and_no_pending_deed():
    closure = yaml.safe_load(Path("ratification/2026-08-09-owner-ratification-closure-v13.yaml").read_text())
    assert "owner_removed_deeds" not in closure
    assert "owner_removed_deeds" not in closure["excluded_from_ratification_package"]
    assert closure["pending_deed_decisions"] == []
    assert {str(x["id"]) for x in closure["ratified_deed_decisions"]} == {
        "0", "A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B6",
        "B7", "C1", "C3", "C4", "C7", "C8", "C11", "D2", "D3", "D4",
    }


def test_live_ratification_authority_carries_D4_and_exact_sharpening():
    record = yaml.safe_load(Path("ratification/live-owner-ratifications.yaml").read_text())
    assert record["id"] == "TAL-RAT-LIVE-001"
    assert record["status"] == "ACTIVE_CARRY_FORWARD"
    assert record["self_certification"] == "PROHIBITED"
    assert len(record["deed_decisions"]) == 20
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    assert decisions["D4"]["decision"] == "RATIFY"
    assert decisions["D4"]["git_blob_sha1"] == "1f4c8cd2b8063443b1a549ac31c0fd7c66389fd9"
    for item in record["deed_decisions"]:
        assert item["decision"] == "RATIFY"
        assert git_blob_sha1(Path(item["path"])) == item["git_blob_sha1"]
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    d4 = bindings["TAL-DEED-D4-SHARP-001"]
    assert d4["deed"] == "D4"
    assert d4["git_blob_sha1"] == "57ab36c4ee9fb95e64925e71cb5a382f1eb04689"
    assert git_blob_sha1(Path(d4["path"])) == d4["git_blob_sha1"]


def test_C7_sharpening_preserves_adversarial_verification_and_bounded_secrecy():
    text = Path("deeds/amendments/2026-08-09-C7-adversarial-verification-sharpening.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Daylight is an instrument, not a virtue" in normalized
    assert "Do not ask to be trusted where you can arrange to be tested" in normalized
    assert "Price the watcher too" in normalized
    assert "Search failure alone is never converted into negative evidence" in normalized
    assert "Necessary secrets may remain secret" in normalized
    assert "Selective disclosure designed to create a false appearance of inspectability is counterfeit daylight" in normalized
    assert "The watcher is not presumed reliable merely because he is hostile" in normalized


def test_closure_carries_all_owner_ratifications_without_reopening_prior_deeds():
    closure = yaml.safe_load(Path("ratification/2026-08-09-owner-ratification-closure-v13.yaml").read_text())
    by_id = {str(x["id"]): x for x in closure["ratified_deed_decisions"]}
    assert set(by_id) == {"0", "A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B6", "B7", "C1", "C3", "C4", "C7", "C8", "C11", "D2", "D3", "D4"}
    for item in by_id.values():
        assert item["decision"] == "RATIFY"
        assert git_blob_sha1(Path(item["path"])) == item["git_blob_sha1"]


def test_historical_v12_template_preserves_final_pending_deed_and_no_authority():
    result = validate_decision_record(_template(), ".", completed=False)
    assert result["completed"] is False
    assert result["deed_decisions"] == 1
    assert {str(x["id"]) for x in _template()["deed_decisions"]} == {"D4"}


def test_final_single_deed_cannot_masquerade_as_incremental_record():
    record = _one_decision_progress()
    with pytest.raises(RatificationGuardError, match="leave at least one unit pending"):
        validate_in_progress_record(record, ".")


def test_out_of_scope_deed_cannot_be_smuggled_into_owner_decision():
    record = _completed_all_ratify()
    record["deed_decisions"][-1]["id"] = "X-NOT-LIVE"
    with pytest.raises(RatificationGuardError, match="scope mismatch"):
        validate_decision_record(record, ".", completed=True)


def test_completed_record_requires_explicit_owner_authority():
    record = _completed_all_ratify()
    result = validate_decision_record(record, ".", completed=True)
    assert result["completed"] is True
    record["owner_directive"] = ""
    with pytest.raises(RatificationGuardError, match="owner directive"):
        validate_decision_record(record, ".", completed=True)


def test_ratified_D4_text_change_invalidates_closure(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/D4-disclose-the-mechanism.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_carried_forward_D3_text_change_invalidates_closure(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/D3-counsel-against-the-inclination.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_D4_sharpening_change_invalidates_closure(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/amendments/2026-08-09-D4-accountable-mechanism-sharpening.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_closure_cannot_reintroduce_a_pending_D4_decision(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "ratification/2026-08-09-owner-ratification-closure-v13.yaml"
    closure = yaml.safe_load(path.read_text(encoding="utf-8"))
    closure["pending_deed_decisions"] = [{"id": "D4", "owner_decision": "PENDING_OWNER_RULING"}]
    path.write_text(yaml.safe_dump(closure, sort_keys=False), encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="zero pending deed decisions"):
        validate_dossier(root)


def test_final_D4_owner_act_is_completed_and_not_an_in_progress_surface():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v12-complete.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["completed_surface"] is True
    assert result["completed"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 0


def test_closure_preserves_constitutional_non_effects():
    closure = yaml.safe_load(Path("ratification/2026-08-09-owner-ratification-closure-v13.yaml").read_text())
    assert closure["non_effects"] == [
        "voice remains ungranted",
        "runtime remains NOT_OPERATIONAL",
        "semantic completion remains INCOMPLETE",
        "completeness remains PENDING_PROBE",
        "Sanctum establishment does not occur",
    ]


def test_historical_v7_C7_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v7-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 5


def test_historical_v8_C8_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v8-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 4


def test_historical_v9_C11_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v9-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 3


def test_historical_v10_D2_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v10-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 2


def test_historical_v11_D3_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v11-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 1
