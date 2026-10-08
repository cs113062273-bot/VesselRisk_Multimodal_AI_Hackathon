"""One bounded, paired LCX/RCA experiment; never tunes on outer-test labels.

Frozen v1 artifacts and headline metrics are left intact. Expanded-policy adoption
is gated by a predeclared AUC/Brier rule, not cherry-picking an outer-fold family.
"""
import hashlib
import json
import time
from pathlib import Path
import joblib
import numpy as np
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, brier_score_loss
from ml.compatibility import check_model_compatibility
from ml.schema import ROOT, ARTIFACTS, SEED, load_data
from ml.modeling import candidates, calibrated
from ml.train import json_write, metrics

OUT = ROOT / 'experiments/vessel_refinement'
GRID = np.round(np.arange(.15, .751, .01), 2)
PROTOCOL = {
    'targets': ['LCX', 'RCA'], 'outer': 'Exactly the frozen v1 5-fold x 2-repeat split indices',
    'new_candidates': 'ExtraTrees: 160 trees, leaf 2/5, max_features .8, balanced; SVM RBF: C .3/3, gamma scale, balanced, training-only internal probability calibration',
    'selection': 'Existing inner ROC-AUC - .25*Brier; add four configurations to the six frozen candidates. Select each family parameters, then family using training-only inner scores.',
    'threshold': '3-fold calibrated inner OOF within outer train; maximize F1 over fixed grid .15:.01:.75. Ties: higher precision, then higher threshold.',
    'pooled': 'One decision per patient: mean(probability - training-selected threshold) across its two held-out folds >= 0; equivalent to mean probability >= mean threshold.',
    'promotion_rule': 'Expanded search only if paired AUC >= frozen baseline + .01 and Brier <= baseline + .005. No picking a family on outer scores.',
    'threshold_retention_rule': 'Retain research operating point only if F1 >= baseline + .03, recall >= baseline + .10, precision >= max(.45, baseline precision - .15).',
    'development_limit': 'Single bounded post-baseline development experiment on reused outer splits; comparisons are descriptive development evidence, not an untouched confirmation or external validation.',
    'seed': SEED,
}


def extra_candidates(X, schema):
    template = candidates(X, schema)[0][2]
    choices = [('ExtraTrees', {'min_samples_leaf': leaf}, ExtraTreesClassifier(n_estimators=160, min_samples_leaf=leaf, max_features=.8, class_weight='balanced', random_state=SEED, n_jobs=1)) for leaf in [2, 5]]
    choices += [('SVM RBF', {'C': c}, SVC(C=c, kernel='rbf', gamma='scale', class_weight='balanced', probability=True, random_state=SEED)) for c in [.3, 3.]]
    return [(name, params, clone(template).set_params(model=model)) for name, params, model in choices]


def select_extras(X, y, schema, seed):
    best, trials = {}, []
    for name, params, estimator in extra_candidates(X, schema):
        p = cross_val_predict(estimator, X, y, cv=StratifiedKFold(3, shuffle=True, random_state=seed), method='predict_proba')[:, 1]
        auc, brier = roc_auc_score(y, p), brier_score_loss(y, p)
        score = auc - .25 * brier
        trials.append({'family': name, 'params': params, 'auc': float(auc), 'brier': float(brier), 'selection_score': float(score)})
        if name not in best or score > best[name][0]:
            best[name] = (float(score), estimator, params)
    return best, trials


def select_threshold(y, p):
    # Inputs are training-only inner OOF. Outer labels are never an argument.
    scores = [(float(f1_score(y, p >= t, zero_division=0)), float(precision_score(y, p >= t, zero_division=0)), float(t)) for t in GRID]
    f1, precision, threshold = max(scores)
    return threshold, {'f1': f1, 'precision': precision, 'n': len(y)}


def threshold_oof(model, X, y, absolute_indices, seed):
    cv = StratifiedKFold(3, shuffle=True, random_state=seed)
    splits = list(cv.split(X, y))
    p = cross_val_predict(clone(model), X, y, cv=splits, method='predict_proba')[:, 1]
    threshold, score = select_threshold(y, p)
    audit = {'threshold': threshold, 'inner_score': score,
             'inner_splits': [{'train_indices': absolute_indices[a].tolist(), 'validation_indices': absolute_indices[b].tolist()} for a, b in splits],
             'inner_oof': [{'row': int(i), 'truth': int(v), 'probability': float(q)} for i, v, q in zip(absolute_indices, y, p)]}
    return threshold, audit


def operating_metrics(y, p, thresholds):
    out = metrics(y, p)
    label = p >= thresholds
    out.update(accuracy=float(accuracy_score(y, label)), precision=float(precision_score(y, label, zero_division=0)),
               recall=float(recall_score(y, label, zero_division=0)), f1=float(f1_score(y, label, zero_division=0)),
               confusion_matrix=confusion_matrix(y, label, labels=[0, 1]).tolist())
    return out


def run():
    start = time.perf_counter()
    check_model_compatibility()
    OUT.mkdir(parents=True, exist_ok=True)
    # Freeze this declaration before observing any new experiment results.
    json_write(OUT / 'protocol.json', PROTOCOL)
    evidence = json.loads((ARTIFACTS / 'evidence.json').read_text(encoding='utf-8'))
    registry = json.loads((ARTIFACTS / 'registry.json').read_text(encoding='utf-8'))
    X, ys, _ = load_data()
    records = {}
    for target in PROTOCOL['targets']:
        y = ys[target]; base = evidence['targets'][target]
        bundle = joblib.load(ARTIFACTS / registry['models'][target]['file'])
        schema = bundle['schema']
        probabilities = {name: np.zeros((2, len(X))) for name in ['Frozen baseline', 'Expanded search', 'ExtraTrees', 'SVM RBF']}
        thresholds = {name: np.zeros((2, len(X))) for name in ['Frozen baseline', 'Expanded search']}
        fold_records, expanded_folds = [], []
        for f, (fold, source) in enumerate(zip(bundle['folds'], base['folds'])):
            train_idx, test_idx = np.asarray(fold['train_indices']), np.asarray(fold['test_indices'])
            assert set(train_idx).isdisjoint(test_idx)
            tx, vx, ty = X.iloc[train_idx], X.iloc[test_idx], y[train_idx]
            best, trials = select_extras(tx, ty, schema, SEED + f)
            fitted = {name: calibrated(clone(estimator), tx, ty, SEED + f) for name, (_, estimator, _) in best.items()}
            combined_trials = source['inner_trials'] + trials
            winner = max(combined_trials, key=lambda r: r['selection_score'])
            if winner['family'] in fitted:
                selected = fitted[winner['family']]
            else:
                assert winner['family'] == source['selected_family'] and winner['params'] == source['params']
                selected = fold['model']
            baseline_p = fold['model'].predict_proba(vx)[:, 1]
            expanded_p = selected.predict_proba(vx)[:, 1]
            baseline_t, baseline_audit = threshold_oof(fold['model'], tx, ty, train_idx, SEED + f)
            if selected is fold['model']:
                expanded_t, expanded_audit = baseline_t, baseline_audit
            else:
                expanded_t, expanded_audit = threshold_oof(selected, tx, ty, train_idx, SEED + f)
            for name, p in [('Frozen baseline', baseline_p), ('Expanded search', expanded_p), *[(n, m.predict_proba(vx)[:, 1]) for n, m in fitted.items()]]:
                probabilities[name][f // 5, test_idx] = p
            thresholds['Frozen baseline'][f // 5, test_idx] = baseline_t
            thresholds['Expanded search'][f // 5, test_idx] = expanded_t
            alternatives = {**fold['alternatives'], **fitted}
            expanded_folds.append({**fold, 'model': selected, 'family': winner['family'], 'alternatives': alternatives})
            fold_records.append({'fold': f, 'repeat': f // 5, 'train_indices': train_idx.tolist(), 'test_indices': test_idx.tolist(),
                                 'selected_family': winner['family'], 'params': winner['params'], 'new_inner_trials': trials,
                                 'baseline_threshold_audit': baseline_audit, 'expanded_threshold_audit': expanded_audit,
                                 'baseline_threshold_metrics': operating_metrics(y[test_idx], baseline_p, baseline_t),
                                 'expanded_threshold_metrics': operating_metrics(y[test_idx], expanded_p, expanded_t)})
            print(f'{target} fold {f + 1}/10: expanded={winner["family"]}; training thresholds baseline={baseline_t:.2f}, expanded={expanded_t:.2f}', flush=True)
        frozen_p = np.array([r['probability'] for r in base['oof']])
        assert np.allclose(probabilities['Frozen baseline'].mean(axis=0), frozen_p, atol=1e-12)
        variants = []
        for name in ['Frozen baseline', 'Expanded search']:
            p = probabilities[name].mean(axis=0); ts = thresholds[name].mean(axis=0)
            for rule in ['0.50', 'Nested F1']:
                values = operating_metrics(y, p, .5 if rule == '0.50' else ts)
                variants.append({'policy': name, 'operating_point': rule, 'metrics': values,
                                 'fold_threshold_min': float(thresholds[name].min()), 'fold_threshold_max': float(thresholds[name].max())})
        baseline, expanded = variants[0]['metrics'], variants[2]['metrics']
        promote = bool(expanded['roc_auc'] >= baseline['roc_auc'] + .01 and expanded['brier'] <= baseline['brier'] + .005)
        chosen_policy = 'Expanded search' if promote else 'Frozen baseline'
        research = next(v for v in variants if v['policy'] == chosen_policy and v['operating_point'] == 'Nested F1')
        retain = bool(research['metrics']['f1'] >= baseline['f1'] + .03 and research['metrics']['recall'] >= baseline['recall'] + .10 and research['metrics']['precision'] >= max(.45, baseline['precision'] - .15))
        # Final threshold uses the same calibrated inner OOF process on all data,
        # separately from the outer evaluation. It never replaces outer thresholds.
        final_extra, final_trials = select_extras(X, y, schema, SEED)
        final_fitted = {name: calibrated(clone(estimator), X, y, SEED) for name, (_, estimator, _) in final_extra.items()}
        final_winner = max(base['final_selection_trials'] + final_trials, key=lambda r: r['selection_score'])
        final_expanded = final_fitted.get(final_winner['family'], bundle['model'])
        final_model = final_expanded if promote else bundle['model']
        final_threshold, final_audit = threshold_oof(final_model, X, y, np.arange(len(X)), SEED)
        records[target] = {'variants': variants, 'candidate_comparisons': [{'family': n, 'metrics': metrics(y, p.mean(axis=0))} for n, p in probabilities.items()],
                           'expanded_model_promoted': promote, 'retained_research_threshold': retain, 'chosen_policy': chosen_policy,
                           'final_research_threshold': final_threshold, 'final_threshold_audit': final_audit, 'folds': fold_records,
                           'new_final_trials': final_trials, 'final_expanded_family': final_winner['family'],
                           'oof': [{'row': i, 'truth': int(y[i]), 'baseline_probability': float(probabilities['Frozen baseline'][:, i].mean()),
                                    'expanded_probability': float(probabilities['Expanded search'][:, i].mean()),
                                    'baseline_threshold': float(thresholds['Frozen baseline'][:, i].mean()), 'expanded_threshold': float(thresholds['Expanded search'][:, i].mean()),
                                    'repeat_baseline_thresholds': thresholds['Frozen baseline'][:, i].tolist(), 'repeat_expanded_thresholds': thresholds['Expanded search'][:, i].tolist()} for i in range(len(X))]}
        if promote:
            # Only an accepted expanded policy is retained as a promotable bundle.
            expanded_bundle = {**bundle, 'model': final_expanded, 'family': final_winner['family'], 'alternatives': {**bundle['alternatives'], **final_fitted}, 'folds': expanded_folds}
            joblib.dump(expanded_bundle, OUT / f'{target}.accepted.joblib', compress=3)
        print(f'{target}: baseline AUC {baseline["roc_auc"]:.4f}, expanded AUC {expanded["roc_auc"]:.4f}; promote={promote}; threshold retain={retain}, recall={research["metrics"]["recall"]:.3f}, F1={research["metrics"]["f1"]:.3f}', flush=True)
        json_write(OUT / f'{target}.json', records[target])
    result = {'protocol': PROTOCOL, 'baseline_evidence_sha256': hashlib.sha256((ARTIFACTS / 'evidence.json').read_bytes()).hexdigest(),
              'baseline_registry_sha256': hashlib.sha256((ARTIFACTS / 'registry.json').read_bytes()).hexdigest(), 'targets': records, 'runtime_seconds': time.perf_counter() - start}
    json_write(OUT / 'results.json', result)
    print(f'Bounded experiment completed in {time.perf_counter() - start:.1f}s. Frozen production artifacts unchanged.', flush=True)


if __name__ == '__main__':
    run()
