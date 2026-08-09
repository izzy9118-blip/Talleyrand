from copy import deepcopy
from pathlib import Path
import shutil

import pytest
import yaml

from ratification_guard import (
    PASS_STATUS,
    RatificationGuardError,
    validate_decision_record,
    validate_dossier,
    validate_in_progress_record,
)


def _template():
    return yaml.safe_load(Path("ratification/owner-decision.template.yaml").read_text(encoding="utf-8"))


def _progress():
    return yaml.safe_load(Path("ratification/2026-08-08-owner-decisions-in-progress.yaml").read_text(encoding="utf-8"))


def _completed_all_ratify():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-TEST"
    record["status"] = "OWNER_DECISIONS_RECORDED"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-08"
    record["method_decision"]["decision"] = "RATIFY"
    for item in record["deed_decisions"]:
        item["decision"] = "RATIFY"
    return record


def _copy_validation_surface(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    shutil.copytree("deeds", root / "deeds")
    shutil.copytree("method", root / "method")
    shutil.copytree("ratification", root / "ratification")
    return root


def test_live_dossier_is_structurally_exact_and_nonoperative():
    result = validate_dossier(".")
    assert result["status"] == PASS_STATUS
    assert result["pending_deed_decisions"] == 21
    assert result["method_decisions"] == 1
    assert result["already_owner_ratified"] == 1


def test_owner_decision_template_cannot_claim_authority():
    result = validate_decision_record(_template(), ".", completed=False)
    assert result["completed"] is False


def test_live_incremental_record_preserves_undecided_deeds():
    result = validate_in_progress_record(_progress(), ".")
    assert result["in_progress"] is True
    assert result["decided_units"] == 1
    assert result["pending_units"] == 21
    assert _progress()["method_decision"]["decision"] == "RATIFY"
    assert all(x["decision"] == "PENDING_OWNER_RULING" for x in _progress()["deed_decisions"])


def test_in_progress_record_cannot_invent_an_owner_decision():
    record = deepcopy(_progress())
    record["method_decision"]["decision"] = "PENDING_OWNER_RULING"
    with pytest.raises(RatificationGuardError, match="at least one actual owner decision"):
        validate_in_progress_record(record, ".")


def test_in_progress_record_cannot_change_frozen_binding():
    record = deepcopy(_progress())
    record["method_decision"]["git_blob_sha1"] = "0" * 40
    with pytest.raises(RatificationGuardError, match="binding mismatch"):
        validate_in_progress_record(record, ".")


def test_completed_record_requires_explicit_owner_authority_but_structure_can_validate():
    record = _completed_all_ratify()
    result = validate_decision_record(record, ".", completed=True)
    assert result["completed"] is True
    record["owner_directive"] = ""
    with pytest.raises(RatificationGuardError, match="owner directive"):
        validate_decision_record(record, ".", completed=True)


def test_excluded_candidate_cannot_be_smuggled_into_owner_decision():
    record = _completed_all_ratify()
    record["deed_decisions"][-1]["id"] = "C5"
    with pytest.raises(RatificationGuardError, match="scope mismatch"):
        validate_decision_record(record, ".", completed=True)


def test_deed_text_change_invalidates_frozen_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/A1-read-the-designed-word.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_dossier_cannot_pre_decide_a_deed(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "ratification/2026-08-08-owner-review-dossier.yaml"
    dossier = yaml.safe_load(path.read_text(encoding="utf-8"))
    dossier["pending_deed_decisions"][0]["owner_decision"] = "RATIFY"
    path.write_text(yaml.safe_dump(dossier, sort_keys=False), encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="must not pre-decide"):
        validate_dossier(root)
