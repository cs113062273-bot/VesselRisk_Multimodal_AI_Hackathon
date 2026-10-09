"""Recompute saved audit evidence without CatBoost, refitting or model selection."""
import hashlib
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score, brier_score_loss
from ml.schema import ARTIFACTS, load_data, SEED
from ml.train import metrics, json_write

HERE = Path(__file__).resolve().parent


def verify_frozen_artifacts(fingerprints):
    registry_rename = None
    for name, digest in fingerprints.items():
        raw = (ARTIFACTS / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() == digest:
            continue
        # Preserve the historical fingerprint. Accept only the exact documented
        # display-version rename; every other byte must match the original file.
        if name == 'registry.json' and json.loads(raw).get('version') == 'vesselrisk-1.0':
            original = raw.replace(b'"version": "vesselrisk-1.0"', b'"version": "cardiovision-1.0"', 1)
            if hashlib.sha256(original).hexdigest() == digest:
                registry_rename = {'from': 'cardiovision-1.0', 'to': 'vesselrisk-1.0',
                                  'historical_sha256': digest, 'current_sha256': hashlib.sha256(raw).hexdigest()}
                continue
        raise AssertionError(f'Frozen artifact changed: {name}')
    return registry_rename


def paired_ci(y, base, candidate):
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(y == v) for v in [0, 1]]
    scores = []
    for _ in range(2000):
        i = np.concatenate([rng.choice(g, len(g)) for g in groups])
        scores.append([roc_auc_score(y[i], candidate[i]) - roc_auc_score(y[i], base[i]),
                       brier_score_loss(y[i], candidate[i]) - brier_score_loss(y[i], base[i])])
    return dict(zip(['auc_delta', 'brier_delta'], np.quantile(scores, [.025, .975], axis=0).T.tolist()))


def verify():
    result = json.loads((HERE / 'results.json').read_text())
    execution = json.loads((HERE / 'execution.json').read_text())
    assert hashlib.sha256((HERE / 'protocol.json').read_bytes()).hexdigest() == execution['protocol_sha256']
    assert hashlib.sha256((HERE / 'run.py').read_bytes()).hexdigest() == execution['runner_sha256']
    registry_rename = verify_frozen_artifacts(execution['frozen_artifacts'])
    if registry_rename:
        print('Registry display-version rename verified: cardiovision-1.0 -> vesselrisk-1.0; all other bytes match the historical fingerprint.')
    evidence = json.loads((ARTIFACTS / 'evidence.json').read_text(encoding='utf-8'))
    _, ys, _ = load_data()
    secondary = {}
    for target, record in result['targets'].items():
        y = ys[target]
        rows = record['oof']
        assert [r['row'] for r in rows] == list(range(303))
        assert [r['truth'] for r in rows] == y.tolist()
        coverage = np.zeros((2, 303), dtype=int)
        folds = json.loads((HERE / f'{target}-folds.json').read_text())
        for f, fold in enumerate(folds):
            training, test = fold['train_indices'], fold['test_indices']
            frozen_fold = evidence['targets'][target]['folds'][f]
            assert training == frozen_fold['train_indices'] and test == frozen_fold['test_indices']
            assert set(training).isdisjoint(test)
            coverage[f // 5, test] += 1
            validation_rows = []
            for split in fold['inner_indices']:
                a, b = set(split['train']), set(split['validation'])
                assert a.isdisjoint(b) and a | b == set(training)
                assert (a | b).isdisjoint(test)
                validation_rows.extend(b)
            assert sorted(validation_rows) == sorted(training)
            assert [t['candidate'] for t in fold['trials']] == result['protocol']['candidates']
            for trial in fold['trials']:
                p = np.array(trial['inner_oof'])
                assert np.isfinite(p).all() and ((p >= 0) & (p <= 1)).all()
                auc, brier = roc_auc_score(y[training], p), brier_score_loss(y[training], p)
                assert np.isclose(auc, trial['auc'], atol=1e-12, rtol=0)
                assert np.isclose(brier, trial['brier'], atol=1e-12, rtol=0)
                assert np.isclose(auc - .25 * brier, trial['selection_score'], atol=1e-12, rtol=0)
            trials = frozen_fold['inner_trials'] + [
                {'family': t['candidate']['family'], 'params': t['candidate'], 'selection_score': t['selection_score']}
                for t in fold['trials']]
            winner = max(trials, key=lambda t: t['selection_score'])
            assert winner['family'] == fold['selected']['family']
            assert winner['params'] == fold['selected']['params']
            source = winner['family'] if winner['family'] in ['Elastic net', 'HistGradientBoosting', 'CatBoost'] else 'Baseline'
            for i in test:
                assert rows[i]['predictions']['Expanded'][f // 5] == rows[i]['predictions'][source][f // 5]
            for name, fm in fold['metrics'].items():
                measured = metrics(y[test], np.array([rows[i]['predictions'][name][f // 5] for i in test]))
                assert measured == fm
        assert (coverage == 1).all()
        probabilities = {n: np.array([r['predictions'][n] for r in rows]).T for n in record['metrics']}
        assert np.allclose(probabilities['Baseline'].mean(axis=0), [r['probability'] for r in evidence['targets'][target]['oof']], rtol=0, atol=1e-12)
        for name, array in probabilities.items():
            assert metrics(y, array.mean(axis=0)) == record['metrics'][name]
            assert [metrics(y, p) for p in array] == record['repeat_metrics'][name]
        base = probabilities['Baseline'].mean(axis=0)
        ci = paired_ci(y, base, probabilities['Expanded'].mean(axis=0))
        assert ci == record['paired_conditional_95ci']
        secondary[target] = {name: paired_ci(y, base, probabilities[name].mean(axis=0))
                             for name in ['Elastic net', 'HistGradientBoosting', 'CatBoost']}
        print(f'{target}: all 80 inner trials, training-only winners, split coverage, fold/repeat/pooled metrics and paired intervals verified.')
    json_write(HERE / 'verification.json', {'status': 'passed',
        'registry_display_version_rename': registry_rename,
        'secondary_family_conditional_95ci': secondary,
        'scope': 'Frozen-prediction audit, not new validation. Secondary family intervals are descriptive, unadjusted for multiple comparisons and must not select a winner.'})
    print('All frozen model/evidence fingerprints verified; registry display-version changes explicitly accounted for. No additional fitting performed.')


if __name__ == '__main__':
    verify()
