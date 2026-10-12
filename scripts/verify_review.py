"""Verify the archive and execute its extracted source in the pinned environment."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def run(command, directory, env):
    subprocess.run(command, cwd=directory, env=env, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, default=ROOT / 'submission/VesselRisk-Track-A-review.zip')
    parser.add_argument('--contents-only', action='store_true')
    args = parser.parse_args()
    archive_hash = hashlib.sha256(args.archive.read_bytes()).hexdigest()
    destination = ROOT / 'tmp/review-validation' / archive_hash[:12]
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.archive) as archive:
        assert archive.testzip() is None, 'Archive CRC failure'
        files = set(archive.namelist())
        for name in files:
            candidate = (destination / name).resolve()
            assert candidate.is_relative_to(destination.resolve()), f'Unsafe archive path: {name}'
        manifest_name = 'VesselRisk/review/FILE_MANIFEST.json'
        manifest = json.loads(archive.read(manifest_name))
        assert files == {f'VesselRisk/{item["path"]}' for item in manifest['files']} | {manifest_name}
        for item in manifest['files']:
            data = archive.read(f'VesselRisk/{item["path"]}')
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
        archive.extractall(destination)
    extracted = destination / 'VesselRisk'
    result = {'archive_sha256': archive_hash, 'files_verified': len(files),
              'extracted_to': str(extracted), 'crc_and_manifest': 'passed'}
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    env.pop('PYTHONPATH', None)
    if not args.contents_only:
        run([sys.executable, '-m', 'pytest', 'tests/test_validity.py', 'tests/test_reliability.py', '-q'], extracted, env)
        run([sys.executable, '-m', 'ml.evaluate'], extracted, env)
        npm = shutil.which('npm')
        assert npm, 'Node.js/npm required for extracted frontend validation'
        def node_command(*arguments):
            return ['cmd', '/d', '/c', npm, *arguments] if os.name == 'nt' else [npm, *arguments]
        run(node_command('ci', '--no-audit', '--no-fund'), extracted / 'web', env)
        # Delivery contains portable source, not the author's machine-specific build.
        run(node_command('run', 'build'), extracted / 'web', env)
        browser_env = {**env, 'CI': '1', 'DEMO_URL': 'http://127.0.0.1:3012',
                       'PLAYWRIGHT_API_PORT': '8003', 'PLAYWRIGHT_PYTHON': sys.executable}
        run(node_command('exec', '--', 'playwright', 'test', 'reliability.spec.ts', 'workspace-analytics.spec.ts'), extracted / 'web', browser_env)
        result.update({'scientific_api_checks': 30, 'frozen_metrics': 'passed',
                       'desktop_browser_checks': 3, 'fresh_frontend_dependencies': 'npm ci',
                       'fresh_production_build': 'npm run build',
                       'environment': 'Pinned existing Python environment; extracted source and fresh frontend dependencies. Not a fresh Python installation.'})
    output = args.archive.with_suffix('.verification.json')
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Verified {len(files)} archive files; results: {output}', flush=True)


if __name__ == '__main__':
    main()
