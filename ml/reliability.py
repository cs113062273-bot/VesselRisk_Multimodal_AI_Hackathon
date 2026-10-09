"""Reproducible diagnostics of frozen predictions and local explanations; no fitting."""
import json
import time

import numpy as np

from ml.integrity import digest, verify_manifest
from ml.modeling import explain
from ml.schema import ARTIFACTS, ROOT, SEED
from ml.train import json_write, metrics

OUTPUT = ROOT / 'experiments/reliability/results.json'
PROTOCOL = {
    'rows': [2, 41, 68, 3],
    'selection': 'Four existing demo rows fixed before measuring explanation stability; not representative sampling.',
    'variants': ['Displayed: 2 cycles', 'Different seed: 2 cycles', 'More computation: 8 cycles', 'Different background vs 8-cycle reference'],
    'calibration': 'Six quantile bins of repeat-averaged held-out predictions. Vertical bars are descriptive 95% Wilson intervals for the observed fraction, conditional on bins; correlated CV fits and model-selection uncertainty are not covered.',
    'bootstrap': '2000 patient resamples of fixed held-out predictions; conditional on the fitted models, not external validation.',
    'stability': 'Seed and computation changes compare with the displayed two-cycle explanation. Background changes compare two eight-cycle explanations with the same seed, changing only training background. Top-five overlap and sign agreement are descriptive, not clinical validity or model uncertainty.',
}


def calibration_bins(y, p, count=6):
    boundaries = np.percentile(p, np.linspace(0, 100, count + 1))
    membership = np.searchsorted(boundaries[1:-1], p)
    result = []
    z = 1.959963984540054
    for index in range(count):
        mask = membership == index
        n = int(mask.sum())
        if not n:
            continue
        positives = int(y[mask].sum())
        rate = positives / n
        denominator = 1 + z * z / n
        center = (rate + z * z / (2 * n)) / denominator
        half = z * np.sqrt(rate * (1 - rate) / n + z * z / (4 * n * n)) / denominator
        result.append({'x': float(p[mask].mean()), 'y': rate, 'n': n, 'positive': positives,
                       'low': max(0., float(center - half)), 'high': min(1., float(center + half))})
    return result


def attribution_comparison(reference, changed):
    a = np.argsort(-np.abs(reference), kind='stable')[:5]
    b = np.argsort(-np.abs(changed), kind='stable')[:5]
    return {'top5_overlap': len(set(a) & set(b)) / 5,
            'top5_sign_agreement': float(np.mean(np.sign(reference[a]) == np.sign(changed[a]))),
            'max_change_pp': float(np.max(np.abs(reference - changed)) * 100)}


def probability_diagnostics(record):
    y = np.array([row['truth'] for row in record['oof']])
    p = np.array([row['probability'] for row in record['oof']])
    repeat_p = np.array([row['repeat_probabilities'] for row in record['oof']]).T
    baseline = np.zeros_like(repeat_p)
    for fold in record['folds']:
        baseline[fold['repeat'], fold['test_indices']] = y[fold['train_indices']].mean()
    baseline_p = baseline.mean(axis=0)
    squared_error = (p - y) ** 2
    baseline_error = (baseline_p - y) ** 2
    rng = np.random.default_rng(SEED)
    samples = rng.integers(0, len(y), size=(2000, len(y)))
    return {
        'bins': calibration_bins(y, p), 'brier': float(squared_error.mean()),
        'brier_ci': np.quantile(squared_error[samples].mean(axis=1), [.025, .975]).tolist(),
        'training_prevalence_brier': float(baseline_error.mean()),
        'brier_skill': float(1 - squared_error.mean() / baseline_error.mean()),
        'brier_delta_ci': np.quantile((squared_error - baseline_error)[samples].mean(axis=1), [.025, .975]).tolist(),
        'repeat_metrics': [metrics(y, repeat) for repeat in repeat_p],
    }


def main():
    from api.service import ModelService
    started = time.perf_counter()
    manifest = verify_manifest()
    # Source binding prevents an old diagnostic being silently used after changes.
    fingerprints = {**manifest['files'], 'ml/modeling.py': digest(ROOT / 'ml/modeling.py'),
                    'ml/reliability.py': digest(ROOT / 'ml/reliability.py')}
    service = ModelService()
    targets = {}
    for target, bundle in service.bundles.items():
        cases = []
        for row in PROTOCOL['rows']:
            member = next(f for f in bundle['folds'] if row in f['test_indices'])
            assert row not in member['train_indices']
            frame = service.X.iloc[[row]]
            background = member['background']
            replacement = service.X.iloc[member['train_indices']].sample(len(background), random_state=SEED + 1)
            settings = [(2, SEED, background), (2, SEED + 1, background),
                        (8, SEED, background), (8, SEED, replacement)]
            variants = []
            values = []
            for label, (cycles, seed, bg) in zip(PROTOCOL['variants'], settings):
                begin = time.perf_counter()
                result = explain(member['model'], frame, bg, service.schema, cycles=cycles, seed=seed)
                value = result.values[0]
                values.append(value)
                reference_index = 2 if len(values) == 4 else 0
                variants.append({'name': label, 'cycles': cycles, 'seed': seed, 'reference_variant': reference_index,
                                 'background_rows': bg.index.tolist(), 'seconds': time.perf_counter() - begin,
                                 'base_probability': float(result.base_values[0]), 'values': value.tolist(),
                                 'comparison': attribution_comparison(values[reference_index], value)})
            cases.append({'row': row, 'fold': next(i for i, f in enumerate(bundle['folds']) if f is member),
                          'probability': float(member['model'].predict_proba(frame)[0, 1]), 'variants': variants})
            print(f'{target} row {row}: overlap {[v["comparison"]["top5_overlap"] for v in variants[1:]]}', flush=True)
        summaries = []
        for index, label in enumerate(PROTOCOL['variants'][1:], 1):
            measurements = [case['variants'][index]['comparison'] for case in cases]
            summaries.append({'name': label,
                              'mean_top5_overlap': float(np.mean([m['top5_overlap'] for m in measurements])),
                              'min_top5_overlap': min(m['top5_overlap'] for m in measurements),
                              'mean_sign_agreement': float(np.mean([m['top5_sign_agreement'] for m in measurements])),
                              'max_change_pp': max(m['max_change_pp'] for m in measurements)})
        targets[target] = {'probability': probability_diagnostics(service.evidence['targets'][target]),
                           'local_shap': {'n': len(cases), 'summary': summaries, 'cases': cases}}
    json_write(OUTPUT, {'protocol': PROTOCOL, 'fingerprints': fingerprints,
                        'features': list(service.X.columns), 'targets': targets,
                        'runtime_seconds': time.perf_counter() - started})
    print(f'Wrote {OUTPUT}; no model weights or frozen evaluation files changed.', flush=True)


def load_verified():
    if not OUTPUT.exists():
        return None
    result = json.loads(OUTPUT.read_text(encoding='utf-8'))
    if result.get('protocol') != PROTOCOL:
        return None
    expected = set(verify_manifest()['files']) | {'ml/modeling.py', 'ml/reliability.py'}
    if set(result.get('fingerprints', {})) != expected:
        return None
    if any(digest(ROOT / name) != value for name, value in result['fingerprints'].items()):
        return None
    return result


if __name__ == '__main__':
    main()
