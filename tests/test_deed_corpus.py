from pathlib import Path
import yaml

from deed_corpus import PASS_STATUS, validate_deed_corpus


def test_live_deed_corpus_resolves_and_counts_after_A5_removal():
    result = validate_deed_corpus(Path('.'))
    assert result['status'] == PASS_STATUS
    assert result['deed_count'] == 21
    assert result['effective_owner_ratified'] == 6
    assert result['pending_owner_ratification'] == 15
    assert result['owner_removed_deeds'] == ['A5']


def test_A5_is_absent_from_live_tree_and_index():
    assert not Path('deeds/A5-read-the-ground-beneath-the-table.md').exists()
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    live = {str(x['id']) for x in index['deeds']}
    assert 'A5' not in live
    assert index['candidate_resolution']['owner_removed_deeds']['A5']
    assert index['owner_removal_record'] == '../ratification/2026-08-08-owner-removal-A5.yaml'


def test_owner_removal_record_preserves_exact_A5_history_binding():
    record = yaml.safe_load(Path('ratification/2026-08-08-owner-removal-A5.yaml').read_text())
    assert record['id'] == 'TAL-DEED-REMOVE-A5-001'
    assert record['authority'] == 'REPOSITORY_OWNER_DIRECTIVE'
    assert record['owner_directive'] == 'delete a5'
    assert record['deed']['historical_git_blob_sha1'] == 'a089840a1daa38321bb66afcd7f2f11808c72938'
    assert record['disposition']['live_corpus'] == 'REMOVED'
    assert record['disposition']['future_owner_ratification_scope'] == 'EXCLUDED'


def test_excluded_candidates_and_removed_deeds_are_not_live_deeds():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    live = {str(x['id']) for x in index['deeds']}
    resolution = index['candidate_resolution']
    excluded = (
        set(resolution['preserved_unresolved'])
        | set(resolution['absorbed_not_drafted'])
        | set(resolution['retired_current_formulations'])
        | set(resolution['owner_removed_deeds'])
        | set(resolution['held_out'])
    )
    assert not live.intersection(excluded)
    assert {'A5', 'C5', 'C6', 'C10', 'D1', 'A6', 'B5', 'C9'}.issubset(excluded)


def test_effective_ratifications_are_expressed_by_record_without_rewriting_frozen_deeds():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    by_id = {str(x['id']): x for x in index['deeds']}
    for did in ('0', 'A1', 'A2', 'A3', 'A4'):
        assert by_id[did]['ratification'] == 'OWNER_RATIFIED_BY_RECORD'
        assert by_id[did]['ratification_record'] == '../ratification/2026-08-08-owner-deed-decisions-v2-in-progress.yaml'
    assert by_id['C1']['ratification'] == 'OWNER_RATIFIED'
    for did in ('B1', 'B2', 'B3', 'B4', 'B6', 'B7', 'C2', 'C3', 'C4', 'C7', 'C8', 'C11', 'D2', 'D3', 'D4'):
        assert by_id[did]['ratification'] == 'PENDING_OWNER_RATIFICATION'
