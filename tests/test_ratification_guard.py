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
    return yaml.safe_load(Path("ratification/owner-decision.v3.template.yaml").read_text(encoding="utf-8"))


def _one_decision_progress():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V3-TEST"
    record["status"] = "OWNER_DECISIONS_IN_PROGRESS"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-08"
    record["deed_decisions"][0]["decision"] = "RATIFY"
    return record


def _completed_all_ratify():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V3-COMPLETE-TEST"
    record["status"] = "OWNER_DECISIONS_RECORDED"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-08"
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


def test_live_dossier_is_v3_exact_and_nonoperative():
    result = validate_dossier(".")
    assert result["status"] == PASS_STATUS
    assert result["active_dossier"] == "TAL-RAT-DOSSIER-2026-08-08-003"
    assert result["pending_deed_decisions"] == 15
    assert result["prior_owner_decisions"] == 7
    assert result["owner_removed_deeds"] == 1


def test_predecessor_dossiers_are_preserved():
    assert Path("ratification/2026-08-08-owner-review-dossier.yaml").is_file()
    assert Path("ratification/2026-08-08-owner-review-dossier-v2.yaml").is_file()
    active = yaml.safe_load(Path("ratification/2026-08-08-owner-review-dossier-v3.yaml").read_text())
    assert active["supersedes"] == "TAL-RAT-DOSSIER-2026-08-08-002"


def test_A5_is_owner_removed_not_pending_or_live():
    dossier = yaml.safe_load(Path("ratification/2026-08-08-owner-review-dossier-v3.yaml").read_text())
    pending = {str(x["id"]) for x in dossier["pending_deed_decisions"]}
    assert "A5" not in pending
    assert not Path("deeds/A5-read-the-ground-beneath-the-table.md").exists()
    removed = dossier["owner_removed_deeds"]
    assert len(removed) == 1
    assert removed[0]["id"] == "A5"
    assert removed[0]["historical_git_blob_sha1"] == "a089840a1daa38321bb66afcd7f2f11808c72938"
    assert removed[0]["disposition"] == "REMOVED_FROM_LIVE_CORPUS_AND_FUTURE_RATIFICATION_SCOPE"


def test_A5_owner_removal_record_is_explicit_and_blob_bound():
    dossier = yaml.safe_load(Path("ratification/2026-08-08-owner-review-dossier-v3.yaml").read_text())
    binding = dossier["governing_bindings"]["A5_owner_removal"]
    path = Path(binding["path"])
    assert path.is_file()
    assert git_blob_sha1(path) == binding["git_blob_sha1"] == "fc185c7983f817c784b9eadec9293cd43751532a"
    record = yaml.safe_load(path.read_text())
    assert record["authority"] == "REPOSITORY_OWNER_DIRECTIVE"
    assert record["owner_directive"] == "delete a5"
    assert record["disposition"]["runtime_eligibility"] == "PROHIBITED"


def test_carried_forward_owner_ratifications_are_exact_and_not_reopened():
    dossier = yaml.safe_load(Path("ratification/2026-08-08-owner-review-dossier-v3.yaml").read_text())
    by_id = {str(x["id"]): x for x in dossier["prior_owner_decisions_not_reopened"]}
    assert set(by_id) == {"TAL-DISCOVERY-001", "C1", "0", "A1", "A2", "A3", "A4"}
    for item in by_id.values():
        assert item["decision"] == "RATIFY"
        assert git_blob_sha1(Path(item["path"])) == item["git_blob_sha1"]


def test_v3_template_has_only_15_live_pending_deeds_and_no_authority():
    result = validate_decision_record(_template(), ".", completed=False)
    assert result["completed"] is False
    assert result["deed_decisions"] == 15
    ids = {str(x["id"]) for x in _template()["deed_decisions"]}
    assert "A5" not in ids
    assert ids == {"B1", "B2", "B3", "B4", "B6", "B7", "C2", "C3", "C4", "C7", "C8", "C11", "D2", "D3", "D4"}


def test_incremental_v3_record_can_decide_one_deed_without_inventing_others():
    record = _one_decision_progress()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 1
    assert result["pending_units"] == 14
    assert record["deed_decisions"][0]["id"] == "B1"


def test_A5_cannot_be_smuggled_into_owner_decision():
    record = _completed_all_ratify()
    record["deed_decisions"][-1]["id"] = "A5"
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
    path = root / "deeds/B1-recover-the-design-from-fragments.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_carried_forward_ratified_deed_text_change_invalidates_active_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/A4-read-the-document-by-its-true-audience.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_dossier_cannot_pre_decide_B1(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "ratification/2026-08-08-owner-review-dossier-v3.yaml"
    dossier = yaml.safe_load(path.read_text(encoding="utf-8"))
    dossier["pending_deed_decisions"][0]["owner_decision"] = "RATIFY"
    path.write_text(yaml.safe_dump(dossier, sort_keys=False), encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="must not pre-decide"):
        validate_dossier(root)
