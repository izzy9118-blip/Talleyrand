#!/usr/bin/env python3
"""Structural guard for Talleyrand owner-ratification records.

Dossier v4 is the active review surface after the owner's removals of A5 and C2.
Earlier review surfaces and decision records remain historical. This guard validates
exact Git blob bindings, carried-forward owner acts, owner-removal boundaries, and
the remaining ratification scope. It never certifies historical truth or completeness.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

DOSSIER_PATH = Path("ratification/2026-08-08-owner-review-dossier-v4.yaml")
PREDECESSOR_DOSSIER_PATH = Path("ratification/2026-08-08-owner-review-dossier-v3.yaml")
PREDECESSOR_V2_DOSSIER_PATH = Path("ratification/2026-08-08-owner-review-dossier-v2.yaml")
LEGACY_DOSSIER_PATH = Path("ratification/2026-08-08-owner-review-dossier.yaml")
TEMPLATE_PATH = Path("ratification/owner-decision.v4.template.yaml")
HISTORICAL_V3_ID = "TAL-RAT-DOSSIER-2026-08-08-003"
ACTIVE_DOSSIER_ID = "TAL-RAT-DOSSIER-2026-08-08-004"
PASS_STATUS = "RATIFICATION_DOSSIER_STRUCTURAL_PASS_NOT_TRUTH_CERTIFICATION"
ALLOWED_OWNER_DECISIONS = {"RATIFY", "DECLINE", "RETURN_FOR_REVISION", "HOLD"}
PENDING_OWNER_DECISION = "PENDING_OWNER_RULING"


class RatificationGuardError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RatificationGuardError(message)


def _load_yaml(path: Path) -> dict:
    _require(path.is_file(), f"missing record: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    _require(isinstance(data, dict), f"record is not an object: {path}")
    return data


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _assert_blob(root: Path, binding: dict, label: str) -> None:
    rel = binding.get("path")
    expected = binding.get("git_blob_sha1")
    _require(isinstance(rel, str) and rel, f"{label}: missing path")
    _require(isinstance(expected, str) and len(expected) == 40, f"{label}: missing Git blob SHA-1")
    path = root / rel
    _require(path.is_file(), f"{label}: bound file missing: {rel}")
    _require(git_blob_sha1(path) == expected, f"{label}: text changed after dossier freeze: {rel}")


def _index_pending(index: dict) -> dict[str, dict]:
    deeds = index.get("deeds")
    _require(isinstance(deeds, list), "deeds/index.yaml has no deed list")
    out: dict[str, dict] = {}
    for entry in deeds:
        did = str(entry.get("id"))
        if entry.get("ratification") in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}:
            out[did] = entry
    return out


def _index_excluded(index: dict) -> set[str]:
    resolution = index.get("candidate_resolution") or {}
    excluded: set[str] = set()
    excluded.update(str(x) for x in (resolution.get("preserved_unresolved") or {}).keys())
    excluded.update(str(x) for x in (resolution.get("absorbed_not_drafted") or {}).keys())
    excluded.update(str(x) for x in (resolution.get("retired_current_formulations") or {}).keys())
    excluded.update(str(x) for x in (resolution.get("owner_removed_deeds") or {}).keys())
    excluded.update(str(x) for x in (resolution.get("held_out") or []))
    return excluded


def _dossier_excluded(dossier: dict) -> set[str]:
    groups = dossier.get("excluded_from_ratification_package") or {}
    out: set[str] = set()
    for values in groups.values():
        _require(isinstance(values, list), "dossier excluded groups must be lists")
        out.update(str(x) for x in values)
    return out


def _record_excluded(record: dict) -> set[str]:
    groups = record.get("excluded_acknowledgement") or {}
    out: set[str] = set()
    for values in groups.values():
        _require(isinstance(values, list), "owner-record excluded groups must be lists")
        out.update(str(x) for x in values)
    return out


def _removed_ids(dossier: dict) -> set[str]:
    removed = dossier.get("owner_removed_deeds") or []
    _require(isinstance(removed, list), "dossier owner_removed_deeds must be a list")
    return {str(item.get("id")) for item in removed}


def validate_dossier(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    for path, label in (
        (PREDECESSOR_DOSSIER_PATH, "predecessor v3 ratification dossier"),
        (PREDECESSOR_V2_DOSSIER_PATH, "predecessor v2 ratification dossier"),
        (LEGACY_DOSSIER_PATH, "legacy ratification dossier"),
    ):
        _require((root / path).is_file(), f"{label} missing")

    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(dossier.get("record_type") == "talleyrand_owner_ratification_dossier", "wrong dossier record_type")
    _require(dossier.get("id") == ACTIVE_DOSSIER_ID, "wrong active dossier id")
    _require(dossier.get("supersedes") == HISTORICAL_V3_ID, "active dossier must name v3 predecessor")
    _require(dossier.get("status") == "PREPARED_PENDING_OWNER_RULING", "dossier must remain pending owner ruling")
    _require(dossier.get("authority") == "NONE_BY_ITSELF", "dossier may not claim ratification authority")
    _require(dossier.get("self_certification") == "PROHIBITED", "self-certification prohibition missing")

    bindings = dossier.get("governing_bindings") or {}
    for key, label in (
        ("keel_amendment", "TAL-KEEL-AMD-001"),
        ("discovery_protocol", "TAL-DISCOVERY-001"),
        ("deep_analysis_rule", "TAL-METHOD-DEEP-ANALYSIS-001"),
        ("A2_sharpening", "TAL-DEED-A2-SHARP-001"),
        ("B1_sharpening", "TAL-DEED-B1-SHARP-001"),
        ("B2_sharpening", "TAL-DEED-B2-SHARP-001"),
        ("B3_sharpening", "TAL-DEED-B3-SHARP-001"),
        ("B4_sharpening", "TAL-DEED-B4-SHARP-001"),
        ("B6_sharpening", "TAL-DEED-B6-SHARP-001"),
        ("B7_sharpening", "TAL-DEED-B7-SHARP-001"),
        ("deed_index", "deed index"),
        ("session_sharpenings", "session sharpenings"),
        ("prior_owner_deed_decision_record", "prior owner deed decision record"),
        ("A5_owner_removal", "A5 owner removal"),
        ("C2_owner_removal", "C2 owner removal"),
    ):
        _assert_blob(root, bindings.get(key) or {}, label)

    index = _load_yaml(root / "deeds/index.yaml")
    _require(index.get("version") == "2.3.0", "active dossier requires deed corpus 2.3.0")
    pending = _index_pending(index)
    _require(len(pending) == 8, "deed corpus must contain exactly 8 pending owner decisions after C2 removal")
    live_ids = {str(x.get("id")) for x in index.get("deeds", [])}
    _require(not {"A5", "C2"}.intersection(live_ids), "owner-removed deed re-entered live deed index")
    _require(not (root / "deeds/A5-read-the-ground-beneath-the-table.md").exists(), "A5 file still exists in live tree")
    _require(not (root / "deeds/C2-strike-the-smallest-lever-that-reaches-the-center.md").exists(), "C2 file still exists in live tree")

    units = dossier.get("pending_deed_decisions")
    _require(isinstance(units, list) and len(units) == 8, "dossier must contain exactly 8 pending deed decisions")
    ids = [str(x.get("id")) for x in units]
    _require(len(ids) == len(set(ids)), "dossier contains duplicate deed decision")
    _require(set(ids) == set(pending), "dossier deed scope does not exactly match the pending corpus")
    _require(not {"A5", "C2"}.intersection(ids), "owner-removed deed entered pending ratification scope")
    for unit in units:
        did = str(unit.get("id"))
        _require(unit.get("owner_decision") == "NOT_YET_GIVEN", f"{did}: dossier must not pre-decide owner ruling")
        entry = pending[did]
        _require(unit.get("path") == f"deeds/{entry.get('file')}", f"{did}: dossier path differs from deed index")
        _require(unit.get("title") == entry.get("title"), f"{did}: dossier title differs from deed index")
        _assert_blob(root, unit, f"deed {did}")

    prior = dossier.get("prior_owner_decisions_not_reopened")
    expected_prior = {"TAL-DISCOVERY-001", "C1", "0", "A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B6", "B7"}
    _require(isinstance(prior, list) and len(prior) == len(expected_prior), "wrong carried-forward owner decision count")
    by_id = {str(x.get("id")): x for x in prior}
    _require(set(by_id) == expected_prior, "wrong carried-forward owner decision baseline")
    for item in prior:
        _require(item.get("decision") == "RATIFY", f"{item.get('id')}: prior decision not preserved as RATIFY")
        _assert_blob(root, item, f"prior owner decision {item.get('id')}")

    removed = dossier.get("owner_removed_deeds")
    _require(isinstance(removed, list) and len(removed) == 2, "dossier must preserve exactly two owner-removed deeds")
    removed_by_id = {str(x.get("id")): x for x in removed}
    _require(set(removed_by_id) == {"A5", "C2"}, "wrong owner-removed deed set")
    expected_removed = {
        "A5": ("a089840a1daa38321bb66afcd7f2f11808c72938", "delete a5"),
        "C2": ("1b926abd0162e67538c8b4fd00de7ebb495a23bb", "delete c2"),
    }
    for did, (historical_blob, directive) in expected_removed.items():
        item = removed_by_id[did]
        _require(item.get("historical_git_blob_sha1") == historical_blob, f"{did} historical blob binding changed")
        _require(item.get("disposition") == "REMOVED_FROM_LIVE_CORPUS_AND_FUTURE_RATIFICATION_SCOPE", f"{did} removal disposition changed")
        removal_path = root / item.get("removal_record", "")
        _require(removal_path.is_file(), f"{did} removal record missing")
        _require(git_blob_sha1(removal_path) == item.get("removal_record_git_blob_sha1"), f"{did} removal record binding changed")
        removal = _load_yaml(removal_path)
        _require(removal.get("owner_directive") == directive, f"{did} owner directive not preserved")
        _require((removal.get("disposition") or {}).get("live_corpus") == "REMOVED", f"{did} is not marked removed")
        _require((removal.get("disposition") or {}).get("future_owner_ratification_scope") == "EXCLUDED", f"{did} is not excluded from future ratification")

    excluded = _index_excluded(index)
    _require(excluded == _dossier_excluded(dossier), "dossier excluded set differs from deed-corpus resolution")
    _require(not excluded.intersection(ids), "excluded candidate entered ratification scope")
    _require({"A5", "C2", "C5", "C6", "C10", "D1"}.issubset(excluded), "required excluded items missing")

    return {
        "status": PASS_STATUS,
        "pending_deed_decisions": len(units),
        "prior_owner_decisions": len(prior),
        "owner_removed_deeds": len(removed),
        "excluded_candidates": len(excluded),
        "active_dossier": dossier.get("id"),
    }


def _dossier_for_record(root: Path, record: dict) -> dict:
    dossier_id = record.get("dossier_id")
    if dossier_id == ACTIVE_DOSSIER_ID:
        validate_dossier(root)
        return _load_yaml(root / DOSSIER_PATH)
    if dossier_id == HISTORICAL_V3_ID:
        validate_dossier(root)
        return _load_yaml(root / PREDECESSOR_DOSSIER_PATH)
    raise RatificationGuardError("owner decision record targets unknown dossier")


def _decision_surface(record: dict, dossier: dict) -> tuple[list, dict[str, dict], list[str]]:
    expected_units = {str(x["id"]): x for x in dossier.get("pending_deed_decisions", [])}
    deeds = record.get("deed_decisions")
    _require(isinstance(deeds, list) and len(deeds) == len(expected_units), "owner decision record must enumerate the dossier's full live pending deed scope")
    ids = [str(x.get("id")) for x in deeds]
    _require(len(ids) == len(set(ids)) and set(ids) == set(expected_units), "owner decision deed scope mismatch")
    _require(not _removed_ids(dossier).intersection(ids), "owner-removed deed entered owner decision record")
    return deeds, expected_units, ids


def _check_binding(item: dict, expected: dict, label: str) -> None:
    _require(item.get("git_blob_sha1") == expected.get("git_blob_sha1"), f"{label}: decision text binding mismatch")


def validate_decision_record(record: dict, root: str | Path = ".", *, completed: bool = False) -> dict[str, Any]:
    root = Path(root)
    dossier = _dossier_for_record(root, record)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    deeds, expected_units, ids = _decision_surface(record, dossier)

    for item in deeds:
        did = str(item.get("id"))
        _check_binding(item, expected_units[did], did)
        decision = item.get("decision")
        if completed:
            _require(decision in ALLOWED_OWNER_DECISIONS, f"{did}: completed owner decision is invalid")
        else:
            _require(decision == PENDING_OWNER_DECISION, f"{did}: template must remain pending")

    _require(not set(ids).intersection(_dossier_excluded(dossier)), "owner decision record includes excluded candidate")
    if completed:
        _require(record.get("status") == "OWNER_DECISIONS_RECORDED", "completed record has wrong status")
        _require(record.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "completed record lacks owner authority")
        _require(isinstance(record.get("owner_directive"), str) and record["owner_directive"].strip(), "completed record lacks owner directive")
        _require(isinstance(record.get("date"), str) and record["date"], "completed record lacks date")
    else:
        _require(record.get("status") == "TEMPLATE_PENDING_OWNER_DIRECTIVE", "decision template has wrong status")
        _require(record.get("authority") == "OWNER_DIRECTIVE_REQUIRED", "decision template may not claim owner authority")
        _require(record.get("owner_directive") is None, "decision template must not contain an owner directive")
        _require(_record_excluded(record) == _dossier_excluded(dossier), "template excluded acknowledgement differs from dossier")

    return {"status": PASS_STATUS, "completed": completed, "deed_decisions": len(deeds)}


def validate_in_progress_record(record: dict, root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    dossier = _dossier_for_record(root, record)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    _require(record.get("status") == "OWNER_DECISIONS_IN_PROGRESS", "in-progress record has wrong status")
    _require(record.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "in-progress record lacks owner authority")
    _require(isinstance(record.get("owner_directive"), str) and record["owner_directive"].strip(), "in-progress record lacks owner directive")
    _require(isinstance(record.get("date"), str) and record["date"], "in-progress record lacks date")

    deeds, expected_units, ids = _decision_surface(record, dossier)
    decisions = []
    for item in deeds:
        did = str(item.get("id"))
        _check_binding(item, expected_units[did], did)
        decision = item.get("decision")
        _require(decision in ALLOWED_OWNER_DECISIONS | {PENDING_OWNER_DECISION}, f"{did}: invalid in-progress decision")
        decisions.append(decision)

    _require(any(x in ALLOWED_OWNER_DECISIONS for x in decisions), "in-progress record must contain at least one actual owner decision")
    _require(any(x == PENDING_OWNER_DECISION for x in decisions), "in-progress record must leave at least one unit pending")
    _require(not set(ids).intersection(_dossier_excluded(dossier)), "owner decision record includes excluded candidate")
    _require(_record_excluded(record) == _dossier_excluded(dossier), "owner record excluded acknowledgement differs from dossier")

    return {
        "status": PASS_STATUS,
        "in_progress": True,
        "decided_units": sum(1 for x in decisions if x in ALLOWED_OWNER_DECISIONS),
        "pending_units": sum(1 for x in decisions if x == PENDING_OWNER_DECISION),
        "deed_decisions": len(deeds),
    }
