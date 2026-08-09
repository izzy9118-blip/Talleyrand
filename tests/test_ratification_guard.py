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
    return yaml.safe_load(Path("ratification/owner-decision.v2.template.yaml").read_text(encoding="utf-8"))


def _live_progress():
    return yaml.safe_load(
        Path("ratification/2026-08-08-owner-deed-decisions-v2-in-progress.yaml").read_text(encoding="utf-8")
    )


def _progress_with_deed0_ratified():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V2-TEST"
    record["status"] = "OWNER_DECISIONS_IN_PROGRESS"
    record["authority"] = "REPOSITORY_OWNER_DIRECTIVE"
    record["owner_directive"] = "Test fixture only; not an actual owner ratification."
    record["date"] = "2026-08-08"
    record["deed_decisions"][0]["decision"] = "RATIFY"
    return record


def _completed_all_ratify():
    record = deepcopy(_template())
    record["id"] = "TAL-RAT-OWNER-DECISION-V2-COMPLETE-TEST"
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


def test_live_dossier_is_v2_exact_and_nonoperative():
    result = validate_dossier(".")
    assert result["status"] == PASS_STATUS
    assert result["active_dossier"] == "TAL-RAT-DOSSIER-2026-08-08-002"
    assert result["pending_deed_decisions"] == 21
    assert result["prior_owner_decisions"] == 2


def test_old_and_new_deed0_are_both_preserved_but_only_new_is_active():
    assert Path("deeds/00-see-one-board.md").is_file()
    assert Path("deeds/00-see-the-connected-boards.md").is_file()
    dossier = yaml.safe_load(Path("ratification/2026-08-08-owner-review-dossier-v2.yaml").read_text(encoding="utf-8"))
    deed0 = dossier["pending_deed_decisions"][0]
    assert deed0["title"] == "SEE THE CONNECTED BOARDS"
    assert deed0["git_blob_sha1"] == "208216723993d6103fb4ddbc9f96d0cea2e63228"
    assert deed0["supersedes_review_binding"]["git_blob_sha1"] == "1700193646bc6f2cd5fa9661cb521eb671949e9e"


def test_connected_boards_keel_amendment_is_owner_ratified_without_rewriting_keel():
    amendment = yaml.safe_load(Path("amendments/2026-08-08-connected-boards-keel-amendment.md").read_text(encoding="utf-8").split("---\n", 2)[1])
    assert amendment["id"] == "TAL-KEEL-AMD-001"
    assert amendment["status"] == "OWNER_RATIFIED"
    assert amendment["amends_principle"] == 6


def test_owner_decision_v2_template_cannot_claim_authority():
    result = validate_decision_record(_template(), ".", completed=False)
    assert result["completed"] is False
    assert result["deed_decisions"] == 21


def test_live_owner_record_ratifies_only_revised_deed0():
    record = _live_progress()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 1
    assert result["pending_units"] == 20
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    assert by_id["0"] == "RATIFY"
    assert all(decision == "PENDING_OWNER_RULING" for did, decision in by_id.items() if did != "0")
    assert "do it" in record["owner_directive"]


def test_incremental_v2_record_can_decide_one_deed_without_inventing_others():
    record = _progress_with_deed0_ratified()
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 1
    assert result["pending_units"] == 20


def test_in_progress_record_cannot_change_revised_deed0_binding():
    record = deepcopy(_live_progress())
    record["deed_decisions"][0]["git_blob_sha1"] = "1700193646bc6f2cd5fa9661cb521eb671949e9e"
    with pytest.raises(RatificationGuardError, match="binding mismatch"):
        validate_in_progress_record(record, ".")


def test_live_record_cannot_invent_second_owner_decision():
    record = deepcopy(_live_progress())
    record["deed_decisions"][1]["decision"] = "RATIFY"
    result = validate_in_progress_record(record, ".")
    assert result["decided_units"] == 2
    # Structural validity alone does not create authority for that second decision;
    # the committed live record is the documentary owner act and must remain exact.
    assert _live_progress()["deed_decisions"][1]["decision"] == "PENDING_OWNER_RULING"


def test_completed_record_requires_explicit_owner_authority():
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


def test_deed_text_change_invalidates_active_dossier(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "deeds/00-see-the-connected-boards.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nunauthorized drift\n", encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="text changed after dossier freeze"):
        validate_dossier(root)


def test_dossier_cannot_pre_decide_revised_deed0(tmp_path):
    root = _copy_validation_surface(tmp_path)
    path = root / "ratification/2026-08-08-owner-review-dossier-v2.yaml"
    dossier = yaml.safe_load(path.read_text(encoding="utf-8"))
    dossier["pending_deed_decisions"][0]["owner_decision"] = "RATIFY"
    path.write_text(yaml.safe_dump(dossier, sort_keys=False), encoding="utf-8")
    with pytest.raises(RatificationGuardError, match="must not pre-decide"):
        validate_dossier(root)
