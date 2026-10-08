"""Extract real coronary geometry from a pinned BodyParts3D derivative."""
import hashlib
import json
from pathlib import Path
import numpy as np
import requests

ROOT = Path(__file__).resolve().parents[1]
REPO = 'ashemag/human-atlas'
REVISION = '1c38bf35c254a891200d3cedecfd57abebe83d8d'


def main():
    revision = REVISION
    base = f'https://raw.githubusercontent.com/{REPO}/{revision}/'
    r = requests.get(base+'public/models/atlas.json',timeout=30); r.raise_for_status()
    atlas = r.json()
    heart = {'FJ2428','FJ2438','FJ2439'}
    great = {'FJ2966','FJ3413','FJ3645','FJ2737'}
    parts = []
    for p in atlas['parts']:
        n = p['name'].lower()
        target = None
        if p['id'] == 'FJ2631' or 'left coronary artery' in n and ('anterior interventricular' in n or 'anterior descending' in n) or 'septal branch of anterior interventricular artery' in n:
            target = 'LAD'
        elif 'circumflex branch of left coronary artery' in n:
            target = 'LCX'
        elif 'right coronary artery' in n or 'right posterior interventricular artery' in n:
            target = 'RCA'
        if target or p['id'] in heart | great:
            parts.append({**p, 'target':target, 'surface':'heart' if p['id'] in heart else 'great' if p['id'] in great else 'artery'})
    assert all(any(p['target']==t for p in parts) for t in ['LAD','LCX','RCA'])
    chunks = {}
    for i in sorted({p['chunk'] for p in parts}):
        response = requests.get(base+'public'+atlas['chunks'][i]['url'],timeout=60); response.raise_for_status()
        chunks[i] = response.content
    vertices = [np.frombuffer(chunks[p['chunk']],dtype='<f4',count=p['vertexCount']*3,offset=p['positions']).reshape(-1,3) for p in parts if p['surface']=='heart']
    v = np.vstack(vertices); center = (v.min(axis=0)+v.max(axis=0))/2
    scale = 3.5/np.max(v.max(axis=0)-v.min(axis=0))
    content, manifest = bytearray(), []
    for p in parts:
        b = chunks[p['chunk']]
        positions = np.frombuffer(b,dtype='<f4',count=p['vertexCount']*3,offset=p['positions']).reshape(-1,3)
        positions = ((positions-center)*scale).astype('<f4')
        normals = np.frombuffer(b,dtype='<i2',count=p['vertexCount']*3,offset=p['normals']).astype('<f4')/32767
        indices = np.frombuffer(b,dtype='<u4',count=p['indexCount'],offset=p['indices'])
        offsets = []
        for array in [positions,normals,indices]:
            offsets.append(len(content)); content.extend(array.tobytes())
        manifest.append({'id':p['id'],'name':p['name'],'target':p['target'],'surface':p['surface'],
                         'positions':offsets[0],'normals':offsets[1],'indices':offsets[2],
                         'vertexCount':p['vertexCount'],'indexCount':p['indexCount']})
    out = ROOT/'web/public/anatomy'; out.mkdir(parents=True,exist_ok=True)
    (out/'heart.bin').write_bytes(content)
    metadata = {'parts':manifest,'bytes':len(content),'triangles':sum(p['indexCount']//3 for p in parts),
                'source':'BodyParts3D 4.0 / DBCLS','license':'CC BY 4.0',
                'upstream':f'https://github.com/{REPO}/tree/{revision}', 'revision':revision,
                'sha256':hashlib.sha256(content).hexdigest(),'adaptation':'Selected cardiac wall, great vessels and coronary branches; recentered and uniformly scaled; preserved real source geometry and IDs.',
                'mapping':'LAD anterior interventricular / anterior descending branches; LCX circumflex branches; RCA right coronary trunk and branches. Generic adult male anatomy, not a patient scan.'}
    (out/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    attr = requests.get(base+'public/ATTRIBUTION.md',timeout=30); attr.raise_for_status()
    (out/'UPSTREAM_ATTRIBUTION.md').write_text(attr.text,encoding='utf-8')
    print(f'{len(parts)} actual anatomical meshes; {len(content):,} bytes; {metadata["triangles"]:,} triangles; revision {revision}')


if __name__ == '__main__':
    main()
