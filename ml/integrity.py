"""Verify the complete inference artifact set before deserializing estimators."""
import hashlib
import json

from ml.schema import ARTIFACTS, ROOT


def digest(path):
    content = path.read_bytes()
    # Git may convert text line endings between desktop Windows and Linux CI.
    # Preserve all other bytes; binary estimators always use their exact bytes.
    if path.suffix in {'.json', '.py'}:
        content = content.replace(b'\r\n', b'\n')
    return hashlib.sha256(content).hexdigest()


def write_manifest(root=ROOT, artifacts=ARTIFACTS):
    registry = json.loads((artifacts / 'registry.json').read_text(encoding='utf-8'))
    paths = [artifacts / name for name in ['registry.json', 'evidence.json', 'ood.joblib']]
    paths += [artifacts / record['file'] for record in registry['models'].values()]
    paths += [root / 'data/data_dictionary/features.json']
    manifest = {'version': 1, 'files': {p.relative_to(root).as_posix(): digest(p) for p in paths}}
    (artifacts / 'integrity.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def verify_manifest(root=ROOT, artifacts=ARTIFACTS):
    try:
        manifest = json.loads((artifacts / 'integrity.json').read_text(encoding='utf-8'))
        registry = json.loads((artifacts / 'registry.json').read_text(encoding='utf-8'))
        required = {f'ml/artifacts/{name}' for name in ['registry.json', 'evidence.json', 'ood.joblib']}
        required.update(f'ml/artifacts/{r["file"]}' for r in registry['models'].values())
        required.add('data/data_dictionary/features.json')
        if manifest['version'] != 1 or set(manifest['files']) != required:
            raise ValueError('incomplete manifest')
        for name, expected in manifest['files'].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root.resolve()) or digest(path) != expected:
                raise ValueError(name)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise RuntimeError(f'Artifact integrity check failed: {error}. Restore the paired artifact set.') from error
    return manifest


if __name__ == '__main__':
    # Explicit packaging step for trusted files, never performed by API startup.
    write_manifest()
    verify_manifest()
    print('Inference artifact manifest written and verified.')
