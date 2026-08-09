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
    return yaml.safe_load(Path("ratification/owner-decision.v8.template.yaml").read_text(encoding="utf-8"))


def _one_decision_progress():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V8-TEST"
    record["status"] = "OWNER_DECISIONS_IN_PROGRESS"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-09"
    record["deed_decisions"][0]["decision"] = "RATIFY"
    return record


def _completed_all_ratify():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V8-COMPLETE-TEST"
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


def test_live_dossier_is_v8_exact_and_nonoperative():
    result = validate_dossier(".")
    assert result["status"] == PASS_STATUS
    assert result["active_dossier"] == "TAL-RAT-DOSSIER-2026-08-09-008"
    assert result["pending_deed_decisions"] == 5
    assert result["prior_owner_decisions"] == 16
    assert result["live_ratified_deeds"] == 15


def test_active_dossier_contains_only_five_remaining_live_pending_deeds():
    dossier = yaml.safe_load(Path("ratification/2026-08-09-owner-review-dossier-v8.yaml").read_text())
    assert "owner_removed_deeds" not in dossier
    assert "owner_removed_deeds" not in dossier["excluded_from_ratification_package"]
    assert set(str(x["id"]) for x in dossier["pending_deed_decisions"]) == {
        "C8", "C11", "D2", "D3", "D4"
    }


def test_live_ratification_authority_carries_C7_and_exact_sharpening():
    record = yaml.safe_load(Path("ratification/live-owner-ratifications.yaml").read_text())
    assert record["id"] == "TAL-RAT-LIVE-001"
    assert record["status"] == "ACTIVE_CARRY_FORWARD"
    assert record["self_certification"] == "PROHIBITED"
    assert len(record["deed_decisions"]) == 15
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    assert decisions["C7"]["decision"] == "RATIFY"
    assert decisions["C7"]["git_blob_sha1"] == "9e5f9e1ecdab0b13ab52f6c9634c94fe7faa3032"
    for item in record["deed_decisions"]:
        assert item["decision"] == "RATIFY"
        assert git_blob_sha1(Path(item["path"])) == item["git_blob_sha1"]
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    c7 = bindings["TAL-DEED-C7-SHARP-001"]
    assert c7["deed"] == "C7"
    assert c7["git_blob_sha1"] == "a8207ef26f3162fa76e6ddaf308b2a8823df639a"
    assert git_blob_sha1(Path(c7["path"])) == c7["git_blob_sha1"]


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


def test_carried_forward_owner_ratifications_include_C7_without_reopening_prior_deeds():
    dossier = yaml.safe_load(Path("ratification/2026-08-09-owner-review-dossier-v8.yaml").read_text())
    by_id = {str(x["id"]): x for x in dossier["prior_owner_decisions_not_reopened"]}
    assert set(by_id) == {"TAL-DISCOVERY-001", "0", "A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B6", "B7", "C1", "C3", "C4", "C7"}
    for item in by_id.values():
        assert item["decision"] == "RATIFY"
        assert git_blob_sha1(Path(item["path"])) == item["git_blob_sha1"]


def test_v8_template_has_only_five_live_pending_deeds_and_no_authority():
    result = validate_decision_record(_template(), ".", completed=False)
    assert result["completed"] is False
    assert result["deed_decisions"] == 5
    assert {str(x["id"]) for x in _template()["deed_decisions"]} == {"C8", "C11", "D2", "D3", "D4"}


def test_incremental_v8_record_can_decide_one_deed_without_inventing_others():
    record = _one_decision_progress()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 1
    assert result["pending_units"] == 4
    assert record["deed_decisions"][0]["id"] == "C8"


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


def test_pending_deed_text_change_invalidates_active_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/C8-take-the-seat-refuse-the-role.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_carried_forward_C7_text_change_invalidates_active_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/C7-declare-in-daylight.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_C7_sharpening_change_invalidates_active_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/amendments/2026-08-09-C7-adversarial-verification-sharpening.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_dossier_cannot_pre_decide_C8(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "ratification/2026-08-09-owner-review-dossier-v8.yaml"
    dossier = yaml.safe_load(path.read_text(encoding="utf-8"))
    dossier["pending_deed_decisions"][0]["owner_decision"] = "RATIFY"
    path.write_text(yaml.safe_dump(dossier, sort_keys=False), encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="must not pre-decide"):
        validate_dossier(root)


def test_historical_v7_C7_owner_record_remains_readable_but_not_active():
    record = yaml.safe_load(Path("ratification/2026-08-09-owner-deed-decisions-v7-in-progress.yaml").read_text())
    result = validate_in_progress_record(record, ".")
    assert result["historical_surface"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 5
