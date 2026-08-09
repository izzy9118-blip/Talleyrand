from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
C4_PATH = Path("deeds/C4-move-it-onto-paper.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-09-C4-letter-spirit-credit-sharpening.md")


def test_C4_ratification_is_exact_and_live():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    decisions = {str(item["id"]): item for item in record["deed_decisions"]}
    c4 = decisions["C4"]
    assert c4["decision"] == "RATIFY"
    assert c4["git_blob_sha1"] == "d35b84d0b053053e3de0887b96dab6f27f6070a0"
    assert git_blob_sha1(C4_PATH) == c4["git_blob_sha1"]


def test_C4_sharpening_is_exactly_bound():
    record = yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))
    bindings = {str(item["id"]): item for item in record["interpretive_bindings"]}
    binding = bindings["TAL-DEED-C4-SHARP-001"]
    assert binding["deed"] == "C4"
    assert binding["path"] == str(SHARPENING_PATH)
    assert binding["git_blob_sha1"] == "3f2debc06de08f7a4ff2a6060fd5aa00047d352a"
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"]


def test_C4_letter_spirit_credit_rules_are_mandatory():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "does not make it more authoritative than speech" in normalized
    assert "Paper fixes something narrower and politically useful: the pledge" in normalized
    assert "Judgment must recover the spirit of the bargain" in normalized
    assert "The signer must also be priced through an established conduct file" in normalized
    assert "Subsequent conduct tests both the instrument and the signer" in normalized
    assert "The paper fixes the letter; judgment recovers the spirit. Price the pledge through the signer." in normalized
    assert "It does not require publication" in normalized


def test_manifest_loads_C4_and_moves_next_to_C11_after_C8():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    assert state["effective_owner_ratified_count"] == 17
    assert state["effective_pending_deed_rulings"] == 3
    assert state["deed_C4_owner_decision"] == "RATIFY"
    assert state["deed_C4_owner_sharpening"] == "TAL-DEED-C4-SHARP-001"
    assert manifest["records"]["deed_C4_interpretive_sharpening"] == str(SHARPENING_PATH)
    review = manifest["ratification_review_state"]
    assert review["next_pending_deed"] == "D2"
    assert "TAL-DEED-C4-SHARP-001" in review["owner_ratified_deed_sharpenings"]
