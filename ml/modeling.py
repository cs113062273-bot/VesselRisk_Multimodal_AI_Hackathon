import numpy as np
import shap
from scipy.special import logit
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, brier_score_loss
from xgboost import XGBClassifier
from ml.schema import LeakageGuard, SEED, encode_frame, decode_frame


def candidates(X, schema):
    cats = [f['name'] for f in schema if f['kind'] == 'category' and f['name'] in X]
    nums = [c for c in X if c not in cats]
    pre = ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median')), ('scale', StandardScaler())]), nums),
        ('category', Pipeline([('impute', SimpleImputer(strategy='most_frequent')), ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cats),
    ])
    models = [
        ('Logistic regression', {'C': c}, LogisticRegression(C=c, class_weight='balanced', max_iter=2500, random_state=SEED)) for c in [.1, 1.0]
    ] + [
        ('Random forest', {'min_samples_leaf': leaf}, RandomForestClassifier(n_estimators=120, min_samples_leaf=leaf, max_features=.7, class_weight='balanced_subsample', random_state=SEED, n_jobs=1)) for leaf in [3, 8]
    ] + [
        ('XGBoost', {'max_depth': depth}, XGBClassifier(n_estimators=110, max_depth=depth, learning_rate=.04, subsample=.85, colsample_bytree=.8, reg_lambda=5, min_child_weight=4, random_state=SEED, n_jobs=2, tree_method='hist', eval_metric='logloss')) for depth in [2, 3]
    ]
    return [(name, params, Pipeline([('leakage', LeakageGuard()), ('preprocess', pre), ('model', m)])) for name, params, m in models]


def inner_select(X, y, schema, seed):
    """The outer test fold is never available to model or parameter selection."""
    inner = StratifiedKFold(3, shuffle=True, random_state=seed)
    scores = []
    best_by_family = {}
    for name, params, estimator in candidates(X, schema):
        p = cross_val_predict(estimator, X, y, cv=inner, method='predict_proba', n_jobs=1)[:, 1]
        # Ranking is predeclared; calibration and final evaluation happen separately.
        auc, brier = roc_auc_score(y, p), brier_score_loss(y, p)
        score = auc - .25 * brier
        record = {'family': name, 'params': params, 'auc': float(auc), 'brier': float(brier), 'selection_score': float(score)}
        scores.append(record)
        if name not in best_by_family or score > best_by_family[name][0]:
            best_by_family[name] = (score, estimator, params)
    name = max(best_by_family, key=lambda n: best_by_family[n][0])
    return name, best_by_family, scores


def calibrated(estimator, X, y, seed, method='sigmoid'):
    # ensemble=False uses held-out calibration scores and then refits the base
    # pipeline on the entire training partition. All preprocessing stays inside CV.
    model = CalibratedClassifierCV(estimator, method=method, cv=StratifiedKFold(3, shuffle=True, random_state=seed), ensemble=False)
    return model.fit(X, y)


def explain(model, frame, background, schema, cycles=2, seed=SEED):
    """Model-agnostic permutation SHAP on the exact calibrated probability.

    One categorical feature is one coalition; no misleading one-hot partial categories.
    Background comes exclusively from the relevant training partition.
    """
    b = encode_frame(background, schema)
    values = encode_frame(frame, schema)
    def predict(z):
        return model.predict_proba(decode_frame(z, schema))[:, 1]
    explainer = shap.PermutationExplainer(predict, b, seed=seed, feature_names=[f['name'] for f in schema])
    result = explainer(values, max_evals=(2 * len(schema) + 1) * cycles, batch_size=4096, silent=True)
    probabilities = model.predict_proba(frame)[:, 1]
    error = np.max(np.abs(result.base_values + result.values.sum(axis=1) - probabilities))
    if error > 1e-6:
        raise RuntimeError(f'SHAP probability reconstruction failed: {error}')
    return result
