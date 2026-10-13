"""Package portable application source, trained models, assets and documentation."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from submission_files import EXCLUDED_DIRS, EXCLUDED_FILES, collect_files, validate_required

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'submission'


def package():
    OUTPUT.mkdir(exist_ok=True)
    files = collect_files(ROOT)
    validate_required(p.relative_to(ROOT).as_posix() for p in files)
    manifest = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    manifest_path = ROOT / 'review/FILE_MANIFEST.json'
    manifest_path.parent.mkdir(exist_ok=True)
    manifest_path.write_text(json.dumps({
        'root': 'VesselRisk', 'files': manifest,
        'note': 'Portable source. Run python scripts/start.py --setup. The manifest itself is not hashed.',
        'excluded': sorted(EXCLUDED_DIRS | EXCLUDED_FILES),
    }, indent=2) + '\n', encoding='utf-8')
    archive = OUTPUT / 'VesselRisk-Track-A-review.zip'
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=6) as zipped:
        for path in files + [manifest_path]:
            zipped.write(path, 'VesselRisk/' + path.relative_to(ROOT).as_posix())
    with ZipFile(archive) as zipped:
        assert zipped.testzip() is None, 'Archive CRC failure'
        validate_required(n.removeprefix('VesselRisk/') for n in zipped.namelist())
        for item in manifest:
            data = zipped.read('VesselRisk/' + item['path'])
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (OUTPUT / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(f'Created {archive.name}: {archive.stat().st_size / 1024**2:.2f} MiB, '
          f'{len(files) + 1} files; CRC, file hashes and required assets verified.')


if __name__ == '__main__':
    package()
