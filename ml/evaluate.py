"""Audit frozen nested OOF evidence; retrain with python -m ml.train."""
import csv
import hashlib
import json
import numpy as np
from ml.schema import ARTIFACTS, DATA_PATH, ROOT, load_data
from ml.train import metrics
from ml.integrity import verify_manifest


def main():
    verify_manifest()
    evidence=json.loads((ARTIFACTS/'evidence.json').read_text(encoding='utf-8'))
    registry=json.loads((ARTIFACTS/'registry.json').read_text(encoding='utf-8'))
    _,ys,_=load_data()
    assert hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()==registry['dataset_sha256']==evidence['dataset']['sha256']
    rows=[]
    for target,e in evidence['targets'].items():
        model=registry['models'][target]
        assert hashlib.sha256((ARTIFACTS/model['file']).read_bytes()).hexdigest()==model['sha256']
        assert [r['truth'] for r in e['oof']]==ys[target].tolist()
        p=np.array([r['probability'] for r in e['oof']])
        values=metrics(ys[target],p)
        for k,v in values.items():
            if k=='confusion_matrix':assert v==e['metrics'][k]
            else:assert np.isclose(v,e['metrics'][k],atol=1e-12)
        rows.append({'target':target,**{k:v for k,v in values.items() if k!='confusion_matrix'},'auc_ci_low':e['auc_ci'][0],'auc_ci_high':e['auc_ci'][1]})
        print(f'{target}: AUC {values["roc_auc"]:.4f}, F1 {values["f1"]:.4f}, recall {values["recall"]:.4f}, Brier {values["brier"]:.4f} | hashes and OOF metrics verified')
    out=ROOT/'experiments/metrics.csv';out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    refinement=ROOT/'experiments/vessel_refinement/results.json'
    if refinement.exists():
        from ml.refine_vessels import operating_metrics
        result=json.loads(refinement.read_text(encoding='utf-8'))
        assert hashlib.sha256((ARTIFACTS/'evidence.json').read_bytes()).hexdigest()==result['baseline_evidence_sha256'], 'Stale threshold evidence: run python -m ml.refine_vessels'
        assert hashlib.sha256((ARTIFACTS/'registry.json').read_bytes()).hexdigest()==result['baseline_registry_sha256']
        threshold_rows=[]
        for target,e in result['targets'].items():
            for v in e['variants']:
                prefix='baseline' if v['policy']=='Frozen baseline' else 'expanded'
                p=np.array([r[f'{prefix}_probability'] for r in e['oof']])
                threshold=.5 if v['operating_point']=='0.50' else np.array([r[f'{prefix}_threshold'] for r in e['oof']])
                values=operating_metrics(ys[target],p,threshold)
                assert values['confusion_matrix']==v['metrics']['confusion_matrix']
                for k,value in values.items():
                    if k!='confusion_matrix': assert np.isclose(value,v['metrics'][k],atol=1e-12)
                threshold_rows.append({'target':target,'policy':v['policy'],'operating_point':v['operating_point'],**{k:v for k,v in values.items() if k!='confusion_matrix'}})
        with (ROOT/'experiments/research_threshold_metrics.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(threshold_rows[0]));writer.writeheader();writer.writerows(threshold_rows)
        print('Training-selected threshold metrics and frozen baseline fingerprints verified.')
    print('Verified frozen internal evaluation. This does not constitute new or external validation.')


if __name__=='__main__':main()
