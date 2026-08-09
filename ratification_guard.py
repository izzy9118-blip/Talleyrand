#!/usr/bin/env python3
"""Structural guard for Talleyrand owner-ratification records.

The guard freezes exact text by Git blob identity and enforces the boundary between
ratifiable deeds and unresolved/absorbed/retired ore. It never decides whether a
deed should be ratified and never certifies historical truth or completeness.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

DOSSIER_PATH = Path("ratification/2026-08-08-owner-review-dossier.yaml")
TEMPLATE_PATH = Path("ratification/owner-decision.template.yaml")
PASS_STATUS = "RATIFICATION_DOSSIER_STRUCTURAL_PASS_NOT_TRUTH_CERTIFICATION"
ALLOWED_OWNER_DECISIONS = {"RATIFY", "DECLINE", "RETURN_FOR_REVISION", "HOLD"}


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
    actual = git_blob_sha1(path)
    _require(actual == expected, f"{label}: text changed after dossier freeze: {rel}")


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
    excluded.update(str(x) for x in (resolution.get("held_out") or []))
    return excluded


def _dossier_excluded(dossier: dict) -> set[str]:
    groups = dossier.get("excluded_from_ratification_package") or {}
    out: set[str] = set()
    for values in groups.values():
        _require(isinstance(values, list), "dossier excluded groups must be lists")
        out.update(str(x) for x in values)
    return out


def validate_dossier(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(dossier.get("record_type") == "talleyrand_owner_ratification_dossier", "wrong dossier record_type")
    _require(dossier.get("status") == "PREPARED_PENDING_OWNER_RULING", "dossier must remain pending owner ruling")
    _require(dossier.get("authority") == "NONE_BY_ITSELF", "dossier may not claim ratification authority")
    _require(dossier.get("self_certification") == "PROHIBITED", "self-certification prohibition missing")

    bindings = dossier.get("governing_bindings") or {}
    _assert_blob(root, bindings.get("deed_index") or {}, "deed index")
    _assert_blob(root, bindings.get("session_sharpenings") or {}, "session sharpenings")

    index = _load_yaml(root / "deeds/index.yaml")
    _require(index.get("version") == "2.0.0", "ratification dossier is for deed corpus 2.0.0 only")
    pending = _index_pending(index)
    _require(len(pending) == 21, "deed corpus must contain exactly 21 pending owner decisions")

    units = dossier.get("pending_deed_decisions")
    _require(isinstance(units, list) and len(units) == 21, "dossier must contain exactly 21 pending deed decisions")
    ids = [str(x.get("id")) for x in units]
    _require(len(ids) == len(set(ids)), "dossier contains duplicate deed decision")
    _require(set(ids) == set(pending), "dossier deed scope does not exactly match the pending corpus")

    for unit in units:
        did = str(unit.get("id"))
        _require(unit.get("owner_decision") == "NOT_YET_GIVEN", f"{did}: dossier must not pre-decide owner ruling")
        entry = pending[did]
        expected_path = f"deeds/{entry.get('file')}"
        _require(unit.get("path") == expected_path, f"{did}: dossier path differs from deed index")
        _require(unit.get("title") == entry.get("title"), f"{did}: dossier title differs from deed index")
        _assert_blob(root, unit, f"deed {did}")

    method = dossier.get("method_decision") or {}
    _require(method.get("id") == "TAL-DISCOVERY-001", "discovery protocol decision missing")
    _require(method.get("owner_decision") == "NOT_YET_GIVEN", "dossier must not pre-ratify discovery protocol")
    _assert_blob(root, method, "TAL-DISCOVERY-001")
    discovery = _load_yaml(root / method["path"])
    _require(discovery.get("status") == "PROPOSED_PENDING_OWNER_RATIFICATION", "discovery protocol is not pending owner ratification")

    already = dossier.get("already_ratified_not_reopened")
    _require(isinstance(already, list) and len(already) == 1, "C1 must be the sole already-ratified baseline")
    c1 = already[0]
    _require(str(c1.get("id")) == "C1" and c1.get("status") == "OWNER_RATIFIED", "C1 baseline is wrong")
    _assert_blob(root, c1, "C1 baseline")

    excluded = _index_excluded(index)
    dossier_excluded = _dossier_excluded(dossier)
    _require(excluded == dossier_excluded, "dossier excluded set differs from deed-corpus resolution")
    _require(not excluded.intersection(ids), "excluded candidate entered ratification scope")
    _require("C5" in excluded and "C6" in excluded, "self-testimonial C5/C6 must remain excluded")
    _require("C10" in excluded and "D1" in excluded, "retired formulations must remain excluded")

    b3 = next(x for x in units if str(x.get("id")) == "B3")
    _require((b3.get("includes_sharpening") or {}).get("component") == "B3 capacity-pricing requirement", "B3 sharpening not bound")
    _require((method.get("includes_sharpening") or {}).get("component") == "discovery protocol precondition 1", "discovery sharpening not bound")

    return {
        "status": PASS_STATUS,
        "pending_deed_decisions": len(units),
        "method_decisions": 1,
        "already_owner_ratified": 1,
        "excluded_candidates": len(excluded),
    }


def validate_decision_record(record: dict, root: str | Path = ".", *, completed: bool = False) -> dict[str, Any]:
    root = Path(root)
    validate_dossier(root)
    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    _require(record.get("dossier_id") == dossier.get("id"), "owner decision record targets wrong dossier")

    method = record.get("method_decision") or {}
    deeds = record.get("deed_decisions")
    _require(isinstance(deeds, list) and len(deeds) == 21, "owner decision record must enumerate all 21 deed units")
    expected_units = {str(x["id"]): x for x in dossier["pending_deed_decisions"]}
    ids = [str(x.get("id")) for x in deeds]
    _require(len(ids) == len(set(ids)) and set(ids) == set(expected_units), "owner decision deed scope mismatch")

    def check_decision(item: dict, expected: dict, label: str) -> None:
        _require(item.get("git_blob_sha1") == expected.get("git_blob_sha1"), f"{label}: decision text binding mismatch")
        decision = item.get("decision")
        if completed:
            _require(decision in ALLOWED_OWNER_DECISIONS, f"{label}: completed owner decision is invalid")
        else:
            _require(decision == "PENDING_OWNER_RULING", f"{label}: template must remain pending")

    check_decision(method, dossier["method_decision"], "TAL-DISCOVERY-001")
    for item in deeds:
        did = str(item.get("id"))
        check_decision(item, expected_units[did], did)

    decision_ids = set(ids)
    _require(not decision_ids.intersection(_dossier_excluded(dossier)), "owner decision record includes excluded candidate")

    if completed:
        _require(record.get("status") == "OWNER_DECISIONS_RECORDED", "completed record has wrong status")
        _require(record.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "completed record lacks owner authority")
        _require(isinstance(record.get("owner_directive"), str) and record["owner_directive"].strip(), "completed record lacks owner directive")
    else:
        _require(record.get("status") == "TEMPLATE_PENDING_OWNER_DIRECTIVE", "decision template has wrong status")
        _require(record.get("authority") == "OWNER_DIRECTIVE_REQUIRED", "decision template may not claim owner authority")
        _require(record.get("owner_directive") is None, "decision template must not contain an owner directive")

    return {"status": PASS_STATUS, "completed": completed, "deed_decisions": len(deeds), "method_decisions": 1}
