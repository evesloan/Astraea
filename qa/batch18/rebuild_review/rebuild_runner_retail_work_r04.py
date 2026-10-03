"""Reviewer-owned exact input-closure rebuild and independent semantic/export comparison."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil,os,traceback,argparse
import numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('family',choices=['retail_display','retail_work']);parser.add_argument('revision');parser.add_argument('--generator');args=parser.parse_args()
family=args.family;rev=args.revision;source=ROOT/'assets'/family
stage=OUT/f'stage_{family}_{rev}';assert not stage.exists(),'Preserve previous stage';stage.mkdir()
dest=OUT/f'rebuild_{family}_{rev}.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):
    p=Path(p);return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
receipt={'passed':False,'family':family,'revision':rev,'stage':str(stage.relative_to(ROOT)),'executed_script_sha256':sha(Path(__file__)),'commands':[]}
for tool in [Path(__file__),OUT/'rebuild_instrument.py',OUT/'rebuild_source_audit.py']:
    archive=OUT/f'{tool.stem}_{family}_{rev}.py';assert not archive.exists();shutil.copyfile(tool,archive)
receipt['exact_reviewer_code_snapshots']=[bind(OUT/f'{name}_{family}_{rev}.py')for name in ['rebuild_runner','rebuild_instrument','rebuild_source_audit']]
def run(cmd,log,cwd):
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    with log.open('w')as f:result=subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
    receipt['commands'].append({'argv':cmd,'cwd':str(cwd),'returncode':result.returncode,'log':bind(log)})
    if result.returncode:raise RuntimeError(f'Command failed ({result.returncode}); {log}')
def differing(a,b,path='$'):
    if type(a)!=type(b):return [path+': type']
    if isinstance(a,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b:out.append(path+'.'+k+': missing')
            else:out.extend(differing(a[k],b[k],path+'.'+k))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [path+': length']
        return [d for i,(x,y)in enumerate(zip(a,b))for d in differing(x,y,path+f'[{i}]')]
    return []if a==b else[path]
try:
    dp=source/'dependency_manifest.json';dep=json.loads(dp.read_text());receipt['declared_dependency_manifest']=bind(dp)
    inputs=dep.get('source_only_inputs',dep.get('inputs'));assert inputs,'No declared original closure'
    seeds=[]
    for row in inputs:
        name=row.get('path_from_catalogue_root',row.get('path'));p=Path(name)
        assert not p.is_absolute()and'..'not in p.parts
        assert 'qa'not in p.parts and p.suffix not in{'.blend','.blend1','.glb'},name
        assert p.name not in {'collision_proposals.json','marker_api.json','body_collision_subset.json'} and not p.name.endswith('.manifest.json'), 'Generated interface/collision output cannot seed source-only rebuild: '+name
        assert not (p.parts[:2]==('assets',family) and p.name=='manifest.json' and len(p.parts)==3),name
        assert sha(ROOT/p)==row['sha256'],f'Declared input hash stale: {name}'
        seeds.append(name)
    assert len(seeds)==len(set(seeds))
    receipt['production_original_inputs']=[bind(ROOT/p)for p in sorted(seeds)]
    for name in seeds:
        p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
    receipt['seed_files']=sorted(str(p.relative_to(stage))for p in stage.rglob('*')if p.is_file())
    assert receipt['seed_files']==sorted(seeds)
    receipt['fresh_stage_exact_declared_original_inputs']=True
    generator=args.generator or next(p for p in seeds if p.startswith(f'assets/{family}/source/build')and p.endswith('.py'))
    assert generator in seeds
    trace=OUT/f'build_reads_{family}_{rev}.json';instrument=OUT/f'rebuild_instrument_{family}_{rev}.py'
    cmd=['blender','--background','--threads','1','--python-exit-code','1','--python',str(instrument),'--',str(stage/generator),str(stage),str(ROOT),str(trace)]
    run(cmd,OUT/f'build_{family}_{rev}.log',stage)
    tr=json.loads(trace.read_text());receipt['file_read_trace']=bind(trace);receipt['instrumentation_script']=bind(instrument)
    receipt['child_python_read_traces']=[]
    for child in tr.get('child_python_runs',[]):
        cp=Path(child['trace']);ct=json.loads(cp.read_text());assert not ct['failure'],ct['failure']
        receipt['child_python_read_traces'].append(bind(cp));tr['python_open_events']+=ct['python_open_events'];tr['actual_blender_image_files']+=ct['actual_blender_image_files']
    # Native image witnesses include save-pre states, avoiding final-scene-only coverage.
    reads=sorted(set(x['path']for x in tr['python_open_events']if x['scope']=='stage'and x['mode'].startswith('r'))|{x['path']for x in tr['actual_blender_image_files']if x['scope']=='stage'})
    foreign=[x for x in tr['python_open_events']if x['scope']=='outside_stage_catalogue'and x['mode'].startswith('r')]+[x for x in tr['actual_blender_image_files']if x['scope']=='outside_stage_catalogue']
    receipt['observed_catalogue_reads']=reads;receipt['outside_stage_catalogue_reads']=foreign
    assert not foreign,foreign
    generated_reads=[p for p in reads if p not in seeds and not p.endswith('.pyc')]
    for name in generated_reads:assert(stage/name).is_file(),f'Attempted undeclared absent read: {name}'
    receipt['freshly_generated_files_reopened']=generated_reads
    receipt['original_inputs_unchanged_through_generation']=all(sha(ROOT/r['path'])==r['sha256']for r in receipt['production_original_inputs'])
    assert receipt['original_inputs_unchanged_through_generation'],'Production modified during rebuild'
    produced=[]
    current_exports=sorted((source/'exports').glob('AST-*.glb'));rebuilt_exports=sorted((stage/'assets'/family/'exports').glob('AST-*.glb'))
    assert [p.name for p in current_exports]==[p.name for p in rebuilt_exports]
    for p in current_exports:
        q=stage/p.relative_to(ROOT);produced.append({'current':bind(p),'rebuilt':bind(q),'byte_identical':sha(p)==sha(q)})
    receipt['actual_exports']=produced
    paths=sorted((stage/'assets'/family/'source').glob('AST-*.blend'));originals=[source/'source'/p.name for p in paths]
    assert paths and all(p.exists()for p in originals)
    audit=OUT/f'rebuild_source_audit_{family}_{rev}.py';prefixes=[f'production_{family}_{rev}_',f'rebuilt_{family}_{rev}_']
    for label,pp,prefix in zip(['production','rebuilt'],[originals,paths],prefixes):
        run(['blender','--background','--threads','1','--python-exit-code','1','--python',str(audit),'--','--prefix',prefix]+[str(p)for p in pp],OUT/f'audit_{label}_{family}_{rev}.log',ROOT)
    receipt['source_audit_script']=bind(audit);results=[];sourcehashpairs={}
    for p,original in zip(paths,originals):
        sp=OUT/f'{prefixes[0]}source_{p.stem}.json';rp=OUT/f'{prefixes[1]}source_{p.stem}.json';s=json.loads(sp.read_text());r=json.loads(rp.read_text())
        assert s['sha256']==sha(original)and r['sha256']==sha(p)
        sourcehashpairs[s['sha256']]=r['sha256']
        exclude={'path','sha256','geometry_cache','executed_script_sha256','used_images'}
        semanticdiff=differing({k:v for k,v in s.items()if k not in exclude},{k:v for k,v in r.items()if k not in exclude})
        # Image paths can differ only by fresh stage prefix; identities, sizes, packed bytes are exact.
        images=lambda row:[{k:v for k,v in im.items()if k!='filepath'}for im in row['used_images']]
        imagediff=differing(images(s),images(r))
        a=np.load(ROOT/s['geometry_cache']);b=np.load(ROOT/r['geometry_cache']);geometry=all(np.array_equal(a[k],b[k])for k in ['triangles','object_names','material_names'])
        results.append({'catalogue_id':p.stem,'current_source':bind(original),'rebuilt_source':bind(p),'audit_bindings':[bind(sp),bind(rp)],'evaluated_geometry_equal':geometry,'editable_geometry_uv_normals_material_graph_hierarchy_properties_equal':not semanticdiff,'semantic_differences':semanticdiff[:100],'packed_image_identity_size_and_bytes_equal':not imagediff,'image_differences':imagediff,'pass':geometry and not semanticdiff and not imagediff})
    receipt['editable_sources']=results
    # Do not delete arbitrary hash fields. Only a source_sha256 value actually bound above may change.
    normalizations=[]
    def normalize_pair(a,b,path='$'):
        if isinstance(a,dict)and isinstance(b,dict):
            a=dict(a);b=dict(b)
            for k in a.keys()&b.keys():
                if k=='source_sha256'and a[k]in sourcehashpairs and b[k]==sourcehashpairs[a[k]]:
                    normalizations.append({'json_path':path+'.'+k,'production':a[k],'rebuilt':b[k]});a[k]=b[k]='VERIFIED_SOURCE_CONTAINER_HASH'
                else:a[k],b[k]=normalize_pair(a[k],b[k],path+'.'+k)
        elif isinstance(a,list)and isinstance(b,list)and len(a)==len(b):
            pairs=[normalize_pair(x,y,path+f'[{i}]')for i,(x,y)in enumerate(zip(a,b))];a=[x[0]for x in pairs];b=[x[1]for x in pairs]
        return a,b
    json_rows=[]
    for p in sorted((stage/'assets'/family).rglob('*.json')):
        if 'qa'in p.relative_to(stage/'assets'/family).parts or str(p.relative_to(stage))in seeds:continue
        q=ROOT/p.relative_to(stage);assert q.exists(),f'Generated JSON absent in production: {q}'
        a,b=normalize_pair(json.loads(q.read_text()),json.loads(p.read_text()),p.name);diff=differing(a,b)
        json_rows.append({'current':bind(q),'rebuilt':bind(p),'equal_except_verified_source_container_hashes':not diff,'differences':diff[:100]})
    receipt['generated_interface_and_manifest_json']=json_rows;receipt['legitimate_source_hash_normalizations']=normalizations
    art=[]
    for p in sorted((stage/'assets'/family).rglob('*')):
        if not p.is_file()or str(p.relative_to(stage))in seeds or p.suffix not in {'.png','.jpg','.svg'}:continue
        q=ROOT/p.relative_to(stage);assert q.exists(),q
        art.append({'current':bind(q),'rebuilt':bind(p),'byte_identical':sha(q)==sha(p)})
    receipt['regenerated_original_artwork']=art
    shared=[]
    for p in sorted((stage/'materials'/'retail').glob('*')):
        if not p.is_file() or str(p.relative_to(stage)) in seeds or p.suffix not in {'.png','.json'}:continue
        q=ROOT/p.relative_to(stage);assert q.exists(),q
        shared.append({'current':bind(q),'rebuilt':bind(p),'byte_identical':sha(q)==sha(p)})
    receipt['regenerated_shared_retail_artwork_and_manifest']=shared
    assert {Path(x['current']['path']).name for x in shared}=={'retail_terracotta_enamel.png','manifest.json'}, 'Shared enamel must regenerate in clean stage from original script'
    assert all(x['byte_identical']for x in shared)
    receipt['passed']=all(r['byte_identical']for r in produced)and all(r['pass']for r in results)and all(r['equal_except_verified_source_container_hashes']for r in json_rows)and all(r['byte_identical']for r in art)
    receipt['limits']='No render or source modification. Original source-container bytes may differ through stored stage paths; only verified source_sha256 fields are normalized. Export byte identity proves actual native geometry, UV, normals, materials and hierarchy reproduction, not physical adequacy. Source audit checks editable mesh topology/UV/normals, modifiers, drivers, shape keys, transforms, material node graphs/properties and packed image bytes. Python audit is not syscall complete; Blender/Python standard resources are execution environment dependencies. Generated collision profiles are not original inputs; any body selection from them is a separate stage2.'
except BaseException as exc:
    receipt['error']=str(exc);receipt['traceback']=traceback.format_exc()
    dest.write_text(json.dumps(receipt,indent=2)+'\n')
    raise
dest.write_text(json.dumps(receipt,indent=2)+'\n')
print('INDEPENDENT_REBUILD',family,rev,receipt['passed'],'exports',len(receipt['actual_exports']),'sources',len(receipt['editable_sources']),'art outputs',len(receipt['regenerated_original_artwork']),flush=True)
sys.exit(0 if receipt['passed']else 2)
