import hashlib
import json
from functools import lru_cache
import joblib
import numpy as np
import pandas as pd
from ml.schema import ARTIFACTS, DATA_PATH, ROOT, TARGETS, guard_columns, load_data, encode_frame
from ml.modeling import explain
from ml.compatibility import check_model_compatibility


class ModelService:
    def __init__(self):
        self.registry = json.loads((ARTIFACTS/'registry.json').read_text(encoding='utf-8'))
        check_model_compatibility(self.registry)
        self.evidence = json.loads((ARTIFACTS/'evidence.json').read_text(encoding='utf-8'))
        if (hashlib.sha256(DATA_PATH.read_bytes()).hexdigest() != self.registry['dataset_sha256']
                or self.evidence['dataset']['sha256'] != self.registry['dataset_sha256']):
            raise RuntimeError('Dataset integrity check failed: restore the workbook paired with these model artifacts.')
        refinement_path = ROOT/'experiments/vessel_refinement/results.json'
        if refinement_path.exists():
            refinement = json.loads(refinement_path.read_text(encoding='utf-8'))
            # Never pair stale threshold evidence with newly retrained artifacts.
            if (refinement['baseline_evidence_sha256'] == hashlib.sha256((ARTIFACTS/'evidence.json').read_bytes()).hexdigest()
                    and refinement['baseline_registry_sha256'] == hashlib.sha256((ARTIFACTS/'registry.json').read_bytes()).hexdigest()):
                self.evidence['refinement'] = {'protocol': refinement['protocol'], 'targets': {
                    t: {k: e[k] for k in ['variants', 'candidate_comparisons', 'expanded_model_promoted',
                                          'retained_research_threshold', 'chosen_policy', 'final_research_threshold']}
                    for t, e in refinement['targets'].items()}}
        self.schema = json.loads((ROOT/'data/data_dictionary/features.json').read_text(encoding='utf-8'))
        self.bundles = {}
        for target, m in self.registry['models'].items():
            path = ARTIFACTS/m['file']
            if hashlib.sha256(path.read_bytes()).hexdigest() != m['sha256']:
                raise RuntimeError(f'Artifact integrity check failed: {target}')
            self.bundles[target] = joblib.load(path)
        self.ood = joblib.load(ARTIFACTS/'ood.joblib')
        self.X, self.ys, _ = load_data()
        # Everyday profiles drawn intact from the source workbook. Select by
        # patient characteristics, while predictions still exclude each row.
        examples = [
            (2, 'smoker with chest pain'),
            (41, 'non-smoker, no diabetes'),
            (68, 'diabetes, breathlessness'),
            (115, 'diabetes, high blood pressure'),
            (12, 'diabetes, high blood pressure'),
            (6, 'former smoker, chest pain'),
            (3, 'high blood pressure, breathlessness'),
            (30, 'non-smoker with chest pain'),
        ]
        self.cases = []
        for row, situation in examples:
            patient = self.X.iloc[row]
            person = 'woman' if patient.Sex == 'Fmale' else 'man'
            self.cases.append({
                'id': str(row), 'row': row,
                'title': f'{int(patient.Age)}-year-old {person} · {situation}',
                'description': 'Example from the dataset. Selecting it fills all 55 inputs; you can edit them.',
                'features': patient.to_dict(),
                'observed': {t: int(y[row]) for t, y in self.ys.items()},
            })

    def validate(self, features):
        guard_columns(features.keys())
        expected = {f['name'] for f in self.schema}
        missing, unknown = expected-set(features), set(features)-expected
        if missing or unknown:
            raise ValueError(f'Expected all 55 inputs. Missing: {sorted(missing)}; unknown: {sorted(unknown)}')
        cleaned = {}
        for f in self.schema:
            name, value = f['name'], features[f['name']]
            if isinstance(value,bool) or value is None:
                raise ValueError(f'{name}: provide a number or one of the listed categories')
            if f['kind']=='category':
                if value not in f['options']:
                    raise ValueError(f'{name}: choose from {f["options"]}')
                cleaned[name] = value
            else:
                try:
                    v = float(value)
                except (ValueError,TypeError):
                    raise ValueError(f'{name}: numeric value required') from None
                if not np.isfinite(v) or v < 0:
                    raise ValueError(f'{name}: a finite nonnegative value is required')
                if f['integer'] and v != int(v):
                    raise ValueError(f'{name}: integer value required by the source schema')
                bounds = {'Age':(18,110),'BP':(50,300),'PR':(20,250),'Length':(100,230),'Weight':(25,250),'EF-TTE':(0,100),'Lymph':(0,100),'Neut':(0,100),'BMI':(10,80)}
                lo,hi = bounds.get(name,(0,max(f['max']*4,100)))
                if not lo <= v <= hi:
                    raise ValueError(f'{name}: supported input bounds are {lo}–{hi}')
                cleaned[name] = int(v) if f['integer'] else v
        return cleaned

    def predict(self, features, case_id=None):
        cleaned = self.validate(features)
        if case_id is not None and case_id not in {c['id'] for c in self.cases}:
            raise ValueError('Unknown demonstration case')
        key = json.dumps(cleaned,sort_keys=True)
        return self._predict(key,case_id)

    @lru_cache(maxsize=64)
    def _predict(self, key, case_id):
        features = json.loads(key)
        frame = pd.DataFrame([features],columns=[f['name'] for f in self.schema])
        targets = {}
        warnings = ['Research and education only. Not a diagnosis, treatment recommendation, or substitute for diagnostic imaging.']
        encoded = encode_frame(frame,self.schema)
        z = (encoded-self.ood['mean'])/self.ood['scale']
        reference = self.ood['reference']
        if case_id is not None:
            reference = np.delete(reference,int(case_id),axis=0)
        distance = float(np.min(np.linalg.norm(reference-z,axis=1)))
        outside = [f['label'] for f in self.schema if f['kind']=='number' and not f['min'] <= float(features[f['name']]) <= f['max']]
        ood = bool(distance > self.ood['threshold'] or outside)
        if ood:
            warnings.append('Limited representation: this profile is outside the training cohort reference range. Estimates may be unreliable.')
        for t,bundle in self.bundles.items():
            applicable = [fold for fold in bundle['folds'] if case_id is None or int(case_id) in fold['test_indices']]
            if case_id is not None:
                selected = applicable[0]
                assert int(case_id) not in selected['train_indices']
                fold_index = next(i for i, fold in enumerate(bundle['folds']) if fold is selected)
                member = f'folds[{fold_index}].model'
                training_indices = selected['train_indices'].tolist()
            else:
                selected = bundle
                member = 'model'
                training_indices = list(range(len(self.X)))
            model = selected['model']
            probability = float(model.predict_proba(frame)[0,1])
            agreement = [{'family':family,'probability':float(m.predict_proba(frame)[0,1])} for family,m in selected['alternatives'].items()]
            spread = float(np.ptp([a['probability'] for a in agreement]))
            resampled = [float(f['model'].predict_proba(frame)[0,1]) for f in applicable]
            sv = explain(model,frame,selected['background'],self.schema,cycles=2)
            contributions = [{'feature':f['name'],'label':f['label'],'group':f['group'],'unit':f['unit'],
                              'input':features[f['name']],'value':float(v)} for f,v in zip(self.schema,sv.values[0])]
            contributions.sort(key=lambda f:abs(f['value']),reverse=True)
            targets[t] = {'probability':probability,'positive':probability>=.5,'threshold':.5,
                          'family':selected['family'],'calibration':'sigmoid',
                          'model_hash':self.registry['models'][t]['sha256'],
                          'model_reference': {
                              'artifact_file': self.registry['models'][t]['file'],
                              'member': member, 'training_n': len(training_indices),
                              'training_indices_sha256': hashlib.sha256(json.dumps(training_indices, separators=(',', ':')).encode()).hexdigest(),
                              'note': 'model_hash identifies the complete bundle; member identifies the displayed estimator. Headline metrics average two held-out predictions per patient; this estimate uses one fitted model.',
                          },
                          'agreement':agreement,'agreement_spread':spread,
                          'resampling_range':[float(np.min(resampled)),float(np.max(resampled))],
                          'range_models':len(resampled),'range_note':'Observed range of refitted models; not a clinical confidence interval.',
                          'confidence_note':'Limited cohort evidence' if ood or spread>.25 else 'Internal cohort evidence only',
                          'explanation':{'base_probability':float(sv.base_values[0]),'contributions':contributions,
                                         'reconstructed_probability':float(sv.base_values[0]+sv.values[0].sum()),
                                         'method':'Permutation SHAP on calibrated probability','unit':'probability contribution','background_n':len(selected['background']),
                                         'note':'Associations in a model, not causes or treatment effects. Correlated features can share attribution.'}}
        if any(r['agreement_spread']>.25 for r in targets.values()):
            warnings.append('Candidate models disagree for at least one target. Inspect the model comparison before interpreting the estimate.')
        if targets['CAD']['positive'] != any(targets[t]['positive'] for t in ['LAD','LCX','RCA']):
            warnings.append('Independent CAD and vessel classifiers disagree at the 0.50 research threshold. Outputs are not forced into consistency.')
        case = next((c for c in self.cases if c['id']==case_id),None)
        modified = bool(case and any(features[k] != case['features'][k] for k in features))
        return {'targets':targets,'warnings':warnings,'ood':{'flag':ood,'nearest_distance':distance,
                'reference_threshold':self.ood['threshold'],'outside_features':outside,'method':'Standardized mixed-feature nearest-neighbor distance; heuristic, not validated detector'},
                'mode':'held-out sensitivity' if modified else 'held-out demonstration' if case else 'new profile',
                'case_id':case_id,'observed':case['observed'] if case and not modified else None,
                'version':self.registry['version'],'dataset_sha256':self.registry['dataset_sha256'],
                'anatomy_note':'Generic vessel anatomy. Color shows vessel-level estimated probability, not lesion location or severity.',
                'feature_count':55}


@lru_cache(maxsize=1)
def get_service():
    return ModelService()
