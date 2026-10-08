"""Frozen development opportunity audit. Run from repository root as a module.

Optional CatBoost is isolated: see requirements.txt in this directory.
This runner never writes to ml/artifacts or chooses a deployable model.
"""
import hashlib
import importlib.metadata
import json
import os
import time
import warnings
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '2')
import joblib
import numpy as np
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import roc_auc_score, brier_score_loss
from threadpoolctl import threadpool_limits
from catboost import CatBoostClassifier
from ml.compatibility import check_model_compatibility
from ml.modeling import candidates, calibrated
from ml.schema import ARTIFACTS, ROOT, SEED, LeakageGuard, load_data
from ml.train import json_write, metrics

HERE = Path(__file__).resolve().parent


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cat_frame(X, columns):
    frame = X.copy()
    for name in columns:
        frame[name] = frame[name].astype(str)
    return frame


def make_candidate(spec, X, schema):
    family = spec['family']
    params = {k: v for k, v in spec.items() if k != 'family'}
    if family == 'CatBoost':
        cats = [f['name'] for f in schema if f['kind'] == 'category']
        return Pipeline([
            ('leakage', LeakageGuard()),
            ('categories', FunctionTransformer(cat_frame, kw_args={'columns': cats})),
            ('model', CatBoostClassifier(**params, cat_features=cats, iterations=150,
                learning_rate=.04, boosting_type='Ordered', loss_function='Logloss',
                thread_count=2, random_seed=SEED, allow_writing_files=False, verbose=False)),
        ])
    if family == 'Elastic net':
        model = LogisticRegression(**params, penalty='elasticnet', solver='saga',
                                   max_iter=10000, tol=.0001, random_state=SEED)
    else:
        model = HistGradientBoostingClassifier(**params, max_iter=100, learning_rate=.04,
                    min_samples_leaf=20, early_stopping=False, random_state=SEED)
    return clone(candidates(X, schema)[0][2]).set_params(model=model)


def paired_interval(y, base, expanded):
    rng = np.random.default_rng(SEED)
    groups = [np.flatnonzero(y == value) for value in [0, 1]]
    values = []
    for _ in range(2000):
        idx = np.concatenate([rng.choice(g, len(g)) for g in groups])
        values.append([roc_auc_score(y[idx], expanded[idx]) - roc_auc_score(y[idx], base[idx]),
                       brier_score_loss(y[idx], expanded[idx]) - brier_score_loss(y[idx], base[idx])])
    return dict(zip(['auc_delta', 'brier_delta'], np.quantile(values, [.025, .975], axis=0).T.tolist()))


def run():
    start = time.perf_counter()
    check_model_compatibility()
    # Refuse to silently replace a completed experiment with another search.
    if (HERE / 'results.json').exists():
        raise SystemExit('Completed audit exists. Use a separate clean copy for reproduction.')
    protocol = json.loads((HERE / 'protocol.json').read_text())
    frozen = {p.name: fingerprint(p) for p in ARTIFACTS.iterdir() if p.is_file()}
    json_write(HERE / 'execution.json', {
        'protocol_sha256': fingerprint(HERE / 'protocol.json'), 'runner_sha256': fingerprint(Path(__file__)),
        'frozen_artifacts': frozen,
        'libraries': {n: importlib.metadata.version(n) for n in ['catboost', 'numpy', 'scikit-learn', 'xgboost']},
    })
    X, ys, _ = load_data()
    evidence = json.loads((ARTIFACTS / 'evidence.json').read_text(encoding='utf-8'))
    result = {}
    for target in protocol['targets']:
        bundle = joblib.load(ARTIFACTS / f'{target}.joblib')
        y, base = ys[target], evidence['targets'][target]
        names = ['Baseline', 'Expanded', 'Elastic net', 'HistGradientBoosting', 'CatBoost', 'Train prevalence']
        probs = {n: np.full((2, len(X)), np.nan) for n in names}
        fold_records = []
        for f, (fold, record) in enumerate(zip(bundle['folds'], base['folds'])):
            train, test = np.asarray(fold['train_indices']), np.asarray(fold['test_indices'])
            assert set(train).isdisjoint(test) and set(train) | set(test) == set(range(len(X)))
            tx, ty = X.iloc[train], y[train]
            inner = list(StratifiedKFold(3, shuffle=True, random_state=SEED + f).split(tx, ty))
            inner_indices = [{'train': train[a].tolist(), 'validation': train[b].tolist()} for a, b in inner]
            best, trials = {}, []
            for spec in protocol['candidates']:
                estimator = make_candidate(spec, tx, bundle['schema'])
                with warnings.catch_warnings(record=True) as seen:
                    warnings.simplefilter('always', ConvergenceWarning)
                    p = cross_val_predict(estimator, tx, ty, cv=inner, method='predict_proba')[:, 1]
                auc, brier = roc_auc_score(ty, p), brier_score_loss(ty, p)
                score = float(auc - .25 * brier)
                trial = {'candidate': spec, 'auc': float(auc), 'brier': float(brier), 'selection_score': score,
                         'inner_oof': p.tolist(), 'warnings': sorted(set(str(w.message) for w in seen))}
                trials.append(trial)
                family = spec['family']
                if family not in best or score > best[family][0]:
                    best[family] = (score, estimator, spec)
            fitted = {name: calibrated(clone(e), tx, ty, SEED + f) for name, (_, e, _) in best.items()}
            winner = max(record['inner_trials'] + [
                {'family': n, 'params': s, 'selection_score': score} for n, (score, _, s) in best.items()
            ], key=lambda t: t['selection_score'])
            selected = fitted.get(winner['family'], fold['model'])
            predictions = {n: m.predict_proba(X.iloc[test])[:, 1] for n, m in fitted.items()}
            predictions.update(Baseline=fold['model'].predict_proba(X.iloc[test])[:, 1],
                               Expanded=selected.predict_proba(X.iloc[test])[:, 1])
            predictions['Train prevalence'] = np.full(len(test), ty.mean())
            for n, p in predictions.items():
                probs[n][f // 5, test] = p
            fm = {n: metrics(y[test], p) for n, p in predictions.items()}
            fold_records.append({'fold': f, 'train_indices': train.tolist(), 'test_indices': test.tolist(),
                'inner_indices': inner_indices, 'trials': trials, 'selected': winner,
                'metrics': fm, 'calibration_seed': SEED + f})
            json_write(HERE / f'{target}-folds.json', fold_records)
            # Log progress without feeding outer performance back into development.
            print(f'{target}: completed fold {f + 1}/10, all eight trials logged', flush=True)
        assert all(np.isfinite(p).all() for p in probs.values())
        assert np.allclose(probs['Baseline'].mean(axis=0), [r['probability'] for r in base['oof']], atol=1e-12)
        summary = {n: metrics(y, p.mean(axis=0)) for n, p in probs.items()}
        delta_auc = summary['Expanded']['roc_auc'] - summary['Baseline']['roc_auc']
        delta_brier = summary['Expanded']['brier'] - summary['Baseline']['brier']
        auc_wins = sum(f['metrics']['Expanded']['roc_auc'] > f['metrics']['Baseline']['roc_auc'] for f in fold_records)
        brier_wins = sum(f['metrics']['Expanded']['brier'] < f['metrics']['Baseline']['brier'] for f in fold_records)
        result[target] = {'metrics': summary, 'auc_delta': delta_auc, 'brier_delta': delta_brier,
            'auc_improved_folds': auc_wins, 'brier_improved_folds': brier_wins,
            'paired_conditional_95ci': paired_interval(y, probs['Baseline'].mean(axis=0), probs['Expanded'].mean(axis=0)),
            'opportunity_flag': bool((delta_auc >= .02 and delta_brier <= .005 and auc_wins >= 7) or
                                     (delta_brier <= -.01 and delta_auc >= -.005 and brier_wins >= 7)),
            'repeat_metrics': {n: [metrics(y, p) for p in arr] for n, arr in probs.items()},
            'oof': [{'row': i, 'truth': int(y[i]), 'predictions': {n: arr[:, i].tolist() for n, arr in probs.items()}} for i in range(len(X))]}
    assert frozen == {p.name: fingerprint(p) for p in ARTIFACTS.iterdir() if p.is_file()}
    json_write(HERE / 'results.json', {'protocol': protocol, 'targets': result,
               'production_unchanged': True, 'runtime_seconds': time.perf_counter() - start})
    for target, r in result.items():
        print(target, json.dumps({k: r[k] for k in ['auc_delta', 'brier_delta', 'auc_improved_folds', 'brier_improved_folds', 'paired_conditional_95ci', 'opportunity_flag']}), flush=True)


if __name__ == '__main__':
    with threadpool_limits(limits=2):
        run()
