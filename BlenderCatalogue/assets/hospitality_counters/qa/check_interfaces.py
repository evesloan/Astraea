"""Native GLB-node/accessor checks using triangle BVH, not source meshes.
No render. Reports source and exchange frames explicitly; wrong-axis and blocked controls.
"""
import json,struct,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
FMT={5121:('B',1),5123:('H',2),5125:('I',4),5126:('f',4)};W={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def C(p):return [p[0],p[2],-p[1]]
def load(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n]);off=20+n;ln=struct.unpack_from('<I',raw,off)[0];blob=raw[off+8:off+8+ln]
 def arr(idx):
  a=d['accessors'][idx];b=d['bufferViews'][a['bufferView']];code,size=FMT[a['componentType']];w=W[a['type']];offset=b.get('byteOffset',0)+a.get('byteOffset',0);stride=b.get('byteStride',w*size)
  return [struct.unpack_from('<'+code*w,blob,offset+i*stride) for i in range(a['count'])]
 def mat(node):
  if'matrix'in node:return Matrix([node['matrix'][i::4] for i in range(4)])
  r=node.get('rotation',[0,0,0,1]);q=Quaternion((r[3],r[0],r[1],r[2]));m=q.to_matrix().to_4x4();m.translation=Vector(node.get('translation',[0,0,0]));s=node.get('scale',[1,1,1]);return m@Matrix.Diagonal((*s,1))
 parts=[]
 def walk(i,parent):
  node=d['nodes'][i];m=parent@mat(node)
  if'mesh'in node:
   vs=[];fs=[]
   for p in d['meshes'][node['mesh']]['primitives']:
    off=len(vs);vs.extend(m@Vector(x) for x in arr(p['attributes']['POSITION']));ix=[x[0] for x in arr(p['indices'])];fs.extend(tuple(off+j for j in ix[k:k+3]) for k in range(0,len(ix),3))
   parts.append({'name':node.get('name',''),'extras':node.get('extras',{}),'verts':vs,'faces':fs,'bvh':BVHTree.FromPolygons(vs,fs,all_triangles=True)})
  for j in node.get('children',[]):walk(j,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,Matrix.Identity(4))
 return parts

def aggregate(parts):
 v=[];f=[]
 for p in parts:off=len(v);v+=p['verts'];f += [tuple(x+off for x in tri) for tri in p['faces']]
 return BVHTree.FromPolygons(v,f,all_triangles=True)
def near(parts,p):return min(x['bvh'].find_nearest(Vector(p))[3] for x in parts)
def ray(tree,start,direction,length):
 p,n,i,d=tree.ray_cast(Vector(start),Vector(direction),length);return{'blocked':p is not None,'hit_distance_m':d,'hit_point_glb_m':list(p) if p is not None else None}
report={'scope':'Native actual GLB triangle/query evidence; component geometry only, no room/actor/physics claim','assets':[]};loaded={}
for ident in['AST-HSP-001','AST-HSP-002']:
 path=BASE/'exports'/f'{ident}.glb';parts=load(path);loaded[ident]=parts;tree=aggregate(parts);rec=json.loads((BASE/f'{ident}.manifest.json').read_text());out={'catalogue_id':ident,'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'contacts':[],'opening_probes':[]};checks=[]
 for p in rec['physical_contacts']:
  selected=[x for x in parts if p['surface'] in x['extras'].get('semantic_parts','')];distance=near(selected,p['glb_m']);wrong=near(selected,p['source_m']);out['contacts'].append({'name':p['name'],'kind':p['kind'],'source_m':p['source_m'],'native_glb_m':p['glb_m'],'nearest_native_mesh_distance_m':distance,'wrong_axis_control_distance_m':wrong,'passes':distance<1e-6 and wrong>.002});checks.append(distance<1e-6 and wrong>.002)
 # Staff ray path ends before the closed guest-facing shell. Material-free free space is real.
 probes=[]
 if ident=='AST-HSP-001':
  for x in [.18,.4,.67,1.05,1.35,1.75,2,2.22]:
   for z in [.26,.38]:probes.append((f'lower_open_bay_{x}_{z}',[x,.75,z],[0,-1,0],.95))
  for x in[.18,.4,.67,1.75,2,2.22]:
   for z in[.56,.73]:probes.append((f'upper_open_bay_{x}_{z}',[x,.75,z],[0,-1,0],.95))
 else:
  for t in [.24,.785,1.33]:
   for z in[.26,.38,.55,.73]:
    v=[math.sin(t),-math.cos(t),0];start=[v[0]*.10,.62+v[1]*.10,z];probes.append((f'inner_curve_opening_{t}_{z}',start,v,.63))
 for label,start,direction,length in probes:
  result=ray(tree,C(start),C(direction),length);out['opening_probes'].append({'name':label,'source_start_m':start,'source_direction':direction,'length_m':length,**result});checks.append(not result['blocked'])
 # Sensitive positive obstacle control: point into the same real compartment's metal shelf.
 if ident=='AST-HSP-001':start=[.4,0,.65]
 else:
  t=.785;start=[.62*math.sin(t),.62*(1-math.cos(t)),.65]
 blocked=ray(tree,C(start),C([0,0,-1]),.3);out['blocked_shelf_control']=blocked;checks.append(blocked['blocked'])
 out['passes']=all(checks);report['assets'].append(out)
# Matching top seam measured against source records expressed in actual GLB frame.
left=loaded['AST-HSP-001'];right=loaded['AST-HSP-002'];p_left=[2.399,.90,0];p_right=[.001,.90,0];da=near(left,p_left);db=near(right,p_right)
report['join']={'source_placement_return_translation_m':[2.4,0,0],'glb_placement_return_translation_m':[2.4,0,0],'straight_top_seam_native_glb_m':p_left,'turn_top_seam_local_native_glb_m':p_right,'straight_distance_to_mesh_m':da,'turn_distance_to_mesh_m':db,'physical_joint_gap_m':.002,'passes':da<1e-6 and db<1e-6}
report['all_passed']=all(x['passes'] for x in report['assets']) and report['join']['passes'];(BASE/'qa/interface_checks.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_INTERFACE_CHECKS',report['all_passed']);assert report['all_passed']
