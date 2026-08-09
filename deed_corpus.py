#!/usr/bin/env python3
"""Structural validation for the Talleyrand deed corpus.

This validates repository identity, load-order records, file/frontmatter binding,
and exclusion of unresolved/retired/owner-removed candidates. It does not certify
historical truth, wisdom, or completeness.
"""
from __future__ import annotations

from pathlib import Path
import yaml

PASS_STATUS = "STRUCTURAL_DEED_CORPUS_PASS_NOT_TRUTH_CERTIFICATION"


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


def validate_deed_corpus(root: str | Path = ".") -> dict:
    root = Path(root)
    index_path = root / "deeds/index.yaml"
    _require(index_path.is_file(), "deeds/index.yaml missing")
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    _require(index.get("record_type") == "talleyrand_deed_index", "wrong deed index record_type")
    _require(index.get("version") == "2.3.0", "live deed index must be version 2.3.0")
    deeds = index.get("deeds")
    _require(isinstance(deeds, list) and deeds, "deed index must contain deeds")

    ids = [str(d.get("id")) for d in deeds]
    files = [d.get("file") for d in deeds]
    _require(len(ids) == len(set(ids)), "duplicate deed id")
    _require(len(files) == len(set(files)), "duplicate deed file")
    _require(ids[0] == "0", "Deed 0 must load first")
    _require(not {"A5", "C2"}.intersection(ids), "owner-removed deed re-entered live deed corpus")

    counts = index.get("counts", {})
    owner_ratified = sum(
        1 for d in deeds if d.get("ratification") in {"OWNER_RATIFIED", "OWNER_RATIFIED_BY_RECORD"}
    )
    pending = sum(
        1 for d in deeds if d.get("ratification") in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"}
    )
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
            _require(
                actual_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"},
                f"{did}: frozen deed frontmatter must remain at its reviewed pending state",
            )
            record = entry.get("ratification_record")
            _require(isinstance(record, str) and record, f"{did}: by-record ratification lacks record")
            _require((root / "deeds" / record).resolve().is_file(), f"{did}: ratification record missing")
        elif expected_rat == "OWNER_RATIFIED":
            _require(actual_rat == "OWNER_RATIFIED", f"{did}: frontmatter ratification mismatch")
        else:
            _require(
                expected_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"},
                f"{did}: unknown ratification state",
            )
            _require(
                actual_rat in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"},
                f"{did}: frontmatter ratification mismatch",
            )

    resolution = index.get("candidate_resolution", {})
    excluded = set()
    excluded.update((resolution.get("preserved_unresolved") or {}).keys())
    excluded.update((resolution.get("absorbed_not_drafted") or {}).keys())
    excluded.update((resolution.get("retired_current_formulations") or {}).keys())
    excluded.update((resolution.get("owner_removed_deeds") or {}).keys())
    excluded.update(resolution.get("held_out") or [])
    overlap = excluded.intersection(ids)
    _require(not overlap, f"excluded candidate entered deed corpus: {sorted(overlap)}")
    _require({"A5", "C2"}.issubset(excluded), "owner-removal disposition missing from exclusions")
    _require(not (root / "deeds/A5-read-the-ground-beneath-the-table.md").exists(), "A5 file still exists in live tree")
    _require(not (root / "deeds/C2-strike-the-smallest-lever-that-reaches-the-center.md").exists(), "C2 file still exists in live tree")

    resolution_source = resolution.get("source")
    _require(isinstance(resolution_source, str) and (root / "deeds" / resolution_source).is_file(), "candidate resolution record missing")

    removal_records = index.get("owner_removal_records")
    _require(isinstance(removal_records, list) and len(removal_records) == 2, "owner removal record list must contain A5 and C2")
    expected = {
        "TAL-DEED-REMOVE-A5-001": ("delete a5", "a089840a1daa38321bb66afcd7f2f11808c72938"),
        "TAL-DEED-REMOVE-C2-001": ("delete c2", "1b926abd0162e67538c8b4fd00de7ebb495a23bb"),
    }
    seen = set()
    for rel in removal_records:
        _require(isinstance(rel, str), "owner removal record path must be a string")
        removal_path = (root / "deeds" / rel).resolve()
        _require(removal_path.is_file(), f"owner-removal record missing: {rel}")
        removal = yaml.safe_load(removal_path.read_text(encoding="utf-8"))
        rid = removal.get("id")
        _require(rid in expected, f"unexpected owner-removal record: {rid}")
        directive, historical_blob = expected[rid]
        _require(removal.get("authority") == "REPOSITORY_OWNER_DIRECTIVE", f"{rid}: removal lacks owner authority")
        _require(removal.get("owner_directive") == directive, f"{rid}: owner directive not preserved")
        _require((removal.get("deed") or {}).get("historical_git_blob_sha1") == historical_blob, f"{rid}: historical blob binding changed")
        _require((removal.get("disposition") or {}).get("future_owner_ratification_scope") == "EXCLUDED", f"{rid}: future ratification exclusion missing")
        seen.add(rid)
    _require(seen == set(expected), "owner-removal record set mismatch")

    _require((root / "method/discovery-protocol.yaml").is_file(), "discovery protocol missing")
    _require((root / "method/deep-analysis-rule.yaml").is_file(), "deep-analysis rule missing")

    return {
        "status": PASS_STATUS,
        "deed_count": len(deeds),
        "effective_owner_ratified": owner_ratified,
        "pending_owner_ratification": pending,
        "excluded_candidate_count": len(excluded),
        "owner_removed_deeds": sorted((resolution.get("owner_removed_deeds") or {}).keys()),
    }
