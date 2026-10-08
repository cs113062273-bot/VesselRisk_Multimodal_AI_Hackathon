"""One-command local launch. --setup installs an isolated pinned environment."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]


def npm_cmd(*args):
    npm=shutil.which('npm')
    if not npm:
        raise SystemExit('Install Node.js 22+ (including npm), then run this command again.')
    return ['cmd','/d','/c',npm,*args] if os.name=='nt' else [npm,*args]


def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--setup',action='store_true',help='Create .venv, install pinned dependencies and build the frontend')
    parser.add_argument('--dev',action='store_true',help='Use Next.js development mode')
    parser.add_argument('--port',type=int,default=3000)
    parser.add_argument('--api-port',type=int,default=8000)
    args=parser.parse_args()
    venv=ROOT/'.venv'
    python=venv/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if args.setup:
        if not python.exists():subprocess.run([sys.executable,'-m','venv',str(venv)],check=True)
        subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements-dev.txt')],check=True,cwd=ROOT)
        subprocess.run(npm_cmd('ci','--no-audit','--no-fund'),check=True,cwd=ROOT/'web')
        subprocess.run(npm_cmd('run','build'),check=True,cwd=ROOT/'web')
    if not python.exists():python=Path(sys.executable)
    if not (ROOT/'ml/artifacts/registry.json').exists():
        subprocess.run([str(python),'-m','ml.train'],check=True,cwd=ROOT)
    compatible=subprocess.run([str(python),'-m','ml.compatibility'],cwd=ROOT)
    if compatible.returncode:
        raise SystemExit(compatible.returncode)
    if not (ROOT/'web/node_modules').exists():
        subprocess.run(npm_cmd('ci','--no-audit','--no-fund'),check=True,cwd=ROOT/'web')
    env={**os.environ,'API_URL':f'http://127.0.0.1:{args.api_port}','NEXT_TELEMETRY_DISABLED':'1','PYTHONIOENCODING':'utf-8'}
    if not args.dev and not (ROOT/'web/.next/BUILD_ID').exists():
        subprocess.run(npm_cmd('run','build'),check=True,cwd=ROOT/'web',env=env)
    api=None; web=None
    try:
        api=subprocess.Popen([str(python),'-m','uvicorn','api.main:app','--host','127.0.0.1','--port',str(args.api_port)],cwd=ROOT,env=env)
        ready=False
        for _ in range(120):
            if api.poll() is not None:raise RuntimeError('The API exited during startup. Inspect the error above.')
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{args.api_port}/health',timeout=1) as response:
                    if response.status==200:ready=True;break
            except OSError:time.sleep(.5)
        if not ready:raise RuntimeError('The API did not become healthy within 60 seconds.')
        web=subprocess.Popen(npm_cmd('run','dev' if args.dev else 'start','--','--port',str(args.port)),cwd=ROOT/'web',env=env)
        print(f'\nVesselRisk: http://127.0.0.1:{args.port}\nAPI docs: http://127.0.0.1:{args.api_port}/docs\nPress Ctrl+C to stop both services.\n',flush=True)
        while api.poll() is None and web.poll() is None:time.sleep(1)
        if api.poll() is not None or web.poll() is not None:raise RuntimeError('A service stopped. Inspect its error above.')
    except KeyboardInterrupt:
        print('\nStopping VesselRisk…')
    finally:
        for process in [web,api]:
            if process and process.poll() is None:
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                else:process.terminate()


if __name__=='__main__':run()
