#!/usr/bin/env python3
"""Structural validation for the live Talleyrand deed corpus.

The live index contains only extant deeds. Historical and superseded material is not
part of the live deed surface. This guard validates identity, load order, file and
frontmatter binding, live ratification authority, and exclusion of unresolved,
absorbed, retired, or held-out candidates. It does not certify historical truth,
wisdom, or completeness.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import yaml

PASS_STATUS = "STRUCTURAL_DEED_CORPUS_PASS_NOT_TRUTH_CERTIFICATION"
LIVE_RATIFICATION_RECORD = Path("ratification/live-owner-ratifications.yaml")


class DeedCorpusError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DeedCorpusError(message)


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    _require(text.startswith("---\n"), f"missing YAML frontmatter: {path}")
    end = text.find("\n---\n", 4)
    _require(end != -1, f"unterminated YAML frontmatter: {path}")
    data = yaml.safe_load(text[4:end])
    _require(isinstance(data, dict), f"invalid YAML frontmatter: {path}")
    return data


def _git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _validate_live_ratification_record(root: Path, expected_ratified: set[str]) -> None:
    path = root / LIVE_RATIFICATION_RECORD
    _require(path.is_file(), "live owner-ratification record missing")
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    _require(record.get("record_type") == "talleyrand_live_owner_ratification_index", "wrong live ratification record_type")
    _require(record.get("id") == "TAL-RAT-LIVE-001", "wrong live ratification id")
    _require(record.get("status") == "ACTIVE_CARRY_FORWARD", "live ratification record is not active")
    _require(record.get("self_certification") == "PROHIBITED", "live ratification record lost self-certification prohibition")

    decisions = record.get("deed_decisions")
    _require(isinstance(decisions, list), "live ratification decisions missing")
    ids = {str(item.get("id")) for item in decisions}
    _require(ids == expected_ratified, "live ratification record does not exactly match ratified live deeds")
    for item in decisions:
        did = str(item.get("id"))
        _require(item.get("decision") == "RATIFY", f"{did}: live authority is not RATIFY")
        rel = item.get("path")
        _require(isinstance(rel, str) and rel, f"{did}: live authority path missing")
        deed_path = root / rel
        _require(deed_path.is_file(), f"{did}: live authority deed file missing")
        _require(_git_blob_sha1(deed_path) == item.get("git_blob_sha1"), f"{did}: live authority blob binding changed")

    bindings = record.get("interpretive_bindings") or []
    _require(isinstance(bindings, list), "live interpretive bindings must be a list")
    for binding in bindings:
        rel = binding.get("path")
        expected = binding.get("git_blob_sha1")
        _require(isinstance(rel, str) and rel, "interpretive binding path missing")
        bound = root / rel
        _require(bound.is_file(), f"interpretive binding missing: {rel}")
        _require(_git_blob_sha1(bound) == expected, f"interpretive binding changed: {rel}")


def validate_deed_corpus(root: str | Path = ".") -> dict:
    root = Path(root)
    index_path = root / "deeds/index.yaml"
    _require(index_path.is_file(), "deeds/index.yaml missing")
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    _require(index.get("record_type") == "talleyrand_deed_index", "wrong deed index record_type")
    _require(index.get("version") == "2.7.0", "live deed index must be version 2.7.0")
    _require(index.get("corpus") == "DEED CORPUS 2.7 LIVE-ONLY AFTER C7 RATIFICATION", "live deed corpus label changed")
    _require("owner_removal_records" not in index, "historical removal records re-entered live index")

    deeds = index.get("deeds")
    _require(isinstance(deeds, list) and deeds, "deed index must contain deeds")
    ids = [str(d.get("id")) for d in deeds]
    files = [d.get("file") for d in deeds]
    _require(len(ids) == len(set(ids)), "duplicate deed id")
    _require(len(files) == len(set(files)), "duplicate deed file")
    _require(ids[0] == "0", "Deed 0 must load first")

    counts = index.get("counts", {})
    owner_ratified = sum(1 for d in deeds if d.get("ratification") in {"OWNER_RATIFIED", "OWNER_RATIFIED_BY_RECORD"})
    pending = sum(1 for d in deeds if d.get("ratification") in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"})
    _require(counts.get("deeds") == len(deeds), "deed count mismatch")
    _require(counts.get("effective_owner_ratified") == owner_ratified, "effective owner-ratified count mismatch")
    _require(counts.get("canonical_draft_pending_ratification") == pending, "pending-ratification count mismatch")

    for entry in deeds:
        did = str(entry.get("id"))
        rel = entry.get("file")
        _require(isinstance(rel, str) and rel, f"{did}: missing file")
        path = root / "deeds" / rel
        _require(path.is_file(), f"{did}: indexed deed file missing: {rel}")
        fm = _frontmatter(path)
        _require(str(fm.get("id")) == did, f"{did}: frontmatter id mismatch")
        _require(fm.get("title") == entry.get("title"), f"{did}: frontmatter title mismatch")
        _require(fm.get("status") == entry.get("status"), f"{did}: frontmatter status mismatch")

        expected_rat = entry.get("ratification")
        actual_rat = fm.get("ratification")
        if expected_rat == "OWNER_RATIFIED_BY_RECORD":
            _require(actual_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}, f"{did}: frozen deed frontmatter must remain at reviewed pending state")
            _require(entry.get("ratification_record") == "../ratification/live-owner-ratifications.yaml", f"{did}: live deed points to a superseded ratification surface")
        elif expected_rat == "OWNER_RATIFIED":
            _require(actual_rat == "OWNER_RATIFIED", f"{did}: frontmatter ratification mismatch")
        else:
            _require(expected_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}, f"{did}: unknown ratification state")
            _require(actual_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}, f"{did}: frontmatter ratification mismatch")

    resolution = index.get("candidate_resolution", {})
    _require("owner_removed_deeds" not in resolution, "deleted-deed disposition re-entered live candidate resolution")
    excluded = set()
    excluded.update((resolution.get("preserved_unresolved") or {}).keys())
    excluded.update((resolution.get("absorbed_not_drafted") or {}).keys())
    excluded.update((resolution.get("retired_current_formulations") or {}).keys())
    excluded.update(resolution.get("held_out") or [])
    _require(not excluded.intersection(ids), f"excluded candidate entered deed corpus: {sorted(excluded.intersection(ids))}")

    indexed_files = {str(x) for x in files}
    historical_top_level = {"00-see-one-board.md"}
    discovered = {p.name for p in (root / "deeds").glob("*.md")}
    _require(discovered == indexed_files | historical_top_level, f"unindexed top-level deed file present: {sorted(discovered - indexed_files - historical_top_level)}")

    resolution_source = resolution.get("source")
    _require(isinstance(resolution_source, str) and (root / "deeds" / resolution_source).is_file(), "candidate resolution record missing")
    _require((root / "method/discovery-protocol.yaml").is_file(), "discovery protocol missing")
    _require((root / "method/deep-analysis-rule.yaml").is_file(), "deep-analysis rule missing")

    _validate_live_ratification_record(root, {str(d["id"]) for d in deeds if d.get("ratification") in {"OWNER_RATIFIED", "OWNER_RATIFIED_BY_RECORD"}})

    return {
        "status": PASS_STATUS,
        "deed_count": len(deeds),
        "effective_owner_ratified": owner_ratified,
        "pending_owner_ratification": pending,
        "excluded_candidate_count": len(excluded),
    }
