from pathlib import Path
import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / 'ml' / 'artifacts'
DATA_PATH = ROOT / 'extention+of+z+alizadeh+sani+dataset' / 'extention of Z-Alizadeh sani dataset.xlsx'
TARGETS = {'CAD': 'Cath', 'LAD': 'LAD', 'LCX': 'LCX', 'RCA': 'RCA'}
FORBIDDEN = {'cath', 'cad', 'lad', 'lcx', 'rca'}
SEED = 2026


def guard_columns(columns):
    rejected = [c for c in columns if re.sub(r'[^a-z0-9]', '', str(c).lower()) in FORBIDDEN]
    if rejected:
        raise ValueError(f'Target leakage blocked: {rejected}')


class LeakageGuard(TransformerMixin, BaseEstimator):
    """Reject target names before every training and inference transformation."""
    def fit(self, X, y=None):
        guard_columns(X.columns)
        self.feature_names_in_ = np.array(X.columns)
        return self

    def transform(self, X):
        guard_columns(X.columns)
        if list(X.columns) != list(self.feature_names_in_):
            raise ValueError('Feature schema/order differs from fitted schema')
        return X


def load_data():
    frame = pd.read_excel(DATA_PATH, sheet_name='Sheet 1 - Table 1')
    if frame.shape != (303, 59) or frame.isna().any().any() or frame.duplicated().any():
        raise ValueError('Unexpected source workbook: inspect before retraining')
    X = frame.drop(columns=list(TARGETS.values()))
    guard_columns(X.columns)
    ys = {}
    for key, column in TARGETS.items():
        positive = 'CAD' if key == 'CAD' else 'Stenotic'
        if set(frame[column].unique()) != {positive, 'Normal'}:
            raise ValueError(f'Unexpected target vocabulary: {column}')
        ys[key] = (frame[column] == positive).astype(int).to_numpy()
    return X, ys, frame


LABELS = {
    'Length': 'Height', 'DM': 'Diabetes', 'HTN': 'Hypertension', 'FH': 'Family history',
    'CRF': 'Chronic renal failure', 'CVA': 'Cerebrovascular history', 'CHF': 'Heart failure history',
    'DLP': 'Dyslipidemia', 'BP': 'Systolic blood pressure', 'PR': 'Pulse rate',
    'FBS': 'Fasting blood sugar', 'CR': 'Creatinine', 'TG': 'Triglycerides',
    'LDL': 'LDL cholesterol', 'HDL': 'HDL cholesterol', 'BUN': 'Blood urea nitrogen',
    'ESR': 'ESR', 'HB': 'Hemoglobin', 'K': 'Potassium', 'Na': 'Sodium',
    'WBC': 'White blood cells', 'Lymph': 'Lymphocytes', 'Neut': 'Neutrophils', 'PLT': 'Platelets',
    'EF-TTE': 'Ejection fraction', 'Region RWMA': 'RWMA region code',
    'Tinversion': 'T-wave inversion', 'St Elevation': 'ST elevation', 'St Depression': 'ST depression',
    'VHD': 'Valvular heart disease', 'BBB': 'Bundle branch block', 'LVH': 'Left ventricular hypertrophy',
}
UNITS = {'Age': 'years', 'Weight': 'kg', 'Length': 'cm', 'BMI': 'kg/m²', 'BP': 'mmHg',
         'PR': 'bpm', 'FBS': 'mg/dL', 'CR': 'mg/dL', 'TG': 'mg/dL', 'LDL': 'mg/dL',
         'HDL': 'mg/dL', 'BUN': 'mg/dL', 'ESR': 'mm/h', 'HB': 'g/dL', 'K': 'mEq/L',
         'Na': 'mEq/L', 'WBC': 'cells/µL', 'Lymph': '%', 'Neut': '%', 'PLT': '10³/µL', 'EF-TTE': '%'}


def make_schema(X):
    features = []
    for i, c in enumerate(X.columns):
        group = 'Demographics & history' if i < 17 else 'Symptoms & examination' if i < 31 else 'ECG' if i < 38 else 'Laboratory & echo'
        vals = X[c].unique().tolist()
        categorical = X[c].dtype == object or (len(vals) <= 5 and c not in {'CR', 'K'})
        f = {'name': c, 'label': LABELS.get(c, c), 'group': group, 'unit': UNITS.get(c, ''),
             'kind': 'category' if categorical else 'number',
             'default': X[c].mode().iloc[0] if categorical else float(X[c].median()),
             'constant': len(vals) == 1, 'source_dtype': str(X[c].dtype)}
        if categorical:
            f['options'] = sorted(vals, key=str)
        else:
            f.update(min=float(X[c].min()), max=float(X[c].max()), integer=X[c].dtype.kind in 'iu')
        features.append(f)
    return features


def encode_frame(frame, schema):
    out = frame.copy()
    for f in schema:
        if f['kind'] == 'category':
            out[f['name']] = out[f['name']].map({v: i for i, v in enumerate(f['options'])})
    return out.to_numpy(dtype=float)


def decode_frame(values, schema):
    out = pd.DataFrame(values, columns=[f['name'] for f in schema])
    for f in schema:
        if f['kind'] == 'category':
            out[f['name']] = out[f['name']].round().astype(int).map(dict(enumerate(f['options'])))
    return out
