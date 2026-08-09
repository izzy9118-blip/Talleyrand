from pathlib import Path
import yaml

from deed_corpus import PASS_STATUS, validate_deed_corpus


def test_live_deed_corpus_resolves_and_counts():
    result = validate_deed_corpus(Path('.'))
    assert result['status'] == PASS_STATUS
    assert result['deed_count'] == 20
    assert result['effective_owner_ratified'] == 16
    assert result['pending_owner_ratification'] == 4


def test_live_index_contains_no_deleted_deed_metadata():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    assert index['version'] == '2.8.0'
    assert index['corpus'] == 'DEED CORPUS 2.8 LIVE-ONLY AFTER C8 RATIFICATION'
    assert 'owner_removal_records' not in index
    assert 'owner_removed_deeds' not in index['candidate_resolution']
    assert 'retired_by_owner_removal' not in index['open_consolidation_questions']


def test_only_indexed_top_level_deeds_can_be_live():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    indexed = {x['file'] for x in index['deeds']}
    discovered = {p.name for p in Path('deeds').glob('*.md')}
    assert discovered == indexed | {'00-see-one-board.md'}


def test_excluded_candidates_are_not_live_deeds():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    live = {str(x['id']) for x in index['deeds']}
    resolution = index['candidate_resolution']
    excluded = (
        set(resolution['preserved_unresolved'])
        | set(resolution['absorbed_not_drafted'])
        | set(resolution['retired_current_formulations'])
        | set(resolution['held_out'])
    )
    assert not live.intersection(excluded)


def test_effective_ratifications_use_one_live_authority_surface():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    by_id = {str(x['id']): x for x in index['deeds']}
    for did in ('0', 'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B6', 'B7', 'C3', 'C4', 'C7', 'C8'):
        assert by_id[did]['ratification'] == 'OWNER_RATIFIED_BY_RECORD'
        assert by_id[did]['ratification_record'] == '../ratification/live-owner-ratifications.yaml'
    assert by_id['C1']['ratification'] == 'OWNER_RATIFIED'
    assert by_id['C3']['interpretive_sharpening'] == 'amendments/2026-08-08-C3-authorship-pressure-sharpening.md'
    assert by_id['C4']['interpretive_sharpening'] == 'amendments/2026-08-09-C4-letter-spirit-credit-sharpening.md'
    assert by_id['C7']['interpretive_sharpening'] == 'amendments/2026-08-09-C7-adversarial-verification-sharpening.md'
    assert by_id['C8']['interpretive_sharpening'] == 'amendments/2026-08-09-C8-entitled-standing-sharpening.md'
    for did in ('C11', 'D2', 'D3', 'D4'):
        assert by_id[did]['ratification'] == 'PENDING_OWNER_RATIFICATION'


def test_live_ratification_ledger_contains_exactly_live_ratified_deeds():
    record = yaml.safe_load(Path('ratification/live-owner-ratifications.yaml').read_text())
    ids = {str(x['id']) for x in record['deed_decisions']}
    assert ids == {'0', 'A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'B6', 'B7', 'C1', 'C3', 'C4', 'C7', 'C8'}
    assert all(x['decision'] == 'RATIFY' for x in record['deed_decisions'])
    bindings = {str(x['id']): x for x in record['interpretive_bindings']}
    assert bindings['TAL-DEED-C3-SHARP-001']['deed'] == 'C3'
    assert bindings['TAL-DEED-C4-SHARP-001']['deed'] == 'C4'
    assert bindings['TAL-DEED-C7-SHARP-001']['deed'] == 'C7'
    assert bindings['TAL-DEED-C8-SHARP-001']['deed'] == 'C8'
