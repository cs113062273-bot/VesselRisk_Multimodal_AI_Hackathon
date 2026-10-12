"""Select portable source, runtime assets and review evidence for public delivery."""
import argparse
import os
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    '.dockerignore', '.gitattributes', '.gitignore', 'AGENTS.md', 'ATTRIBUTIONS.md',
    'Dockerfile.api', 'LICENSE', 'README.md', 'Track A.pdf', 'compose.yaml',
    'pytest.ini', 'requirements.txt', 'requirements-dev.txt', 'train.py',
}
SOURCE_DIRS = {
    '.github', 'api', 'data', 'demo', 'docs', 'experiments',
    'extention+of+z+alizadeh+sani+dataset', 'ml', 'report', 'review', 'scripts', 'tests', 'web',
}
EXCLUDED_DIRS = {
    '.git', '.venv', 'node_modules', '__pycache__', '.pytest_cache', '.next',
    '.next-dev', 'test-results', 'playwright-report', 'tmp', 'submission',
}
EXCLUDED_FILES = {
    'docs/EXECUTION_PLAN.md', 'docs/FIRST_30_SECONDS.md',
    'docs/VISUAL_INTERACTION.md', 'docs/VISUAL_POLISH.md',
    'scripts/capture_first_look.mjs', 'scripts/capture_polish.mjs',
    'review/FILE_MANIFEST.json', 'review/RESEARCH_THRESHOLDS.json',
}
DEMO_SCREENSHOTS = {
    'patient-workspace.png', 'coronary-anatomy.png', 'focused-lad.png',
    'focused-lcx.png', 'focused-rca.png', 'prediction-changes.png',
}
ARTIFACTS = {
    'CAD.joblib', 'LAD.joblib', 'LCX.joblib', 'RCA.joblib', 'ood.joblib',
    'registry.json', 'evidence.json', 'integrity.json',
}
REQUIRED = {
    'README.md', 'LICENSE', 'ATTRIBUTIONS.md', 'requirements.txt', 'requirements-dev.txt',
    'scripts/start.py', 'scripts/submission_files.py', 'scripts/package_review.py',
    'scripts/verify_review.py', 'compose.yaml', 'Dockerfile.api', 'web/Dockerfile',
    '.github/workflows/verify.yml', 'pytest.ini', 'tests/test_validity.py',
    'tests/test_reliability.py', 'data/data_dictionary/features.json',
    'extention+of+z+alizadeh+sani+dataset/extention of Z-Alizadeh sani dataset.xlsx',
    'api/__init__.py', 'api/main.py', 'api/service.py', 'api/schemas.py',
    'ml/__init__.py', 'ml/schema.py', 'ml/modeling.py', 'ml/train.py',
    'ml/integrity.py', 'ml/compatibility.py', 'ml/reliability.py', 'ml/reproducibility.py',
    'experiments/reliability/results.json', 'experiments/vessel_refinement/results.json',
    'web/package.json', 'web/package-lock.json', 'web/next.config.ts', 'web/tsconfig.json',
    'web/app/page.tsx', 'web/app/layout.tsx', 'web/app/api/[...path]/route.ts',
    'web/lib/target-colors.ts', 'web/components/HeartViewer.tsx',
    'web/components/HeartViewer.module.css', 'web/components/ReliabilityDetails.tsx',
    'web/components/ModelEvidenceOverview.tsx', 'web/lib/input-provenance.ts',
    'web/public/anatomy/heart.bin', 'web/public/anatomy/manifest.json',
    'web/public/anatomy/UPSTREAM_ATTRIBUTION.md', 'report/VesselRisk-Track-A.pdf',
    'review/index.html', 'review/START_HERE.md', 'review/COMPLETION_SUMMARY.md',
    'review/BUILD_VALIDATION.json', 'review/screenshots/index.json',
    'demo/DEMO_SCRIPT.md', 'demo/DEMO_NARRATION_EN.md',
    'demo/DEMO_TIMELINE.json', 'demo/DEMO_REHEARSAL.json',
    'demo/CUSTOM_PROFILE_START.json', 'demo/CUSTOM_PROFILE_FINAL.json',
} | {f'ml/artifacts/{name}' for name in ARTIFACTS}


def included(name):
    path = PurePosixPath(name)
    parts = path.parts
    if not parts or path.is_absolute() or '..' in parts:
        return False
    if name in ROOT_FILES:
        return True
    if parts[0] not in SOURCE_DIRS or any(p in EXCLUDED_DIRS for p in parts):
        return False
    if name in EXCLUDED_FILES or path.name.startswith('.env'):
        return False
    if path.name.endswith(('.pyc', '.log', '.tsbuildinfo', '.checkpoint.joblib', '.checkpoint.joblib.tmp')):
        return False
    if path.name == 'evidence.partial.json':
        return False
    if parts[0] == 'review' and len(parts) > 2 and parts[1] != 'screenshots':
        return False
    if parts[:2] == ('demo', 'screenshots'):
        return len(parts) == 3 and path.name in DEMO_SCREENSHOTS
    if parts[:2] == ('ml', 'artifacts'):
        return len(parts) == 3 and path.name in ARTIFACTS
    return path.suffix.lower() in {
        '.py', '.mjs', '.ts', '.tsx', '.css', '.json', '.md', '.txt', '.csv',
        '.yaml', '.yml', '.svg', '.bin', '.xlsx', '.pdf', '.html', '.png',
    } or path.name in {'Dockerfile', '.dockerignore'}


def collect_files(root=ROOT):
    files = []
    for directory, dirs, names in os.walk(root):
        current = Path(directory)
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and
                         (current != root or d in SOURCE_DIRS) and
                         not (current == root / 'review' and d != 'screenshots'))
        for name in sorted(names):
            path = current / name
            if included(path.relative_to(root).as_posix()):
                files.append(path)
    return sorted(files)


def validate_required(names):
    missing = REQUIRED - set(names)
    if missing:
        raise RuntimeError('Missing submission files: ' + ', '.join(sorted(missing)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracked', action='store_true', help='Also check the Git index for excluded or missing files')
    args = parser.parse_args()
    files = collect_files()
    validate_required(p.relative_to(ROOT).as_posix() for p in files)
    print(f'Public source: {len(files)} files, {sum(p.stat().st_size for p in files) / 1024**2:.2f} MiB')
    if args.tracked:
        tracked = set(filter(None, subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')))
        validate_required(tracked)
        excluded = sorted(name for name in tracked if not included(name))
        if excluded:
            raise RuntimeError('Local-only files are still tracked: ' + ', '.join(excluded))
        print('Git index contains all required files and no excluded local-only artifacts.')


if __name__ == '__main__':
    main()
