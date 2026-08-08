from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "deeds" / "index.yaml"


def load_index():
    return yaml.safe_load(INDEX.read_text(encoding="utf-8"))


def test_deed_counts_and_files_resolve():
    data = load_index()
    deeds = data["deeds"]
    assert len(deeds) == data["counts"]["deeds"]
    ids = [item["id"] for item in deeds]
    assert len(ids) == len(set(ids))
    for item in deeds:
        assert (ROOT / "deeds" / item["file"]).is_file(), item


def test_ratification_counts_match_index():
    data = load_index()
    deeds = data["deeds"]
    ratified = [d for d in deeds if d["ratification"] == "OWNER_RATIFIED"]
    pending = [d for d in deeds if d["ratification"] != "OWNER_RATIFIED"]
    assert len(ratified) == data["counts"]["owner_ratified"]
    assert len(pending) == data["counts"]["canonical_draft_pending_ratification"]


def test_resolved_new_drafts_are_present_but_not_owner_ratified():
    data = load_index()
    by_id = {d["id"]: d for d in data["deeds"]}
    for deed_id in ("A4", "B1", "B7"):
        assert by_id[deed_id]["status"] == "CANONICAL_DRAFT"
        assert by_id[deed_id]["ratification"] == "PENDING_OWNER_RATIFICATION"


def test_held_and_retired_candidates_do_not_load_as_deeds():
    data = load_index()
    deed_ids = {d["id"] for d in data["deeds"]}
    resolution = data["candidate_resolution"]
    held = set(resolution["held_candidates"])
    retired = set(resolution["retired_current_formulations"])
    assert deed_ids.isdisjoint(held)
    assert deed_ids.isdisjoint(retired)


def test_c1_remains_the_only_owner_ratified_deed():
    data = load_index()
    ratified_ids = {d["id"] for d in data["deeds"] if d["ratification"] == "OWNER_RATIFIED"}
    assert ratified_ids == {"C1"}
