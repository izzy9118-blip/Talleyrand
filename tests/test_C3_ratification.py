from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
C3_PATH = Path("deeds/C3-borrow-the-hand.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-C3-authorship-pressure-sharpening.md")


def test_C3_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    c3 = decisions["C3"]
    assert c3["decision"] == "RATIFY"
    assert c3["git_blob_sha1"] == "42cd835c27c7dd8498056c89dc16b3fc243079b2"
    assert git_blob_sha1(C3_PATH) == c3["git_blob_sha1"]


def test_C3_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-C3-SHARP-001"]
    assert binding["deed"] == "C3"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "4b83856087826db2c8fc86789f4c10d2b7355582"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_C3_authorship_integrity_and_pressure_environment_are_mandatory():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Borrow authority; never manufacture it" in normalized
    assert "Formal authorship does not by itself establish autonomous judgment" in normalized
    assert "An elicited statement does not become independent evidence merely because another person speaks it" in normalized
    assert "A refusal is likewise a documented act, not a predetermined confession" in normalized
    assert "CONTEMPORARY APPLICATION TEST — OMAN" in text
    assert "including any demonstrated United States pressure or leverage" in normalized
    assert "If the evidence does not establish such pressure, do not invent it" in normalized
    assert "illustration of method, not historical ground for C3" in normalized


def test_manifest_keeps_C3_and_moves_next_to_C11_after_C8():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 16
    assert state["effective_pending_deed_rulings"] == 4
    assert state["deed_C3_owner_decision"] == "RATIFY"
    assert state["deed_C3_owner_sharpening"] == "TAL-DEED-C3-SHARP-001"
    assert manifest["records"]["deed_C3_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "C11"
    assert "TAL-DEED-C3-SHARP-001" in review["owner_ratified_deed_sharpenings"]
