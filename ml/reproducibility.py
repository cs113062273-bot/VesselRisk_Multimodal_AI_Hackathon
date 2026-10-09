"""A checkpoint is reusable only under the exact training protocol."""
import hashlib
import importlib.metadata
import json
import platform

from ml.schema import ROOT, SEED
from ml.integrity import digest


def checkpoint_protocol(source_hash, repeats, target, schema):
    sources = ['ml/train.py', 'ml/modeling.py', 'ml/schema.py', 'ml/reproducibility.py']
    libraries = ['numpy', 'pandas', 'scipy', 'scikit-learn', 'xgboost', 'shap', 'joblib']
    return {
        'version': 1, 'source_hash': source_hash, 'repeats': repeats,
        'target': target, 'seed': SEED, 'schema': schema,
        'python': platform.python_version(),
        'libraries': {name: importlib.metadata.version(name) for name in libraries},
        'code': {name: digest(ROOT / name) for name in sources},
    }


def fingerprint(protocol):
    return hashlib.sha256(json.dumps(protocol, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def checkpoint_matches(saved, protocol):
    return saved.get('protocol_sha256') == fingerprint(protocol) and saved.get('protocol') == protocol
