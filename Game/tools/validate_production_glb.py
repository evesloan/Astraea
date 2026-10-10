"""Reject presentation-only geometry before publishing production GLBs.

Original catalogue/authoring files may retain presentation geometry. Call
validate(path) before copying each successor into production. The optional
Star Atlas selection audits active specialty bindings, not archived originals.
"""
from pathlib import Path
import argparse,json,struct,hashlib,shutil

def preview_only(name,extras):
    normalized=''.join(c for c in str(name).lower() if c.isalnum())
    return 'previewground' in normalized or any(extras.get(k) is True for k in ('preview_only','presentation_only','exclude_from_production'))

def inspect(path):
    path=Path(path);raw=path.read_bytes()
    if len(raw)<20 or raw[:4]!=b'glTF' or struct.unpack_from('<I',raw,4)[0]!=2:raise ValueError('Expected GLB version2')
    length,kind=struct.unpack_from('<II',raw,12)
    if kind!=0x4E4F534A or length>len(raw)-20:raise ValueError('Invalid GLB JSON chunk')
    data=json.loads(raw[20:20+length]);bad=[{'name':n.get('name',''),'runtime_collision':n.get('extras',{}).get('runtime_collision'),'extras':n.get('extras',{})}for n in data.get('nodes',[]) if 'mesh' in n and preview_only(n.get('name',''),n.get('extras',{}))]
    return {'file':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'preview_only_meshes':bad}

def validate(path):
    result=inspect(path)
    if result['preview_only_meshes']:raise ValueError('Presentation-only geometry in production GLB: '+', '.join(n['name'] for n in result['preview_only_meshes']))
    return result

def validate_and_copy(source,destination):
    result=validate(source)
    shutil.copy2(source,destination)
    if hashlib.sha256(Path(destination).read_bytes()).hexdigest()!=result['sha256']:raise ValueError('Production copy hash mismatch')
    return result

def star_atlas_files(game):
    paths=set();architecture=Path(game)/'data/architecture'
    for batch in ('FIRST','SECOND','THIRD','FOURTH'):
        p=json.loads((architecture/f'STAR_ATLAS_SPECIALTY_{batch}.json').read_text())
        paths.update(r['model_file']for r in p['rooms'])
        paths.add(p['receiving']['model_file'])
        if p['receiving'].get('commons_patch_file'):paths.add(p['receiving']['commons_patch_file'])
    for filename in ('STAR_ATLAS_EIGHT_HABITATS.json','STAR_ATLAS_SPECIALTY_STRUCTURAL_RECEIVING.json'):
        p=json.loads((architecture/filename).read_text());paths.add(p.get('runtime_model_file',p.get('model_file')))
    return [Path(game)/'assets/models'/p for p in sorted(paths)if p]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('files',nargs='*');parser.add_argument('--star-atlas-specialty',type=Path);parser.add_argument('--receipt',type=Path);a=parser.parse_args();paths=[Path(p)for p in a.files]+(star_atlas_files(a.star_atlas_specialty)if a.star_atlas_specialty else [])
    if not paths:parser.error('Supply GLB files or --star-atlas-specialty Game')
    rows=[inspect(p)for p in paths];bad=sum(len(r['preview_only_meshes'])for r in rows);report={'status':'FAIL'if bad else'PASS','scope':'Only selected production GLBs; original authoring history may retain preview objects','files':rows,'model_count':len(rows),'preview_only_mesh_count':bad}
    if a.receipt:a.receipt.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'model_count':len(rows),'preview_only_mesh_count':bad}));return 1 if bad else 0
if __name__=='__main__':raise SystemExit(main())
