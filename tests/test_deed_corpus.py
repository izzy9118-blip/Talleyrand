from pathlib import Path
import copy
import yaml
import pytest

from deed_corpus import DeedCorpusError, PASS_STATUS, validate_deed_corpus


def test_live_deed_corpus_resolves_and_counts():
    result = validate_deed_corpus(Path('.'))
    assert result['status'] == PASS_STATUS
    assert result['deed_count'] == 22
    assert result['owner_ratified'] == 1
    assert result['pending_owner_ratification'] == 21


def test_excluded_candidates_are_not_live_deeds():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    live = {str(x['id']) for x in index['deeds']}
    resolution = index['candidate_resolution']
    excluded = set(resolution['preserved_unresolved']) | set(resolution['absorbed_not_drafted']) | set(resolution['retired_current_formulations']) | set(resolution['held_out'])
    assert not live.intersection(excluded)
    assert {'C5', 'C6', 'C10', 'D1', 'A6', 'B5', 'C9'}.issubset(excluded)


def test_new_resolved_deeds_are_present_but_not_self_ratified():
    index = yaml.safe_load(Path('deeds/index.yaml').read_text())
    by_id = {str(x['id']): x for x in index['deeds']}
    for did in ('A4', 'B1', 'B7'):
        assert did in by_id
        assert by_id[did]['ratification'] == 'PENDING_OWNER_RATIFICATION'
        assert by_id[did]['status'] == 'CANONICAL_DRAFT'
