from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
C7_PATH = Path("deeds/C7-declare-in-daylight.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-C7-adversarial-verification-sharpening.md")


def test_C7_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    c7 = decisions["C7"]
    assert c7["decision"] == "RATIFY"
    assert c7["git_blob_sha1"] == "9e5f9e1ecdab0b13ab52f6c9634c94fe7faa3032"
    assert git_blob_sha1(C7_PATH) == c7["git_blob_sha1"]
    assert len(decisions) == 18


def test_C7_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-C7-SHARP-001"]
    assert binding["deed"] == "C7"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "a8207ef26f3162fa76e6ddaf308b2a8823df639a"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_C7_adversarial_verification_rules_are_mandatory():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Daylight is an instrument, not a virtue" in normalized
    assert "Do not ask to be trusted where you can arrange to be tested" in normalized
    assert "Publicity alone is not proof" in normalized or "publicity itself" in normalized
    assert "Price the watcher too" in normalized
    assert "Search failure alone is never converted into negative evidence" in normalized
    assert "Necessary secrets may remain secret" in normalized
    assert "Selective disclosure designed to create a false appearance of inspectability is counterfeit daylight" in normalized
    assert "The watcher is not presumed reliable merely because he is hostile" in normalized


def test_manifest_loads_C7_only_with_its_sharpening_and_moves_next_to_C11_after_C8():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 18
    assert state["effective_pending_deed_rulings"] == 2
    assert state["deed_C7_owner_decision"] == "RATIFY"
    assert state["deed_C7_owner_sharpening"] == "TAL-DEED-C7-SHARP-001"
    assert manifest["records"]["deed_C7_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "D3"
    assert "TAL-DEED-C7-SHARP-001" in review["owner_ratified_deed_sharpenings"]
