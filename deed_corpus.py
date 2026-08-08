#!/usr/bin/env python3
"""Structural validation for the Talleyrand deed corpus.

This validates repository identity, load-order records, file/frontmatter binding,
and exclusion of unresolved/retired candidates. It does not certify the truth or
wisdom of any deed.
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
    deeds = index.get("deeds")
    _require(isinstance(deeds, list) and deeds, "deed index must contain deeds")

    ids = [str(d.get("id")) for d in deeds]
    files = [d.get("file") for d in deeds]
    _require(len(ids) == len(set(ids)), "duplicate deed id")
    _require(len(files) == len(set(files)), "duplicate deed file")
    _require(ids[0] == "0", "Deed 0 must load first")

    counts = index.get("counts", {})
    owner_ratified = sum(1 for d in deeds if d.get("ratification") == "OWNER_RATIFIED")
    pending = sum(1 for d in deeds if d.get("ratification") in {"PENDING_OWNER_RATIFICATION", "PENDING_OWNER_RATIFICATION_PER_DEED"})
    _require(counts.get("deeds") == len(deeds), "deed count mismatch")
    _require(counts.get("owner_ratified") == owner_ratified, "owner-ratified count mismatch")
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
        normalized = {
            "PENDING_OWNER_RATIFICATION": "PENDING_OWNER_RATIFICATION_PER_DEED",
            "PENDING_OWNER_RATIFICATION_PER_DEED": "PENDING_OWNER_RATIFICATION_PER_DEED",
            "OWNER_RATIFIED": "OWNER_RATIFIED",
        }
        _require(normalized.get(expected_rat) == normalized.get(actual_rat), f"{did}: frontmatter ratification mismatch")

    resolution = index.get("candidate_resolution", {})
    excluded = set()
    excluded.update((resolution.get("preserved_unresolved") or {}).keys())
    excluded.update((resolution.get("absorbed_not_drafted") or {}).keys())
    excluded.update((resolution.get("retired_current_formulations") or {}).keys())
    excluded.update(resolution.get("held_out") or [])
    overlap = excluded.intersection(ids)
    _require(not overlap, f"excluded candidate entered deed corpus: {sorted(overlap)}")

    resolution_source = index.get("candidate_resolution", {}).get("source")
    _require(isinstance(resolution_source, str) and (root / "deeds" / resolution_source).is_file(), "candidate resolution record missing")
    _require((root / "method/discovery-protocol.yaml").is_file(), "discovery protocol missing")

    return {
        "status": PASS_STATUS,
        "deed_count": len(deeds),
        "owner_ratified": owner_ratified,
        "pending_owner_ratification": pending,
        "excluded_candidate_count": len(excluded),
    }
