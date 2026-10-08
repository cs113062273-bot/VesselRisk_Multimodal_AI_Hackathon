"""Only validity, leakage, prediction and critical integration checks."""
import hashlib
import json
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.service import get_service
from ml.schema import ARTIFACTS, ROOT, TARGETS, LeakageGuard, guard_columns, load_data
from ml.train import metrics
from ml.compatibility import ModelCompatibilityError


@pytest.fixture(scope='module')
def service():
    return get_service()


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c


def test_source_schema_and_label_integrity():
    X,ys,raw=load_data()
    assert X.shape==(303,55)
    assert raw.isna().sum().sum()==0
    assert {t:int(y.sum()) for t,y in ys.items()}=={'CAD':216,'LAD':177,'LCX':119,'RCA':114}
    # Do not silently derive/repair Cath from vessel labels: the supplied source
    # has exactly one conflicting record (zero-based row 93).
    mismatches=np.flatnonzero(ys['CAD']!=np.logical_or.reduce([ys[t] for t in ['LAD','LCX','RCA']]))
    assert mismatches.tolist()==[93]
    assert raw.loc[93,'Cath']=='Normal' and raw.loc[93,'LAD']=='Stenotic'
    assert set(TARGETS.values()).isdisjoint(X.columns)


@pytest.mark.parametrize('name',['LAD','LCX','RCA','Cath',' cAtH ','C A D'])
def test_leakage_guard_rejects_fit_and_inference(name):
    X,_,_=load_data(); fitted=LeakageGuard().fit(X)
    polluted=X.assign(**{name:1})
    with pytest.raises(ValueError,match='leakage'):
        LeakageGuard().fit(polluted)
    with pytest.raises(ValueError,match='leakage'):
        fitted.transform(polluted)
    with pytest.raises(ValueError,match='leakage'):
        guard_columns([name])


def test_nested_fold_isolation_and_complete_oof_coverage(service):
    for t,e in service.evidence['targets'].items():
        coverage=np.zeros((2,303),dtype=int)
        for f in e['folds']:
            train,test=set(f['train_indices']),set(f['test_indices'])
            assert train.isdisjoint(test)
            assert train|test==set(range(303))
            assert len(train)==f['train_n'] and len(test)==f['test_n']
            coverage[f['repeat'],list(test)]+=1
        assert (coverage==1).all()
        assert len(e['oof'])==303
        probs=np.array([r['probability'] for r in e['oof']])
        assert np.isfinite(probs).all() and ((probs>=0)&(probs<=1)).all()
        for i,r in enumerate(e['oof']):
            assert r['row']==i and r['truth']==int(service.ys[t][i])
            assert r['probability']==pytest.approx(np.mean(r['repeat_probabilities']))


def test_evidence_metrics_recompute_from_real_oof(service):
    for t,e in service.evidence['targets'].items():
        p=np.array([r['probability'] for r in e['oof']])
        measured=metrics(service.ys[t],p)
        for name,value in measured.items():
            if name=='confusion_matrix': assert value==e['metrics'][name]
            else: assert value==pytest.approx(e['metrics'][name],abs=1e-12)


def test_exact_models_have_only_eligible_inputs_and_valid_hashes(service):
    for t,b in service.bundles.items():
        record=service.registry['models'][t]
        assert hashlib.sha256((ARTIFACTS/record['file']).read_bytes()).hexdigest()==record['sha256']
        for selected in [b,*b['folds']]:
            for m in selected['alternatives'].values():
                for calibrated in m.calibrated_classifiers_:
                    pipeline=calibrated.estimator
                    guard_columns(pipeline.named_steps['leakage'].feature_names_in_)
                    assert list(pipeline.named_steps['leakage'].feature_names_in_)==list(service.X)


def test_prediction_shap_reconstruction_and_heldout_isolation(client,service):
    case=next(c for c in service.cases if c['title']=='Mixed vessel estimates')
    res=client.post('/predict',json={'features':case['features'],'case_id':case['id']})
    assert res.status_code==200
    out=res.json(); assert set(out['targets'])==set(TARGETS)
    assert out['mode']=='held-out demonstration' and out['observed']==case['observed']
    for t,r in out['targets'].items():
        assert 0<=r['probability']<=1
        assert r['explanation']['reconstructed_probability']==pytest.approx(r['probability'],abs=1e-6)
        assert len(r['explanation']['contributions'])==55
        assert r['explanation']['base_probability']+sum(f['value'] for f in r['explanation']['contributions'])==pytest.approx(r['probability'],abs=1e-6)
        applicable=[f for f in service.bundles[t]['folds'] if int(case['id']) in f['test_indices']]
        assert len(applicable)==2
        assert all(int(case['id']) not in f['train_indices'] for f in applicable)
        expected=applicable[0]['model'].predict_proba(pd.DataFrame([case['features']],columns=service.X.columns))[0,1]
        assert r['probability']==pytest.approx(expected)
        ref=r['model_reference']
        fold_index=next(i for i,f in enumerate(service.bundles[t]['folds']) if f is applicable[0])
        assert ref['member']==f'folds[{fold_index}].model'
        assert ref['artifact_file']==service.registry['models'][t]['file']
        training=applicable[0]['train_indices'].tolist()
        assert ref['training_n']==len(training)
        assert ref['training_indices_sha256']==hashlib.sha256(json.dumps(training,separators=(',',':')).encode()).hexdigest()


def test_patient_edit_updates_predictions_and_invalidates_observed_outcome(client,service):
    case=next(c for c in service.cases if c['title']=='Lower CAD estimate')
    first=client.post('/predict',json={'features':case['features'],'case_id':case['id']}).json()
    changed={**case['features'],'Age':85,'Typical Chest Pain':1,'EF-TTE':25,'HTN':1}
    out=client.post('/predict',json={'features':changed,'case_id':case['id']}).json()
    assert out['mode']=='held-out sensitivity' and out['observed'] is None
    assert abs(out['targets']['CAD']['probability']-first['targets']['CAD']['probability'])>.01
    assert out['targets']['CAD']['explanation']['reconstructed_probability']==pytest.approx(out['targets']['CAD']['probability'])


def test_invalid_inputs_and_target_leakage_rejected_by_api(client,service):
    f=service.cases[0]['features']
    bad=[{**f,'LAD':'Stenotic'},{k:v for k,v in f.items() if k!='Age'},{**f,'unknown':1},{**f,'Age':999},
         {**f,'Sex':'Other'},{**f,'Age':True},{**f,'FBS':-1}]
    for features in bad:
        r=client.post('/predict',json={'features':features})
        assert r.status_code==422, r.text
    assert client.post('/predict',json={'features':f,'case_id':'999'}).status_code==422


def test_critical_get_routes(client):
    for path in ['/health','/schema','/cases','/model-info','/evidence']:
        assert client.get(path).status_code==200
    assert client.get('/health').json()['artifact_integrity']=='verified'


def test_real_anatomical_geometry_and_target_mapping():
    folder=ROOT/'web/public/anatomy'
    m=json.loads((folder/'manifest.json').read_text()); b=(folder/'heart.bin').read_bytes()
    assert hashlib.sha256(b).hexdigest()==m['sha256'] and len(b)==m['bytes']
    assert len(m['parts'])==63
    mapping={p['id']:p['target'] for p in m['parts']}
    assert mapping['FJ2631']=='LAD' and mapping['FJ2649']=='LCX' and mapping['FJ2723']=='RCA'
    assert set(p['target'] for p in m['parts'])=={None,'LAD','LCX','RCA'}
    for p in m['parts']:
        v=np.frombuffer(b,dtype='<f4',count=p['vertexCount']*3,offset=p['positions'])
        idx=np.frombuffer(b,dtype='<u4',count=p['indexCount'],offset=p['indices'])
        assert np.isfinite(v).all() and idx.max()<p['vertexCount']


def test_sklearn_mismatch_rejected_before_unpickling(monkeypatch):
    from api.service import ModelService
    monkeypatch.setattr('ml.compatibility.importlib.metadata.version', lambda _: '1.8.0')
    def must_not_load(*args, **kwargs):
        raise AssertionError('No incompatible artifact may be unpickled')
    monkeypatch.setattr('api.service.joblib.load', must_not_load)
    with pytest.raises(ModelCompatibilityError, match='built with 1.7.1; installed: 1.8.0') as error:
        ModelService()
    assert 'python scripts/start.py --setup' in str(error.value)


def test_changed_workbook_rejected_before_unpickling(monkeypatch,tmp_path):
    from api.service import ModelService
    changed=tmp_path/'changed.xlsx'
    changed.write_bytes(b'An unpaired replacement workbook')
    monkeypatch.setattr('api.service.DATA_PATH',changed)
    def must_not_load(*args, **kwargs):
        raise AssertionError('An unpaired dataset must fail before model loading')
    monkeypatch.setattr('api.service.joblib.load',must_not_load)
    with pytest.raises(RuntimeError,match='Dataset integrity check failed'):
        ModelService()


def test_training_only_threshold_splits_and_oof_coverage(service):
    result=json.loads((ROOT/'experiments/vessel_refinement/results.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ARTIFACTS/'evidence.json').read_bytes()).hexdigest()==result['baseline_evidence_sha256']
    assert hashlib.sha256((ARTIFACTS/'registry.json').read_bytes()).hexdigest()==result['baseline_registry_sha256']
    for target,e in result['targets'].items():
        coverage=np.zeros((2,303),dtype=int)
        for f in e['folds']:
            training,test=set(f['train_indices']),set(f['test_indices'])
            coverage[f['repeat'],list(test)]+=1
            for key in ['baseline_threshold_audit','expanded_threshold_audit']:
                a=f[key]; inner_coverage=[]
                assert {r['row'] for r in a['inner_oof']}==training
                assert all(r['truth']==int(service.ys[target][r['row']]) for r in a['inner_oof'])
                for inner in a['inner_splits']:
                    train,val=set(inner['train_indices']),set(inner['validation_indices'])
                    assert train.isdisjoint(val) and train|val==training
                    assert (train|val).isdisjoint(test)
                    inner_coverage.extend(val)
                assert sorted(inner_coverage)==sorted(training)
                y=np.array([r['truth'] for r in a['inner_oof']]); p=np.array([r['probability'] for r in a['inner_oof']])
                grid=np.round(np.arange(.15,.751,.01),2)
                def f1_at(t):
                    pred=p>=t; tp=np.sum(pred&(y==1)); fp=np.sum(pred&(y==0)); fn=np.sum(~pred&(y==1))
                    return 2*tp/max(2*tp+fp+fn,1)
                assert f1_at(a['threshold'])==pytest.approx(max(f1_at(t) for t in grid))
        assert (coverage==1).all()


def test_research_metrics_reconstruct_and_rejected_models_stay_frozen(service):
    result=json.loads((ROOT/'experiments/vessel_refinement/results.json').read_text(encoding='utf-8'))
    from ml.refine_vessels import operating_metrics
    for target,e in result['targets'].items():
        assert not e['expanded_model_promoted'] and e['retained_research_threshold']
        assert len(e['oof'])==303
        for v in e['variants']:
            prefix='baseline' if v['policy']=='Frozen baseline' else 'expanded'
            p=np.array([r[f'{prefix}_probability'] for r in e['oof']])
            threshold=.5 if v['operating_point']=='0.50' else np.array([r[f'{prefix}_threshold'] for r in e['oof']])
            for r in e['oof']:
                assert r['truth']==int(service.ys[target][r['row']])
                assert r[f'{prefix}_threshold']==pytest.approx(np.mean(r[f'repeat_{prefix}_thresholds']))
            measured=operating_metrics(service.ys[target],p,threshold)
            for key,value in measured.items():
                if key=='confusion_matrix': assert value==v['metrics'][key]
                else: assert value==pytest.approx(v['metrics'][key],abs=1e-12)
        baseline=e['variants'][0]['metrics']; research=e['variants'][1]['metrics']
        assert baseline['roc_auc']==research['roc_auc'] and baseline['brier']==research['brier']
        assert research['confusion_matrix'][0][1]>baseline['confusion_matrix'][0][1]
        assert target in service.evidence['refinement']['targets']
