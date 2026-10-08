"""Check persisted-estimator compatibility before any joblib deserialization."""
import importlib.metadata
import json
from pathlib import Path
import sys


class ModelCompatibilityError(RuntimeError):
    pass


def check_model_compatibility(registry=None):
    if registry is None:
        path = Path(__file__).resolve().parent / 'artifacts/registry.json'
        registry = json.loads(path.read_text(encoding='utf-8'))
    expected = registry['libraries']['scikit-learn']
    try:
        actual = importlib.metadata.version('scikit-learn')
    except importlib.metadata.PackageNotFoundError:
        actual = 'not installed'
    if actual != expected:
        raise ModelCompatibilityError(
            'Incompatible scikit-learn version.\n'
            f'Model artifacts were built with {expected}; installed: {actual}.\n'
            'Run: python scripts/start.py --setup'
        )


if __name__ == '__main__':
    try:
        check_model_compatibility()
    except ModelCompatibilityError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
