"""Offline policy safety boundaries; no model answers synthesized as eval evidence."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / 'benchmarks/pplx-disagreement-offline/replay.py'
SPEC = importlib.util.spec_from_file_location('offline_policy', PATH)
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


def row(**changes):
    value = {'route': 'planner_fallback', 'reason': 'low_confidence',
             'pplx_status': 'row_semantic_issue', 'authoritative_status': 'conformant',
             'shadow_status': 'conformant', 'confidence': 0.4203098334772307}
    value.update(changes)
    return value


def test_warning_preserved_without_mutating_authoritative_or_input():
    value = row()
    before = deepcopy(value)
    result = POLICY.disagreement_to_review(value)
    assert value == before
    assert result['route'] == 'review' and result['shadow_status'] == 'uncertain'
    assert result['authoritative_status'] == 'conformant'
    assert result['warning']['candidate_status'] == 'row_semantic_issue'


@pytest.mark.parametrize('changes', [
    {'pplx_status': 'conformant'}, {'confidence': 0.8}, {'confidence': 0.95},
    {'confidence': -0.1}, {'confidence': float('nan')}, {'confidence': True},
    {'pplx_status': None}, {'pplx_status': 'invalid'}, {'authoritative_status': None},
    {'reason': 'provider_or_contract_failure'}, {'reason': 'conflicting_conventions'},
    {'reason': 'input_limit'}, {'route': 'review', 'reason': 'explicit_uncertainty'},
    {'route': 'pplx', 'reason': 'confident_classification'},
])
def test_policy_does_not_erase_existing_gates_or_invent_missing_answers(changes):
    value = row(**changes)
    assert POLICY.disagreement_to_review(value) == value


def test_reverse_disagreement_also_requests_review_not_clean_acceptance():
    value = row(pplx_status='conformant', authoritative_status='mixed', shadow_status='mixed')
    result = POLICY.disagreement_to_review(value)
    assert result['shadow_status'] == 'uncertain' and result['route'] == 'review'
    assert result['authoritative_status'] == 'mixed'
