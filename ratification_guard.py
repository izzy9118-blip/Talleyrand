#!/usr/bin/env python3
"""Structural guard for the closed Talleyrand owner-ratification surface.

All live deeds are exact-bound to owner decisions. Historical dossiers and templates
remain readable but are not active review surfaces. This guard never certifies
historical truth, completeness, voice, runtime, or minister establishment.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

CLOSURE_PATH = Path("ratification/2026-08-09-owner-ratification-closure-v13.yaml")
FINAL_DOSSIER_PATH = Path("ratification/2026-08-09-owner-review-dossier-v12.yaml")
TEMPLATE_PATH = Path("ratification/owner-decision.v12.template.yaml")
LIVE_RATIFICATION_PATH = Path("ratification/live-owner-ratifications.yaml")
CLOSURE_ID = "TAL-RAT-CLOSURE-2026-08-09-013"
FINAL_DOSSIER_ID = "TAL-RAT-DOSSIER-2026-08-09-012"
PASS_STATUS = "RATIFICATION_CLOSURE_STRUCTURAL_PASS_NOT_TRUTH_CERTIFICATION"
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
    _require(isinstance(decisions, list) and len(decisions) == 20, "live ratification record must contain 20 ratified deeds")
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
        ("TAL-DEED-D4-SHARP-001", "D4"),
    ):
        _require(sharpening_id in by_id, f"{deed_id} sharpening missing from live authority")
        _require(by_id[sharpening_id].get("deed") == deed_id, f"{deed_id} sharpening bound to wrong deed")
    for binding in bindings:
        _assert_blob(root, binding, f"interpretive binding {binding.get('id')}")
    return record


def validate_dossier(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    closure = _load_yaml(root / CLOSURE_PATH)
    _require(closure.get("record_type") == "talleyrand_owner_ratification_closure", "wrong closure record_type")
    _require(closure.get("id") == CLOSURE_ID, "wrong ratification closure id")
    _require(closure.get("status") == "CLOSED_ALL_LIVE_DEEDS_OWNER_RATIFIED", "ratification review is not closed")
    _require(closure.get("authority") == "REPOSITORY_OWNER_DECISIONS_CARRIED_FORWARD", "closure authority is wrong")
    _require(closure.get("self_certification") == "PROHIBITED", "self-certification prohibition missing")
    _require("owner_removed_deeds" not in closure, "deleted-deed section re-entered closure")

    bindings = closure.get("governing_bindings") or {}
    for key, label in (
        ("keel_amendment", "TAL-KEEL-AMD-001"),
        ("discovery_protocol", "TAL-DISCOVERY-001"),
        ("deep_analysis_rule", "TAL-METHOD-DEEP-ANALYSIS-001"),
        ("deed_index", "deed index"),
        ("live_owner_ratifications", "live owner ratifications"),
        ("final_owner_act", "final D4 owner act"),
        ("C3_sharpening", "TAL-DEED-C3-SHARP-001"),
        ("C4_sharpening", "TAL-DEED-C4-SHARP-001"),
        ("C7_sharpening", "TAL-DEED-C7-SHARP-001"),
        ("C8_sharpening", "TAL-DEED-C8-SHARP-001"),
        ("C11_sharpening", "TAL-DEED-C11-SHARP-001"),
        ("D2_sharpening", "TAL-DEED-D2-SHARP-001"),
        ("D3_sharpening", "TAL-DEED-D3-SHARP-001"),
        ("D4_sharpening", "TAL-DEED-D4-SHARP-001"),
    ):
        _assert_blob(root, bindings.get(key) or {}, label)

    index = _load_yaml(root / "deeds/index.yaml")
    _require(index.get("version") == "2.12.0", "closure requires deed corpus 2.12.0")
    _require((index.get("status") or {}).get("ratification") == "ALL_LIVE_DEEDS_OWNER_RATIFIED", "deed index is not closed")
    _require("owner_removal_records" not in index, "deleted-deed records re-entered live index")
    _require("owner_removed_deeds" not in (index.get("candidate_resolution") or {}), "deleted-deed dispositions re-entered live index")

    pending = _index_pending(index)
    _require(not pending, "closed deed corpus contains a pending owner decision")
    units = closure.get("pending_deed_decisions")
    _require(isinstance(units, list) and not units, "closure must contain zero pending deed decisions")

    live = _validate_live_ratifications(root)
    live_ids = {str(x.get("id")) for x in live["deed_decisions"]}
    indexed_ids = {str(x.get("id")) for x in (index.get("deeds") or [])}
    _require(live_ids == indexed_ids and len(live_ids) == 20, "live authority does not exactly cover indexed deeds")
    ratified = closure.get("ratified_deed_decisions")
    _require(isinstance(ratified, list) and len(ratified) == 20, "closure must carry exactly 20 deed decisions")
    ratified_ids = [str(x.get("id")) for x in ratified]
    _require(len(ratified_ids) == len(set(ratified_ids)), "closure contains duplicate deed decision")
    _require(set(ratified_ids) == live_ids, "closure decisions differ from live authority")
    for item in ratified:
        _require(item.get("decision") == "RATIFY", f"{item.get('id')}: closure decision not RATIFY")
        _assert_blob(root, item, f"closure decision {item.get('id')}")

    final = _load_yaml(root / bindings["final_owner_act"]["path"])
    _require(final.get("record_type") == "talleyrand_owner_ratification_record", "final owner act has wrong record_type")
    _require(final.get("dossier_id") == FINAL_DOSSIER_ID, "final owner act targets wrong dossier")
    _require(final.get("status") == "OWNER_DECISIONS_RECORDED", "final owner act is not completed")
    _require(final.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", "final owner act lacks owner authority")
    final_decisions = final.get("deed_decisions") or []
    _require(len(final_decisions) == 1 and str(final_decisions[0].get("id")) == "D4", "final owner act must decide only D4")
    _require(final_decisions[0].get("decision") == "RATIFY", "final D4 decision is not RATIFY")
    _require(final_decisions[0].get("git_blob_sha1") == next(x["git_blob_sha1"] for x in ratified if str(x["id"]) == "D4"), "final D4 binding differs from closure")

    excluded_index = set()
    resolution = index.get("candidate_resolution") or {}
    excluded_index.update(str(x) for x in (resolution.get("preserved_unresolved") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("absorbed_not_drafted") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("retired_current_formulations") or {}).keys())
    excluded_index.update(str(x) for x in (resolution.get("held_out") or []))
    excluded_closure = _excluded(closure, "excluded_from_ratification_package")
    _require(excluded_index == excluded_closure, "closure excluded set differs from live deed index")
    _require(not excluded_closure.intersection(live_ids), "excluded candidate entered ratified deed set")

    return {
        "status": PASS_STATUS,
        "closure": closure.get("id"),
        "active_dossier": None,
        "pending_deed_decisions": 0,
        "ratified_deed_decisions": len(ratified),
        "live_ratified_deeds": len(live_ids),
        "excluded_candidates": len(excluded_closure),
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
    dossier = _load_yaml(root / FINAL_DOSSIER_PATH)
    _require(record.get("record_type") == "talleyrand_owner_ratification_record", "wrong owner decision record_type")
    _require(record.get("dossier_id") == FINAL_DOSSIER_ID, "owner decision record targets wrong final dossier")
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
    """Reject a false final in-progress surface; tolerate earlier historical records."""
    root = Path(root)
    if record.get("dossier_id") != FINAL_DOSSIER_ID:
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

    if record.get("status") == "OWNER_DECISIONS_RECORDED":
        result = validate_decision_record(record, root, completed=True)
        return {**result, "completed_surface": True, "decided_units": len(record.get("deed_decisions") or []), "pending_units": 0}

    validate_dossier(root)
    dossier = _load_yaml(root / FINAL_DOSSIER_PATH)
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
