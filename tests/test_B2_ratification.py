from pathlib import Path
import yaml

from ratification_guard import git_blob_sha1


LIVE_RECORD = Path("ratification/live-owner-ratifications.yaml")
B2_PATH = Path("deeds/B2-price-the-coalition-in-beliefs.md")
SHARPENING_PATH = Path("deeds/amendments/2026-08-08-B2-coalition-belief-sharpening.md")


def _record():
    return yaml.safe_load(LIVE_RECORD.read_text(encoding="utf-8"))


def test_B1_and_B2_remain_ratified_on_live_surface():
    record = _record()
    by_id = {str(item["id"]): item["decision"] for item in record["deed_decisions"]}
    assert by_id["B1"] == "RATIFY"
    assert by_id["B2"] == "RATIFY"


def test_B2_ratification_is_bound_to_frozen_deed_and_member_reconstruction_sharpening():
    record = _record()
    assert git_blob_sha1(B2_PATH) == "89b82d33f5fe365e457e8867148281f35ae314fa"
    by_id = {item["id"]: item for item in record["interpretive_bindings"]}
    binding = by_id["TAL-DEED-B2-SHARP-001"]
    assert binding["deed"] == "B2"
    assert Path(binding["path"]) == SHARPENING_PATH
    assert git_blob_sha1(SHARPENING_PATH) == binding["git_blob_sha1"] == "2c8c38b0f63f9c9da7a1ac20f9ce2e52591b3bfe"
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    assert "reconstruct each member separately" in text
    assert "least costly **truthful** change" in text
    assert "does not presume that every coalition is merely apparent" in text
    assert "dated leak prediction remains mandatory" in text


def test_B2_sharpening_preserves_nonbelief_causes_of_adherence():
    text = SHARPENING_PATH.read_text(encoding="utf-8")
    for term in (
        "coercion",
        "dependence",
        "obligation",
        "material interest",
        "institutional lock-in",
        "fear",
        "lack of alternatives",
    ):
        assert term in text
    assert "what observable conduct should change" in text
    assert "by what date that change should become visible" in text


def test_manifest_continues_to_load_B2_sharpening():
    manifest = yaml.safe_load(Path("manifest.yaml").read_text(encoding="utf-8"))
    state = manifest["deed_corpus_state"]
    ratified = {str(x) for x in state["effective_owner_ratified_deeds"]}
    assert {"B1", "B2"}.issubset(ratified)
    assert state["deed_B2_owner_decision"] == "RATIFY"
    assert state["deed_B2_owner_sharpening"] == "TAL-DEED-B2-SHARP-001"
    review = manifest["ratification_review_state"]
    assert review["active_decision_record"] is None
    assert manifest["records"]["live_owner_ratifications"] == str(LIVE_RECORD)
    assert manifest["records"]["deed_B2_interpretive_sharpening"] == str(SHARPENING_PATH)
