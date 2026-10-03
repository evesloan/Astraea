"""Independently materialize author keep roles after source-only generation; never original seeds."""
from pathlib import Path
import json,hashlib,sys,shutil,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
family,rev=sys.argv[1:3];rp=OUT/f'rebuild_{family}_{rev}.json';r=json.loads(rp.read_text());assert r['passed']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):
    p=Path(p);return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
rebuilt=ROOT/r['stage']/'assets'/family;original=ROOT/'assets'/family
basepath=rebuilt/'collision_proposals.json';base=json.loads(basepath.read_text());assert sha(basepath)==sha(original/'collision_proposals.json')
stage=OUT/f'stage2_{family}_{rev}';assert not stage.exists();stage.mkdir()
selector=stage/'select_body_stage2.py';shutil.copyfile(OUT/'select_body_stage2.py',selector)
detailed=stage/'generated_stage1_detailed_collision.json';shutil.copyfile(basepath,detailed)
spec={'detailed_sha256':sha(detailed),'purpose':'Author original keep-role declarations recovered from independently rebuilt editable sources; generated-stage2 selection config, never original production input','assets':{}}
evidence=[]
for row in r['editable_sources']:
    ident=row['catalogue_id'];ap=ROOT/row['audit_bindings'][1]['path'];audit=json.loads(ap.read_text());assert sha(ap)==row['audit_bindings'][1]['sha256'];parts={o['name']:o['properties']for o in audit['objects']if o['type']=='MESH'}
    shapes=base[ident].get('shapes',base[ident].get('precise_reference'));retained=[];omitted=[]
    for shape in shapes:
        name=shape.get('source_part',shape.get('covered_parts',[None])[0]);props=parts[name];keep=props.get('body_candidate_retained',props.get('body_candidate_keep'));assert isinstance(keep,(bool,int))
        (retained if keep else omitted).append(shape['name'])
    spec['assets'][ident]={'retained_shape_names':retained,'omitted_shape_names':omitted}
    if 'optional_body_candidate'in base[ident]:
        body=base[ident]['optional_body_candidate'];assert retained==body['retained_shape_names']and omitted==body['omitted_shape_names']
    elif (rebuilt/'actor_proxies/body_collision_subset.json').exists():
        body=json.loads((rebuilt/'actor_proxies/body_collision_subset.json').read_text())[ident];assert body['shapes']==[s for s in shapes if s['name']in retained]
    evidence.append({'catalogue_id':ident,'original_source':row['current_source'],'rebuilt_source':row['rebuilt_source'],'source_audit':bind(ap),'detailed_shape_count':len(shapes),'retained_shape_count':len(retained),'omitted_shape_count':len(omitted),'author_choice_matches_editable_source_keep_roles':True})
selection=stage/'generated_selection_from_stage1_editable_source.json';selection.write_text(json.dumps(spec,indent=2)+'\n')
seeds=[bind(p)for p in [selector,detailed,selection]];outputs=[]
for n in(1,2):
    op=stage/f'body_subset_run{n}.json';cmd=[sys.executable,str(selector),'--detailed',str(detailed),'--selection',str(selection),'--output',str(op)];run=subprocess.run(cmd,cwd=stage,capture_output=True,text=True);assert run.returncode==0,run.stderr
    outputs.append({'output':bind(op),'command':cmd,'returncode':run.returncode})
assert outputs[0]['output']['sha256']==outputs[1]['output']['sha256']
receipt={'passed':True,'family':family,'revision':rev,'source_only_stage1_receipt':bind(rp),'stage2_original_inputs':False,'stage2_exact_inputs':seeds,'stage1_generated_detailed_dependency':bind(basepath),'production_detailed_dependency':bind(original/'collision_proposals.json'),'selection_provenance':evidence,'two_repetitions_byte_identical':True,'outputs':outputs,'source_selector':bind(OUT/'select_body_stage2.py'),'executed_script':bind(Path(__file__)),'invariants':'Each retained entire detailed shape dictionary is copied unchanged in source order. Voids, motion records and original owners remain exact. No enclosing hull, inflation or movement is introduced. Literal subset under the same owner transforms cannot add an intrusion at any pose; omitted fine detail remains omitted. No distance, fit, physical adequacy or engine acceptance claim.'}
if(original/'actor_proxies/body_collision_subset.json').exists():receipt['production_body_subset']=bind(original/'actor_proxies/body_collision_subset.json');receipt['rebuilt_body_subset']=bind(rebuilt/'actor_proxies/body_collision_subset.json');assert sha(original/'actor_proxies/body_collision_subset.json')==sha(rebuilt/'actor_proxies/body_collision_subset.json')
(OUT/f'stage2_{family}_{rev}.json').write_text(json.dumps(receipt,indent=2)+'\n');print('STAGE2_PASS',family,[(r['catalogue_id'],r['detailed_shape_count'],r['retained_shape_count'])for r in evidence])
