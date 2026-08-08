#!/usr/bin/env python3
"""Executable structural guard for TAL-DISCOVERY-001.

This validator checks provenance/channel discipline only. It never certifies that
an observation is true, wise, complete, or correctly interpreted.
"""
from __future__ import annotations

import copy

PROTOCOL_ID = "TAL-DISCOVERY-001"
PASS_STATUS = "STRUCTURAL_DISCOVERY_PROTOCOL_PASS_NOT_TRUTH_CERTIFICATION"
CERTIFICATION = "NONE_SELF_CERTIFICATION_PROHIBITED"

EVIDENCE_CLASSES = {"DF", "HT", "SI", "WH", "UU", "V", "ED-PRIMARY"}
SOURCE_TYPES = {
    "PAGE_IMAGE_PRIMARY", "PRIMARY_TRANSCRIPTION", "DIRECT_WITNESS",
    "ATTRIBUTED_REPORT", "SELF_TESTIMONY", "RUMOR",
    "EDITORIAL_TRANSMISSION", "DERIVATIVE_ACCOUNT",
}
CORROBORATION = {"UNCORROBORATED", "PARTIALLY_CORROBORATED", "CORROBORATED", "CONTRADICTED"}
SUPPRESSION = {"NONE", "ALLEGED", "DOCUMENTED"}
DISCLOSURE = {"PUBLIC", "FORMAL", "CONFIDENTIAL", "PRIVATE", "WITHHELD", "SELECTIVELY_DISCLOSED", "NOT_YET_DISCLOSED"}
ABSENCE = {"NONE", "NOT_SEARCHED", "SEARCHED_NOT_FOUND", "SOURCE_EXISTS_NOT_ACQUIRED", "SOURCE_ACQUIRED_INCOMPLETE", "DOCUMENTED_ABSENCE"}
UNRESOLVED_ABSENCE = {"NOT_SEARCHED", "SEARCHED_NOT_FOUND", "SOURCE_EXISTS_NOT_ACQUIRED", "SOURCE_ACQUIRED_INCOMPLETE"}
QUALIFYING_INDEPENDENT_TYPES = {"PAGE_IMAGE_PRIMARY", "PRIMARY_TRANSCRIPTION", "DIRECT_WITNESS", "ATTRIBUTED_REPORT", "EDITORIAL_TRANSMISSION"}


class DiscoveryProtocolError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiscoveryProtocolError(message)


def _has_independent_qualifying_support(support: list[dict], excluded_types: set[str]) -> bool:
    excluded_groups = {item["independence_group"] for item in support if item["source_type"] in excluded_types}
    return any(
        item["source_type"] in QUALIFYING_INDEPENDENT_TYPES
        and item["independence_group"] not in excluded_groups
        for item in support
    )


def validate_discovery_record(record: dict) -> dict:
    _require(isinstance(record, dict), "discovery record must be an object")
    _require(record.get("record_type") == "talleyrand_discovery_record", "wrong record_type")
    _require(record.get("protocol") == PROTOCOL_ID, "wrong discovery protocol")
    _require(record.get("certification") == CERTIFICATION, "self-certification is prohibited")
    _require(record.get("board_frozen_before_reading") is True, "board must be frozen before reading")
    _require(record.get("horus_source_selection_independent") is True, "Horus source-selection independence must be preserved")

    observations = record.get("observations")
    _require(isinstance(observations, list) and observations, "observations must be non-empty")
    seen = set()

    for index, obs in enumerate(observations):
        label = f"observations[{index}]"
        _require(isinstance(obs, dict), f"{label} must be an object")
        oid = obs.get("observation_id")
        _require(isinstance(oid, str) and oid, f"{label}.observation_id missing")
        _require(oid not in seen, f"duplicate observation_id: {oid}")
        seen.add(oid)
        _require(isinstance(obs.get("proposition"), str) and obs["proposition"].strip(), f"{label}.proposition missing")
        evidence_class = obs.get("evidence_class")
        _require(evidence_class in EVIDENCE_CLASSES, f"{label}.evidence_class invalid")

        support = obs.get("support")
        _require(isinstance(support, list) and support, f"{label}.support must be non-empty")
        source_refs, groups, types = set(), set(), set()
        for sidx, item in enumerate(support):
            _require(isinstance(item, dict), f"{label}.support[{sidx}] must be an object")
            ref = item.get("source_ref")
            group = item.get("independence_group")
            stype = item.get("source_type")
            _require(isinstance(ref, str) and ref, f"{label}.support[{sidx}].source_ref missing")
            _require(isinstance(group, str) and group, f"{label}.support[{sidx}].independence_group missing")
            _require(stype in SOURCE_TYPES, f"{label}.support[{sidx}].source_type invalid")
            source_refs.add(ref)
            groups.add(group)
            types.add(stype)

        channel = obs.get("channel")
        _require(isinstance(channel, dict), f"{label}.channel missing")
        for field in ("origin", "immediate_sender", "receiver", "access_state", "formality"):
            _require(isinstance(channel.get(field), str) and channel[field], f"{label}.channel.{field} missing")
        _require(isinstance(channel.get("intermediaries"), list), f"{label}.channel.intermediaries must be a list")

        corroboration = obs.get("corroboration_state")
        _require(corroboration in CORROBORATION, f"{label}.corroboration_state invalid")
        if corroboration == "CORROBORATED":
            _require(len(groups) >= 2, f"{label}: corroborated requires two independent provenance groups")

        if evidence_class == "DF" and "RUMOR" in types:
            _require(_has_independent_qualifying_support(support, {"RUMOR", "DERIVATIVE_ACCOUNT"}), f"{label}: rumor cannot become DF without qualifying independent ground")
        if evidence_class == "DF" and "SELF_TESTIMONY" in types:
            _require(_has_independent_qualifying_support(support, {"SELF_TESTIMONY", "RUMOR", "DERIVATIVE_ACCOUNT"}), f"{label}: self-testimony cannot become DF without independent qualifying ground")

        audience = obs.get("audience")
        _require(isinstance(audience, dict) and isinstance(audience.get("immediate"), str) and audience["immediate"], f"{label}.audience missing")
        _require(isinstance(audience.get("secondary"), list), f"{label}.audience.secondary must be a list")
        true_claim = audience.get("true_audience_claim") is True
        basis = audience.get("basis_source_refs", [])
        _require(isinstance(basis, list), f"{label}.audience.basis_source_refs must be a list")
        if true_claim:
            _require(bool(basis), f"{label}: true-audience claim requires source ground")
            _require(set(basis).issubset(source_refs), f"{label}: audience basis must resolve to support")

        _require(obs.get("disclosure_state") in DISCLOSURE, f"{label}.disclosure_state invalid")

        suppression = obs.get("suppression")
        _require(isinstance(suppression, dict) and suppression.get("state") in SUPPRESSION, f"{label}.suppression invalid")
        mechanism_refs = suppression.get("mechanism_source_refs", [])
        _require(isinstance(mechanism_refs, list), f"{label}.suppression.mechanism_source_refs must be a list")
        if suppression["state"] == "DOCUMENTED":
            _require(bool(mechanism_refs), f"{label}: documented suppression requires mechanism sources")
            _require(set(mechanism_refs).issubset(source_refs), f"{label}: suppression mechanism must resolve to support")

        technical = obs.get("technical_jurisdiction")
        _require(isinstance(technical, dict) and isinstance(technical.get("requires_specialist"), bool), f"{label}.technical_jurisdiction invalid")
        competence_refs = technical.get("competence_source_refs", [])
        _require(isinstance(competence_refs, list), f"{label}.technical_jurisdiction.competence_source_refs must be a list")
        if technical["requires_specialist"]:
            _require(bool(competence_refs), f"{label}: specialist-dependent claim requires competent ground")
            _require(set(competence_refs).issubset(source_refs), f"{label}: competence refs must resolve to support")

        absence = obs.get("source_absence")
        _require(isinstance(absence, dict) and absence.get("state") in ABSENCE, f"{label}.source_absence invalid")
        negative_claim = absence.get("negative_claim")
        _require(isinstance(negative_claim, bool), f"{label}.source_absence.negative_claim must be boolean")
        if absence["state"] in UNRESOLVED_ABSENCE:
            _require(negative_claim is False, f"{label}: unresolved search state cannot assert absence")
        if absence["state"] == "DOCUMENTED_ABSENCE":
            _require(negative_claim is True, f"{label}: documented absence must be an explicit scoped negative claim")
            _require(isinstance(absence.get("scope"), str) and absence["scope"].strip(), f"{label}: documented absence requires scope")
            _require(bool(source_refs), f"{label}: documented absence requires positive source ground")

        action = obs.get("action_link")
        _require(isinstance(action, dict), f"{label}.action_link missing")
        _require(action.get("kind") in {"JUDGMENT", "DEED", "QUERY", "DECISION", "ARCHIVE_ONLY"}, f"{label}.action_link.kind invalid")
        _require(isinstance(action.get("could_change"), str) and action["could_change"].strip(), f"{label}.action_link.could_change missing")

    out = copy.deepcopy(record)
    out["validation"] = PASS_STATUS
    return out
