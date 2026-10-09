import copy
import json

import numpy as np
import pytest

from ml.integrity import digest, write_manifest, verify_manifest
from ml.reproducibility import checkpoint_protocol, fingerprint, checkpoint_matches
from ml.reliability import calibration_bins, attribution_comparison, probability_diagnostics


def test_checkpoint_rejects_changed_protocol_and_legacy():
    protocol = checkpoint_protocol('dataset', 2, 'CAD', [])
    saved = {'protocol': protocol, 'protocol_sha256': fingerprint(protocol)}
    assert checkpoint_matches(saved, protocol)
    assert not checkpoint_matches({'source_hash': 'dataset', 'repeats': 2}, protocol)
    for key, value in [('target', 'LAD'), ('repeats', 3), ('seed', 17), ('source_hash', 'changed'),
                       ('schema', [{'name': 'new'}]), ('libraries', {'numpy': 'changed'}),
                       ('code', {'ml/modeling.py': 'changed'}), ('python', 'changed')]:
        changed = copy.deepcopy(protocol)
        changed[key] = value
        assert not checkpoint_matches(saved, changed), key


def test_text_fingerprints_ignore_only_platform_line_endings(tmp_path):
    path = tmp_path / 'modeling.py'
    path.write_bytes(b'x = 1\r\ny = 2\r\n')
    original = digest(path)
    path.write_bytes(b'x = 1\ny = 2\n')
    assert digest(path) == original
    path.write_bytes(b'x = 2\ny = 2\n')
    assert digest(path) != original


def test_complete_manifest_detects_ood_schema_and_model_corruption(tmp_path):
    artifacts = tmp_path / 'ml/artifacts'
    artifacts.mkdir(parents=True)
    schema = tmp_path / 'data/data_dictionary/features.json'
    schema.parent.mkdir(parents=True)
    schema.write_text('[]')
    (artifacts / 'registry.json').write_text(json.dumps({'models': {'CAD': {'file': 'CAD.joblib'}}}))
    for name in ['CAD.joblib', 'ood.joblib', 'evidence.json']:
        (artifacts / name).write_bytes(b'original')
    write_manifest(tmp_path, artifacts)
    verify_manifest(tmp_path, artifacts)
    for path in [artifacts / 'ood.joblib', artifacts / 'CAD.joblib', schema]:
        original = path.read_bytes()
        path.write_bytes(b'changed')
        with pytest.raises(RuntimeError, match='Artifact integrity check failed'):
            verify_manifest(tmp_path, artifacts)
        path.write_bytes(original)
    manifest = json.loads((artifacts / 'integrity.json').read_text())
    del manifest['files']['ml/artifacts/ood.joblib']
    (artifacts / 'integrity.json').write_text(json.dumps(manifest))
    with pytest.raises(RuntimeError, match='incomplete manifest'):
        verify_manifest(tmp_path, artifacts)


def test_ood_mismatch_fails_before_any_unpickling(monkeypatch, tmp_path):
    from api.service import ModelService
    from ml.schema import ARTIFACTS
    from shutil import copytree
    root = tmp_path
    copytree(ARTIFACTS, root / 'ml/artifacts')
    from ml.schema import ROOT
    copytree(ROOT / 'data/data_dictionary', root / 'data/data_dictionary')
    (root / 'ml/artifacts/ood.joblib').write_bytes(b'corrupted')
    monkeypatch.setattr('api.service.ROOT', root)
    monkeypatch.setattr('api.service.ARTIFACTS', root / 'ml/artifacts')
    def forbidden(*args, **kwargs):
        pytest.fail('Deserialization happened before integrity verification')
    monkeypatch.setattr('api.service.joblib.load', forbidden)
    with pytest.raises(RuntimeError, match='ood.joblib'):
        ModelService()


def test_calibration_bins_cover_patients_and_handle_ties_and_extremes():
    for y, p in [(np.array([0, 0, 1, 1]), np.array([0., 0., 1., 1.])),
                 (np.array([0, 1, 0, 1]), np.full(4, .5))]:
        bins = calibration_bins(y, p)
        assert sum(b['n'] for b in bins) == len(y)
        assert sum(b['positive'] for b in bins) == y.sum()
        for b in bins:
            assert 0 <= b['low'] <= b['y'] <= b['high'] <= 1
            assert b['high'] > b['low']


def test_local_stability_detects_ranking_and_sign_changes():
    a = np.array([5., 4., 3., 2., 1., 0.])
    identical = attribution_comparison(a, a)
    assert identical == {'top5_overlap': 1., 'top5_sign_agreement': 1., 'max_change_pp': 0.}
    changed = attribution_comparison(a, -a[::-1])
    assert changed['top5_overlap'] == .8
    assert changed['top5_sign_agreement'] == 0


def test_diagnostics_preserve_frozen_metrics_and_bin_coordinates():
    from ml.schema import ARTIFACTS
    evidence = json.loads((ARTIFACTS / 'evidence.json').read_text(encoding='utf-8'))
    for record in evidence['targets'].values():
        diagnostic = probability_diagnostics(record)
        assert diagnostic['brier'] == pytest.approx(record['metrics']['brier'])
        assert sum(b['n'] for b in diagnostic['bins']) == record['n']
        assert np.allclose([[b['x'], b['y']] for b in diagnostic['bins']],
                           [[b['x'], b['y']] for b in record['curves']['calibration']])
        assert len(diagnostic['repeat_metrics']) == 2


def test_saved_local_audit_is_bound_to_current_sources_and_reconstructs():
    from ml.reliability import load_verified
    from ml.schema import ARTIFACTS
    result = load_verified()
    assert result is not None
    evidence = json.loads((ARTIFACTS / 'evidence.json').read_text(encoding='utf-8'))
    for target, record in result['targets'].items():
        assert record['probability'] == probability_diagnostics(evidence['targets'][target])
        for case in record['local_shap']['cases']:
            fold = evidence['targets'][target]['folds'][case['fold']]
            assert case['row'] in fold['test_indices']
            for variant in case['variants']:
                assert set(variant['background_rows']).issubset(fold['train_indices'])
                assert variant['base_probability'] + sum(variant['values']) == pytest.approx(case['probability'], abs=1e-6)
                reference = case['variants'][variant['reference_variant']]['values']
                assert variant['comparison'] == attribution_comparison(np.array(reference), np.array(variant['values']))


def test_stale_reliability_evidence_is_not_served(monkeypatch, tmp_path):
    from ml import reliability
    result = reliability.load_verified()
    assert result is not None
    result['fingerprints']['ml/modeling.py'] = 'changed'
    path = tmp_path / 'results.json'
    path.write_text(json.dumps(result), encoding='utf-8')
    monkeypatch.setattr(reliability, 'OUTPUT', path)
    assert reliability.load_verified() is None
