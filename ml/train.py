"""python -m ml.train: nested repeated stratified evaluation and artifact export."""
import argparse
import hashlib
import importlib.metadata
import json
import time
from collections import Counter
from datetime import datetime, timezone
import joblib
import numpy as np
from scipy.stats import spearmanr
from sklearn.base import clone
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, cross_val_predict
from sklearn.calibration import calibration_curve
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, brier_score_loss, confusion_matrix, roc_curve, precision_recall_curve
from sklearn.neighbors import NearestNeighbors
from ml.schema import ROOT, ARTIFACTS, DATA_PATH, SEED, TARGETS, load_data, make_schema, encode_frame
from ml.modeling import inner_select, calibrated, explain, candidates
from ml.reproducibility import checkpoint_protocol, checkpoint_matches, fingerprint
from ml.integrity import write_manifest


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False, default=lambda v: v.item() if isinstance(v,np.generic) else str(v)),encoding='utf-8')


def metrics(y,p):
    label=p>=.5
    return {'accuracy':float(accuracy_score(y,label)), 'precision':float(precision_score(y,label,zero_division=0)), 'recall':float(recall_score(y,label,zero_division=0)), 'f1':float(f1_score(y,label,zero_division=0)), 'roc_auc':float(roc_auc_score(y,p)), 'pr_auc':float(average_precision_score(y,p)), 'brier':float(brier_score_loss(y,p)), 'confusion_matrix':confusion_matrix(y,label,labels=[0,1]).tolist()}


def curves(y,p):
    fpr,tpr,_=roc_curve(y,p)
    precision,recall,_=precision_recall_curve(y,p)
    observed,predicted=calibration_curve(y,p,n_bins=6,strategy='quantile')
    return {'roc':[{'x':float(a),'y':float(b)} for a,b in zip(fpr,tpr)], 'pr':[{'x':float(a),'y':float(b)} for a,b in zip(recall[::-1],precision[::-1])], 'calibration':[{'x':float(a),'y':float(b)} for a,b in zip(predicted,observed)]}


def bootstrap(y,p):
    rng=np.random.default_rng(SEED); pos,neg=np.where(y==1)[0],np.where(y==0)[0]; vals=[]
    for _ in range(1000):
        idx=np.concatenate([rng.choice(pos,len(pos)),rng.choice(neg,len(neg))]); vals.append(roc_auc_score(y[idx],p[idx]))
    return [float(v) for v in np.quantile(vals,[.025,.975])]


def train(repeats=2):
    start=time.perf_counter(); X,ys,raw=load_data(); schema=make_schema(X)
    ARTIFACTS.mkdir(parents=True,exist_ok=True)
    json_write(ROOT/'data/data_dictionary/features.json',schema)
    records,registry={},{}
    source_hash=hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    for target,y in ys.items():
        print(f'\n{target}: {y.sum()} positive / {len(y)} patients',flush=True)
        outer=RepeatedStratifiedKFold(n_splits=5,n_repeats=repeats,random_state=SEED)
        folds,fold_records,oof=[],[],np.zeros((repeats,len(X)))
        alternative_oof={n:np.zeros_like(oof) for n in ['Logistic regression','Random forest','XGBoost']}
        raw_oof,iso_oof=np.zeros_like(oof),np.zeros_like(oof)
        shap_importance=[]
        checkpoint=ARTIFACTS/f'{target}.checkpoint.joblib'
        protocol = checkpoint_protocol(source_hash, repeats, target, schema)
        splits=list(outer.split(X,y))
        completed=0
        if checkpoint.exists():
            saved=joblib.load(checkpoint)
            if checkpoint_matches(saved, protocol):
                folds,fold_records,oof,alternative_oof,raw_oof,iso_oof,shap_importance=[saved[k] for k in ['folds','fold_records','oof','alternative_oof','raw_oof','iso_oof','shap_importance']]
                completed=len(folds); print(f'  Resuming {completed} completed outer folds',flush=True)
            else:
                print('  Checkpoint protocol changed or predates fingerprinting; starting fresh.', flush=True)
        for fold,(train_idx,test_idx) in enumerate(splits):
            if fold<completed: continue
            tx,vx,ty=X.iloc[train_idx],X.iloc[test_idx],y[train_idx]
            assert set(train_idx).isdisjoint(test_idx)
            name,choices,inner_scores=inner_select(tx,ty,schema,SEED+fold)
            fitted={}
            for family,(_,estimator,params) in choices.items():
                fitted[family]=calibrated(clone(estimator),tx,ty,SEED+fold)
                alternative_oof[family][fold//5,test_idx]=fitted[family].predict_proba(vx)[:,1]
            selected=fitted[name]; p=selected.predict_proba(vx)[:,1]; oof[fold//5,test_idx]=p
            raw_model=clone(choices[name][1]).fit(tx,ty)
            raw_oof[fold//5,test_idx]=raw_model.predict_proba(vx)[:,1]
            isotonic=calibrated(clone(choices[name][1]),tx,ty,SEED+fold,'isotonic')
            iso_oof[fold//5,test_idx]=isotonic.predict_proba(vx)[:,1]
            bg=tx.sample(16,random_state=SEED); sx=vx.sample(6,random_state=SEED)
            sv=explain(selected,sx,bg,schema,cycles=1)
            shap_importance.append(np.mean(np.abs(sv.values),axis=0))
            fm=metrics(y[test_idx],p)
            fold_records.append({'fold':fold,'repeat':fold//5,'train_n':len(train_idx),'test_n':len(test_idx),'train_indices':train_idx.tolist(),'test_indices':test_idx.tolist(),'selected_family':name,'params':choices[name][2],'metrics':fm,'inner_trials':inner_scores})
            folds.append({'model':selected,'family':name,'alternatives':fitted,'background':bg,'train_indices':train_idx,'test_indices':test_idx})
            checkpoint_temp = checkpoint.with_suffix('.joblib.tmp')
            joblib.dump({'protocol':protocol,'protocol_sha256':fingerprint(protocol),'folds':folds,'fold_records':fold_records,'oof':oof,'alternative_oof':alternative_oof,'raw_oof':raw_oof,'iso_oof':iso_oof,'shap_importance':shap_importance},checkpoint_temp,compress=3)
            checkpoint_temp.replace(checkpoint)
            print(f'  fold {fold+1}/{5*repeats}: {name}, AUC {fm["roc_auc"]:.3f}, Brier {fm["brier"]:.3f}',flush=True)
        mean_p=oof.mean(axis=0); pooled=metrics(y,mean_p)
        dispersion={m:{'mean':float(np.mean([f['metrics'][m] for f in fold_records])),'sd':float(np.std([f['metrics'][m] for f in fold_records],ddof=1))} for m in ['accuracy','precision','recall','f1','roc_auc','pr_auc','brier']}
        global_shap=np.mean(shap_importance,axis=0)
        stability=[float(spearmanr(a,b).statistic) for i,a in enumerate(shap_importance) for b in shap_importance[i+1:]]
        groups=[]
        for group,masks in [('Sex',[(v,X.Sex.to_numpy()==v) for v in X.Sex.unique()]),('Age',[('<60',X.Age.to_numpy()<60),('60+',X.Age.to_numpy()>=60)])]:
            for label,mask in masks:
                if len(np.unique(y[mask]))==2:
                    groups.append({'group':group,'label':str(label),'n':int(mask.sum()),'positive':int(y[mask].sum()),'metrics':metrics(y[mask],mean_p[mask])})
        failures=sorted(range(len(X)),key=lambda i:abs(float(y[i])-mean_p[i]),reverse=True)[:8]
        failure_records=[{'row':int(i),'age':int(X.iloc[i].Age),'sex':X.iloc[i].Sex,'truth':int(y[i]),'probability':float(mean_p[i])} for i in failures]
        name,choices,final_trials=inner_select(X,y,schema,SEED)
        final_models={n:calibrated(clone(e),X,y,SEED) for n,(_,e,_) in choices.items()}
        bundle={'model':final_models[name],'family':name,'alternatives':final_models,'background':X.sample(20,random_state=SEED),'folds':folds,'schema':schema}
        path=ARTIFACTS/f'{target}.joblib'; joblib.dump(bundle,path,compress=3)
        registry[target]={'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'family':name,'params':choices[name][2],'calibration':'sigmoid','training_n':len(X)}
        ablations=[]
        for group in ['None','ECG','Laboratory & echo']:
            cols=[f['name'] for f in schema if f['group']!=group]; reduced=X[cols]
            e=candidates(reduced,schema)[0][2]
            ap=cross_val_predict(e,reduced,y,cv=StratifiedKFold(5,shuffle=True,random_state=SEED),method='predict_proba')[:,1]
            ablations.append({'removed':group,'method':'Fixed logistic C=0.1, raw probabilities, 5-fold OOF','metrics':metrics(y,ap)})
        records[target]={'n':len(X),'positive':int(y.sum()),'negative':int(len(y)-y.sum()),'metrics':pooled,'auc_ci':bootstrap(y,mean_p),'dispersion':dispersion,'curves':curves(y,mean_p),'folds':fold_records,'selection_counts':dict(Counter(f['selected_family'] for f in fold_records)),'final_selection_trials':final_trials,'comparisons':[{'family':n,'metrics':metrics(y,arr.mean(axis=0))} for n,arr in alternative_oof.items()],'calibration_comparison':[{'method':n,'metrics':metrics(y,a.mean(axis=0))} for n,a in [('Raw',raw_oof),('Sigmoid',oof),('Isotonic',iso_oof)]],'global_shap':[{'feature':f['name'],'label':f['label'],'group':f['group'],'value':float(v)} for f,v in sorted(zip(schema,global_shap),key=lambda z:z[1],reverse=True)],'shap_stability':{'mean_spearman':float(np.mean(stability)),'folds':len(folds),'heldout_explanations':6*len(folds),'background_n':16},'subgroups':groups,'failures':failure_records,'ablations':ablations,'oof':[{'row':i,'truth':int(y[i]),'probability':float(mean_p[i]),'repeat_probabilities':oof[:,i].tolist()} for i in range(len(X))]}
        print(f'  pooled OOF AUC {pooled["roc_auc"]:.4f}, final {name}',flush=True)
        json_write(ARTIFACTS/'evidence.partial.json',records)
    encoded=encode_frame(X,schema); scale=np.std(encoded,axis=0); scale[scale==0]=1
    z=(encoded-np.mean(encoded,axis=0))/scale
    distance=NearestNeighbors(n_neighbors=2).fit(z).kneighbors(z)[0][:,1]
    joblib.dump({'reference':z,'mean':np.mean(encoded,axis=0),'scale':scale,'threshold':float(np.quantile(distance,.95))},ARTIFACTS/'ood.joblib',compress=3)
    json_write(ARTIFACTS/'evidence.json',{'targets':records,'protocol':{'outer':f'5 folds × {repeats} repeats, stratified','inner':'3-fold stratified search, 6 predeclared candidates','calibration':'Sigmoid, 3-fold out-of-fold calibration inside each outer training partition; ensemble=False','selection':'Inner ROC-AUC - 0.25 × Brier; select parameters per family, then family. No outer labels used.','threshold':.5,'seed':SEED,'ci':'95% patient-stratified bootstrap (1,000 resamples) of repeat-averaged OOF probabilities; conditional on fitted folds, not external validation','pooled':'Each patient occurs once after averaging their held-out predictions across repeats. Fold SD is descriptive; folds overlap.','isotonic':'Sensitivity comparison only; not selected on outer test data. Sigmoid predeclared for the small cohort.','shap':'Permutation SHAP of exact calibrated probability, 16 training-background patients, 6 held-out patients per outer fold; approximate correlated-feature attributions.','limitations':['Single 303-patient referral cohort; no external validation','Independent targets may be inconsistent; CAD is not forced to vessel union','Bootstrap intervals omit retraining and selection uncertainty','No validated clinical decision thresholds','Vessel predictions may be substantially weaker than overall CAD']},'dataset':{'name':'UCI Extension of Z-Alizadeh Sani','n':303,'columns':59,'eligible_inputs':55,'missing':0,'duplicates':0,'sha256':source_hash,'source':'https://archive.ics.uci.edu/dataset/411/extention+of+z+alizadeh+sani+dataset','doi':'10.24432/C5461K','license':'CC BY 4.0','empty_sheet':'Sheet1 has headers only; ignored'},'leakage':{'excluded':list(TARGETS.values()),'status':'PASS','input_count':55,'constant_features':[f['name'] for f in schema if f['constant']],'label_union_disagreements':int(np.sum(ys['CAD']!=((ys['LAD']+ys['LCX']+ys['RCA'])>0))),'audit_experiment':{'description':'Deliberately invalid identity predictor uses each target as its own input: AUC=1 by construction. Guard rejects it. No invalid model is trained or deployed.','invalid_identity_auc':{t:float(roc_auc_score(y,y)) for t,y in ys.items()}}},'runtime_seconds':float(time.perf_counter()-start)})
    json_write(ARTIFACTS/'registry.json',{'version':'vesselrisk-1.0','created_utc':datetime.now(timezone.utc).isoformat(),'dataset_sha256':source_hash,'seed':SEED,'models':registry,'libraries':{n:importlib.metadata.version(n) for n in ['numpy','pandas','scikit-learn','xgboost','shap','joblib']}})
    write_manifest()
    print(f'Finished in {time.perf_counter()-start:.1f}s',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--repeats',type=int,default=2); args=parser.parse_args()
    if args.repeats<2: parser.error('Use at least 2 repeats for submission evidence')
    train(args.repeats)
