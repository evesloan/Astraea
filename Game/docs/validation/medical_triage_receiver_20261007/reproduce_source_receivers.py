"""Read-only GLB/source correspondence checks; not an engine/runtime test."""
import json, struct, hashlib, itertools, copy
from pathlib import Path
import numpy as np
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3],help='Game project root')
parser.add_argument('--output',type=Path,required=True,help='New output directory outside the retained evidence package')
args=parser.parse_args()
ROOT=args.root.resolve()
OUT=args.output.resolve()
if OUT==Path(__file__).resolve().parent:
 parser.error('Choose a separate output directory to preserve retained evidence')
OUT.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(path):return json.loads((ROOT/path).read_text())
def matrix(node):
 if 'matrix' in node:return np.array(node['matrix'],dtype=float).reshape((4,4),order='F')
 x,y,z,w=node.get('rotation',[0,0,0,1]); sx,sy,sz=node.get('scale',[1,1,1])
 r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)], [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)], [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 m=np.eye(4);m[:3,:3]=r@np.diag([sx,sy,sz]);m[:3,3]=node.get('translation',[0,0,0]);return m
def glb(filename):
 b=(ROOT/'assets/models'/filename).read_bytes()
 assert b[:4]==b'glTF' and struct.unpack_from('<I',b,4)[0]==2 and struct.unpack_from('<I',b,8)[0]==len(b)
 n,k=struct.unpack_from('<II',b,12);assert k==0x4e4f534a
 g=json.loads(b[20:20+n]);world={}
 def descend(i,parent):
  assert i not in world,('duplicate glb parent',filename,i)
  world[i]=parent@matrix(g['nodes'][i])
  for child in g['nodes'][i].get('children',[]):descend(child,world[i])
 for root in g['scenes'][g.get('scene',0)]['nodes']:descend(root,np.eye(4))
 return g,world,sha(b)
def bounds(g,index,pose):
 node=g['nodes'][index];points=[]
 for p in g['meshes'][node['mesh']]['primitives']:
  a=g['accessors'][p['attributes']['POSITION']]
  for v in itertools.product(*zip(a['min'],a['max'])):points.append((pose@np.array([*v,1]))[:3])
 return np.min(points,axis=0),np.max(points,axis=0)
def contains(lower,upper,point,tolerance):return bool(np.all(point>=lower-tolerance) and np.all(point<=upper+tolerance))
def resolve(g,source_name,catalogue_id,filename):
 matches=[i for i,n in enumerate(g['nodes']) if n.get('name')==source_name];assert len(matches)==1,'source cardinality'
 si=matches[0];source=g['nodes'][si]
 if 'mesh' in source:return si,si
 assert source_name=='WALL_DIFFUSER' and catalogue_id=='AST-GST-002' and filename=='AST-GST-002.glb','source owner identity'
 extra=source.get('extras',{});assert extra.get('marker_kind')=='physical_receiver' and extra.get('physical_part')=='wall_recessed_diffuser','marker semantics'
 candidates=[i for i,n in enumerate(g['nodes']) if 'mesh' in n and extra['physical_part'] in json.loads(n.get('extras',{}).get('semantic_parts','[]'))]
 assert len(candidates)==1,'semantic receiver cardinality'
 ri=candidates[0];r=g['nodes'][ri]
 assert r['name']=='AST-GST-002__oatmeal_weave' and r.get('extras',{}).get('material_role')=='oatmeal_weave','receiver identity'
 return si,ri
runtime=read('data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json');evidence=read('tests/fixtures/medical_triage_010_expectations.json')
assert sha((ROOT/runtime['source_evidence_file'].removeprefix('res://')).read_bytes())==runtime['source_evidence_sha256']
fixtures={f['name']:f for f in runtime['fixtures']};instances={i['name']:i for i in runtime['instances']}
assert len(fixtures)==34 and len(instances)==74
root=np.eye(4);root[:3,3]=runtime['origin_xyz'];records=[];pins={}
for source in evidence['new_fixture_sources']:
 f=fixtures[source['name']];assert f['position_xyz']==source['position_xyz'] and f['aim_xyz']==source['aim_xyz'] and f['profile']==source['profile']
 owner=f['source_owner'];item=instances.get(owner)
 if item:
  filename=item['file'];yaw=item['yaw_radians'];pose=root@matrix({'rotation':[0,np.sin(yaw/2),0,np.cos(yaw/2)],'translation':item['local_xyz']});catalogue_id=item['catalogue_id']
  assert np.linalg.norm(pose[:3,3]-item['world_xyz'])<1e-8
 else:
  assert owner=='AuthoredMedicalWelcome';filename=runtime['architecture_file'];pose=root;catalogue_id=None
 g,world,h=glb(filename);pins[filename]=h;assert runtime['model_pins'][filename]==h
 si,ri=resolve(g,f['source_node'],catalogue_id,filename);lower,upper=bounds(g,ri,pose@world[ri]);exit=np.array(f['position_xyz']);source_pos=(pose@world[si])[:3,3]
 assert contains(lower,upper,exit,.35),('exit outside housing',f['name'])
 if si!=ri:assert contains(lower,upper,source_pos,.001),('marker detached',f['name'])
 records.append({'name':f['name'],'owner':owner,'model':filename,'source_node':g['nodes'][si]['name'],'source_is_mesh':si==ri,'visible_receiver':g['nodes'][ri]['name'],'receiver_world_bounds_xyz':[lower.tolist(),upper.tolist()],'marker_world_position_xyz':source_pos.tolist() if si!=ri else None,'light_exit_xyz':f['position_xyz'],'source_aim_xyz':f['aim_xyz'],'profile':f['profile'],'housing_check_passed':True})
assert len(records)==23 and sum(r['source_is_mesh'] for r in records)==15
# Negative source-only cases demonstrate rejection by the bounded correspondence rule.
g,_,_=glb('AST-GST-002.glb');neg=[]
for label,mutate in [
 ('wrong_marker_kind',lambda a:a['nodes'][9]['extras'].__setitem__('marker_kind','nonphysical_direction_target')),
 ('wrong_physical_part',lambda a:a['nodes'][9]['extras'].__setitem__('physical_part','wall_hollow_shield')),
 ('missing_semantic_receiver',lambda a:a['nodes'][3]['extras'].__setitem__('semantic_parts','[]')),
 ('duplicate_semantic_receiver',lambda a:a['nodes'].append(copy.deepcopy(a['nodes'][3]))),
 ('renamed_receiver',lambda a:a['nodes'][3].__setitem__('name','UnrelatedVisibleMesh')),
 ('wrong_material_role',lambda a:a['nodes'][3]['extras'].__setitem__('material_role','ivory_enamel')),
 ('duplicate_source_marker',lambda a:a['nodes'].append(copy.deepcopy(a['nodes'][9]))),
]:
 altered=copy.deepcopy(g);mutate(altered)
 try:resolve(altered,'WALL_DIFFUSER','AST-GST-002','AST-GST-002.glb')
 except AssertionError:neg.append({'case':label,'rejected':True})
 else:raise AssertionError(('accepted invalid mutation',label))
report={'status':'PASS_SOURCE_ONLY','scope':'GLB source correspondence and source-predicted bounds; no Godot execution, runtime visibility, raycast, physical or visual acceptance.', 'source_count':23,'marker_backed_sources':8,'mesh_backed_sources':15,'model_sha256':pins,'unchanged_optics_inputs':{p:sha((ROOT/p).read_bytes()) for p in ['data/architecture/D05_MEDICAL_WELCOME_RUNTIME.json','scripts/medical_welcome.gd','data/lighting_profiles.json','scripts/ship.gd']},'records':records,'negative_source_checks':neg}
(OUT/'SOURCE_RECEIVER_CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['records','unchanged_optics_inputs']},indent=2))
