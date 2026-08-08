import copy
import pytest

from discovery_protocol import DiscoveryProtocolError, PASS_STATUS, validate_discovery_record


def base_observation():
    return {
        "observation_id": "OBS-1",
        "proposition": "A formal note records the position.",
        "evidence_class": "DF",
        "support": [
            {"source_ref": "TAL-SRC-005:p100", "independence_group": "pallain-page", "source_type": "PAGE_IMAGE_PRIMARY"}
        ],
        "channel": {
            "origin": "Talleyrand",
            "immediate_sender": "Talleyrand",
            "intermediaries": [],
            "receiver": "Louis XVIII",
            "access_state": "direct documentary access",
            "formality": "official dispatch",
        },
        "corroboration_state": "UNCORROBORATED",
        "audience": {"immediate": "Louis XVIII", "secondary": [], "true_audience_claim": False, "basis_source_refs": []},
        "disclosure_state": "FORMAL",
        "suppression": {"state": "NONE", "mechanism_source_refs": []},
        "technical_jurisdiction": {"requires_specialist": False, "competence_source_refs": []},
        "source_absence": {"state": "NONE", "negative_claim": False},
        "action_link": {"kind": "JUDGMENT", "ref": "B4", "could_change": "which channel is treated as reliable"},
    }


def record():
    return {
        "record_type": "talleyrand_discovery_record",
        "protocol": "TAL-DISCOVERY-001",
        "inquiry_id": "INQ-TEST",
        "board_frozen_before_reading": True,
        "horus_source_selection_independent": True,
        "observations": [base_observation()],
        "certification": "NONE_SELF_CERTIFICATION_PROHIBITED",
    }


def test_valid_record_passes_structural_gate_only():
    assert validate_discovery_record(record())["validation"] == PASS_STATUS


def test_repetition_from_same_chain_is_not_corroboration():
    r = record()
    o = r["observations"][0]
    o["corroboration_state"] = "CORROBORATED"
    o["support"].append({"source_ref": "TAL-SRC-006:x", "independence_group": "pallain-page", "source_type": "PRIMARY_TRANSCRIPTION"})
    with pytest.raises(DiscoveryProtocolError, match="two independent"):
        validate_discovery_record(r)


def test_self_testimony_cannot_silently_become_documented_finding():
    r = record()
    r["observations"][0]["support"] = [{"source_ref": "dispatch", "independence_group": "actor-account", "source_type": "SELF_TESTIMONY"}]
    with pytest.raises(DiscoveryProtocolError, match="self-testimony"):
        validate_discovery_record(r)


def test_documented_suppression_requires_mechanism_source():
    r = record()
    r["observations"][0]["suppression"] = {"state": "DOCUMENTED", "mechanism_source_refs": []}
    with pytest.raises(DiscoveryProtocolError, match="suppression requires"):
        validate_discovery_record(r)


def test_search_failure_cannot_become_negative_evidence():
    r = record()
    r["observations"][0]["source_absence"] = {"state": "SEARCHED_NOT_FOUND", "negative_claim": True}
    with pytest.raises(DiscoveryProtocolError, match="cannot assert absence"):
        validate_discovery_record(r)


def test_true_audience_claim_requires_ground():
    r = record()
    r["observations"][0]["audience"]["true_audience_claim"] = True
    with pytest.raises(DiscoveryProtocolError, match="true-audience"):
        validate_discovery_record(r)


def test_specialist_claim_requires_competence_ground():
    r = record()
    r["observations"][0]["technical_jurisdiction"] = {"requires_specialist": True, "competence_source_refs": []}
    with pytest.raises(DiscoveryProtocolError, match="specialist-dependent"):
        validate_discovery_record(r)


def test_documented_absence_requires_scope_and_positive_ground():
    r = record()
    r["observations"][0]["source_absence"] = {"state": "DOCUMENTED_ABSENCE", "negative_claim": True, "scope": None}
    with pytest.raises(DiscoveryProtocolError, match="requires scope"):
        validate_discovery_record(r)
