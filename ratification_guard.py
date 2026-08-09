#!/usr/bin/env python3
"""Structural guard for the live Talleyrand owner-review surface.

Only extant deeds belong to the active dossier and decision template. Superseded
review surfaces remain historical and are not part of live review. This guard never
certifies historical truth or completeness.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

DOSSIER_PATH = Path("ratification/2026-08-09-owner-review-dossier-v12.yaml")
TEMPLATE_PATH = Path("ratification/owner-decision.v12.template.yaml")
LIVE_RATIFICATION_PATH = Path("ratification/live-owner-ratifications.yaml")
ACTIVE_DOSSIER_ID = "TAL-RAT-DOSSIER-2026-08-09-012"
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
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _assert_blob(root: Path, binding: dict, label: str) -> None:
    rel = binding.get("path")
    expected = binding.get("git_blob_sha1")
    _require(isinstance(rel, str) and rel, f"{label}: missing path")
    _require(isinstance(expected, str) and len(expected) == 40, f"{label}: missing Git blob SHA-1")
    path = root / rel
    _require(path.is_file(), f"{label}: bound file missing: {rel}")
    _require(git_blob_sha1(path) == expected, f"{label}: text changed after dossier freeze: {rel}")


def _index_pending(index: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for entry in index.get("deeds") or []:
        if entry.get("ratification") in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}:
            out[str(entry.get("id"))] = entry
    return out


def _excluded(surface: dict, key: str) -> set[str]:
    groups = surface.get(key) or {}
    out: set[str] = set()
    for values in groups.values():
        _require(isinstance(values, list), f"{key} groups must be lists")
        out.update(str(x) for x in values)
    return out


def _validate_live_ratifications(root: Path) -> dict:
    record = _load_yaml(root / LIVE_RATIFICATION_PATH)
    _require(record.get("record_type") == "talleyrand_live_owner_ratification_index", "wrong live ratification record_type")
    _require(record.get("id") == "TAL-RAT-LIVE-001", "wrong live ratification id")
    _require(record.get("status") == "ACTIVE_CARRY_FORWARD", "live ratification record is not active")
    _require(record.get("self_certification") == "PROHIBITED", "live ratification record lost self-certification prohibition")

    decisions = record.get("deed_decisions")
    _require(isinstance(decisions, list) and len(decisions) == 19, "live ratification record must contain 19 ratified deeds")
    ids = [str(x.get("id")) for x in decisions]
    _require(len(ids) == len(set(ids)), "duplicate live ratification decision")
    for item in decisions:
        _require(item.get("decision") == "RATIFY", f"{item.get('id')}: live decision is not RATIFY")
        _assert_blob(root, item, f"live ratification {item.get('id')}")

    bindings = record.get("interpretive_bindings") or []
    _require(isinstance(bindings, list), "live interpretive bindings must be a list")
    by_id = {str(x.get("id")): x for x in bindings}
    for sharpening_id, deed_id in (
        ("TAL-DEED-C3-SHARP-001", "C3"),
        ("TAL-DEED-C4-SHARP-001", "C4"),
        ("TAL-DEED-C7-SHARP-001", "C7"),
        ("TAL-DEED-C8-SHARP-001", "C8"),
        ("TAL-DEED-C11-SHARP-001", "C11"),
        ("TAL-DEED-D2-SHARP-001", "D2"),
        ("TAL-DEED-D3-SHARP-001", "D3"),
    ):
        _require(sharpening_id in by_id, f"{deed_id} sharpening missing from live authority")
        _require(by_id[sharpening_id].get("deed") == deed_id, f"{deed_id} sharpening bound to wrong deed")
    for binding in bindings:
        _assert_blob(root, binding, f"interpretive binding {binding.get('id')}")
    return record


def validate_dossier(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(dossier.get("record_type") == "talleyrand_owner_ratification_dossier", "wrong dossier record_type")
    _require(dossier.get("id") == ACTIVE_DOSSIER_ID, "wrong active dossier id")
    _require(dossier.get("status") == "PREPARED_PENDING_OWNER_RULING", "dossier must remain pending owner ruling")
    _require(dossier.get("authority") == "NONE_BY_ITSELF", "dossier may not claim ratification authority")
    _require(dossier.get("self_certification") == "PROHIBITED", "self-certification prohibition missing")
    _require("owner_removed_deeds" not in dossier, "deleted-deed section re-entered active dossier")

    bindings = dossier.get("governing_bindings") or {}
    for key, label in (
        ("keel_amendment", "TAL-KEEL-AMD-001"),
        ("discovery_protocol", "TAL-DISCOVERY-001"),
        ("deep_analysis_rule", "TAL-METHOD-DEEP-ANALYSIS-001"),
        ("deed_index", "deed index"),
        ("live_owner_ratifications", "live owner ratifications"),
        ("C3_sharpening", "TAL-DEED-C3-SHARP-001"),
        ("C4_sharpening", "TAL-DEED-C4-SHARP-001"),
        ("C7_sharpening", "TAL-DEED-C7-SHARP-001"),
        ("C8_sharpening", "TAL-DEED-C8-SHARP-001"),
        ("C11_sharpening", "TAL-DEED-C11-SHARP-001"),
        ("D2_sharpening", "TAL-DEED-D2-SHARP-001"),
        ("D3_sharpening", "TAL-DEED-D3-SHARP-001"),
    ):
        _assert_blob(root, bindings.get(key) or {}, label)

    index = _load_yaml(root / "deeds/index.yaml")
    _require(index.get("version") == "2.11.0", "active dossier requires deed corpus 2.11.0")
    _require("owner_removal_records" not in index, "deleted-deed records re-entered live index")
    _require("owner_removed_deeds" not in (index.get("candidate_resolution") or {}), "deleted-deed dispositions re-entered live index")

    pending = _index_pending(index)
    _require(len(pending) == 1, "live deed corpus must contain exactly 1 pending owner decision")
    units = dossier.get("pending_deed_decisions")
    _require(isinstance(units, list) and len(units) == 1, "active dossier must contain exactly 1 pending deed decision")
    ids = [str(x.get("id")) for x in units]
    _require(len(ids) == len(set(ids)), "dossier contains duplicate deed decision")
    _require(set(ids) == set(pending), "dossier deed scope does not exactly match the live pending corpus")
    for unit in units:
        did = str(unit.get("id"))
        entry = pending[did]
        _require(unit.get("owner_decision") == "NOT_YET_GIVEN", f"{did}: dossier must not pre-decide owner ruling")
        _require(unit.get("path") == f"deeds/{entry.get('file')}", f"{did}: dossier path differs from live index")
        _require(unit.get("title") == entry.get("title"), f"{did}: dossier title differs from live index")
        _assert_blob(root, unit, f"pending deed {did}")

    live = _validate_live_ratifications(root)
    live_ids = {str(x.get("id")) for x in live["deed_decisions"]}
    prior = dossier.get("prior_owner_decisions_not_reopened")
    _require(isinstance(prior, list) and len(prior) == 20, "active dossier must carry 19 deed rulings plus discovery")
    prior_ids = {str(x.get("id")) for x in prior}
    _require(prior_ids == live_ids | {"TAL-DISCOVERY-001"}, "carried-forward owner decisions differ from live authority")
    for item in prior:
        _require(item.get("decision") == "RATIFY", f"{item.get('id')}: carried-forward decision not RATIFY")
        _assert_blob(root, item, f"carried-forward decision {item.get('id')}")

    excluded_index = set()
    resolution = index.get("candidate_resolution") or {}
    excluded_index.update(str(x) for x in (resolution.get("preserved_unresolved") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("absorbed_not_drafted") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("retired_current_formulations") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("held_out") or []))
    excluded_dossier = _excluded(dossier, "excluded_from_ratification_package")
    _require(excluded_index == excluded_dossier, "active dossier excluded set differs from live deed index")
    _require(not excluded_dossier.intersection(ids), "excluded candidate entered active ratification scope")

    return {
        "status": PASS_STATUS,
        "active_dossier": dossier.get("id"),
        "pending_deed_decisions": len(units),
        "prior_owner_decisions": len(prior),
        "live_ratified_deeds": len(live_ids),
        "excluded_candidates": len(excluded_dossier),
    }


def _decision_surface(record: dict, dossier: dict) -> tuple[list, dict[str, dict]]:
    expected = {str(x["id"]): x for x in dossier["pending_deed_decisions"]}
    deeds = record.get("deed_decisions")
    _require(isinstance(deeds, list) and len(deeds) == len(expected), "owner decision record must enumerate the active pending scope")
    ids = [str(x.get("id")) for x in deeds]
    _require(len(ids) == len(set(ids)) and set(ids) == set(expected), "owner decision deed scope mismatch")
    return deeds, expected


def validate_decision_record(record: dict, root: str | Path = ".", *, completed: bool = False) -> dict[str, Any]:
    root = Path(root)
    validate_dossier(root)
    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    _require(record.get("dossier_id") == ACTIVE_DOSSIER_ID, "owner decision record targets wrong active dossier")
    deeds, expected = _decision_surface(record, dossier)

    for item in deeds:
        did = str(item.get("id"))
        _require(item.get("git_blob_sha1") == expected[did].get("git_blob_sha1"), f"{did}: decision text binding mismatch")
        decision = item.get("decision")
        if completed:
            _require(decision in ALLOWED_OWNER_DECISIONS, f"{did}: completed owner decision is invalid")
        else:
            _require(decision == PENDING_OWNER_DECISION, f"{did}: template must remain pending")

    _require(not {str(x.get("id")) for x in deeds}.intersection(_excluded(dossier, "excluded_from_ratification_package")), "owner decision record includes excluded candidate")
    if completed:
        _require(record.get("status") == "OWNER_DECISIONS_RECORDED", "completed record has wrong status")
        _require(record.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "completed record lacks owner authority")
        _require(isinstance(record.get("owner_directive"), str) and record["owner_directive"].strip(), "completed record lacks owner directive")
        _require(isinstance(record.get("date"), str) and record["date"], "completed record lacks date")
    else:
        _require(record.get("status") == "TEMPLATE_PENDING_OWNER_DIRECTIVE", "decision template has wrong status")
        _require(record.get("authority") == "OWNER_DIRECTIVE_REQUIRED", "decision template may not claim owner authority")
        _require(record.get("owner_directive") is None, "decision template must not contain owner directive")
        _require(_excluded(record, "excluded_acknowledgement") == _excluded(dossier, "excluded_from_ratification_package"), "template excluded acknowledgement differs from dossier")

    return {"status": PASS_STATUS, "completed": completed, "deed_decisions": len(deeds)}


def validate_in_progress_record(record: dict, root: str | Path = ".") -> dict[str, Any]:
    """Validate current records; tolerate historical records for regression tests only."""
    root = Path(root)
    if record.get("dossier_id") != ACTIVE_DOSSIER_ID:
        live = _validate_live_ratifications(root)
        live_by_id = {str(x["id"]): x for x in live["deed_decisions"]}
        decisions = record.get("deed_decisions") or []
        for item in decisions:
            did = str(item.get("id"))
            if item.get("decision") == "RATIFY" and did in live_by_id:
                _require(item.get("git_blob_sha1") == live_by_id[did].get("git_blob_sha1"), f"{did}: historical ratification disagrees with live authority")
        return {
            "status": PASS_STATUS,
            "in_progress": True,
            "decided_units": sum(1 for x in decisions if x.get("decision") in ALLOWED_OWNER_DECISIONS),
            "pending_units": sum(1 for x in decisions if x.get("decision") == PENDING_OWNER_DECISION),
            "deed_decisions": len(decisions),
            "historical_surface": True,
        }

    validate_dossier(root)
    dossier = _load_yaml(root / DOSSIER_PATH)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    _require(record.get("status") == "OWNER_DECISIONS_IN_PROGRESS", "in-progress record has wrong status")
    _require(record.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "in-progress record lacks owner authority")
    _require(isinstance(record.get("owner_directive"), str) and record["owner_directive"].strip(), "in-progress record lacks owner directive")
    deeds, expected = _decision_surface(record, dossier)
    decisions = []
    for item in deeds:
        did = str(item.get("id"))
        _require(item.get("git_blob_sha1") == expected[did].get("git_blob_sha1"), f"{did}: decision text binding mismatch")
        decision = item.get("decision")
        _require(decision in ALLOWED_OWNER_DECISIONS | {PENDING_OWNER_DECISION}, f"{did}: invalid in-progress decision")
        decisions.append(decision)
    _require(any(x in ALLOWED_OWNER_DECISIONS for x in decisions), "in-progress record must contain at least one owner decision")
    _require(any(x == PENDING_OWNER_DECISION for x in decisions), "in-progress record must leave at least one unit pending")
    return {
        "status": PASS_STATUS,
        "in_progress": True,
        "decided_units": sum(1 for x in decisions if x in ALLOWED_OWNER_DECISIONS),
        "pending_units": sum(1 for x in decisions if x == PENDING_OWNER_DECISION),
        "deed_decisions": len(deeds),
    }
