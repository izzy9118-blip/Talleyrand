from pathlib import Path
import yaml

from deed_corpus import PASS_STATUS, validate_deed_corpus


def test_live_deed_corpus_resolves_and_counts_after_C2_removal():
    result = validate_deed_corpus(Path('.'))
    assert result['status'] == PASS_STATUS
    assert result['deed_count'] == 20
    assert result['effective_owner_ratified'] == 12
    assert result['pending_owner_ratification'] == 8
    assert result['owner_removed_deeds'] == ['A5', 'C2']


def test_A5_and_C2_are_absent_from_live_tree_and_index():
    assert not Path('deeds/A5-read-the-ground-beneath-the-table.md').exists()
    assert not Path('deeds/C2-strike-the-smallest-lever-that-reaches-the-center.md').exists()
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    live = {str(x['id']) for x in index['deeds']}
    assert not {'A5', 'C2'}.intersection(live)
    assert index['candidate_resolution']['owner_removed_deeds']['A5']
    assert index['candidate_resolution']['owner_removed_deeds']['C2']
    assert set(index['owner_removal_records']) == {
        '../ratification/2026-08-08-owner-removal-A5.yaml',
        '../ratification/2026-08-08-owner-removal-C2.yaml',
    }


def test_owner_removal_records_preserve_exact_history_bindings():
    expected = {
        'A5': ('TAL-DEED-REMOVE-A5-001', 'delete a5', 'a089840a1daa38321bb66afcd7f2f11808c72938'),
        'C2': ('TAL-DEED-REMOVE-C2-001', 'delete c2', '1b926abd0162e67538c8b4fd00de7ebb495a23bb'),
    }
    for did, (rid, directive, blob) in expected.items():
        record = yaml.safe_load(Path(f'ratification/2026-08-08-owner-removal-{did}.yaml').read_text())
        assert record['id'] == rid
        assert record['authority'] == 'REPOSITORY_OWNER_DIRECTIVE'
        assert record['owner_directive'] == directive
        assert record['deed']['historical_git_blob_sha1'] == blob
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
    assert {'A5', 'C2', 'C5', 'C6', 'C10', 'D1', 'A6', 'B5', 'C9'}.issubset(excluded)


def test_effective_ratifications_are_expressed_by_record_without_rewriting_frozen_deeds():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    by_id = {str(x['id']): x for x in index['deeds']}
    for did in ('0', 'A1', 'A2', 'A3', 'A4'):
        assert by_id[did]['ratification'] == 'OWNER_RATIFIED_BY_RECORD'
        assert by_id[did]['ratification_record'] == '../ratification/2026-08-08-owner-deed-decisions-v2-in-progress.yaml'
    for did in ('B1', 'B2', 'B3', 'B4', 'B6', 'B7'):
        assert by_id[did]['ratification'] == 'OWNER_RATIFIED_BY_RECORD'
        assert by_id[did]['ratification_record'] == '../ratification/2026-08-08-owner-deed-decisions-v3-in-progress.yaml'
    assert by_id['C1']['ratification'] == 'OWNER_RATIFIED'
    for did in ('C3', 'C4', 'C7', 'C8', 'C11', 'D2', 'D3', 'D4'):
        assert by_id[did]['ratification'] == 'PENDING_OWNER_RATIFICATION'
