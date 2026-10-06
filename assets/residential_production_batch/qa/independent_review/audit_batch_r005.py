"""Read-only audit of supplied bytes. No Blender, Godot, imports or mutation."""
import json, struct, hashlib, math, re, collections
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
def js(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def decode(p):
 b=Path(p).read_bytes(); assert b[:4]==b'glTF' and struct.unpack_from('<II',b,4)==(2,len(b))
 o=12;chunks={}
 while o<len(b):
  n,t=struct.unpack_from('<II',b,o);o+=8;assert o+n<=len(b);chunks[t]=b[o:o+n];o+=n
 assert o==len(b)
 j=json.loads(chunks[0x4e4f534a]);blob=chunks[0x004e4942]
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];c={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];d=np.dtype({5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]);assert 'sparse'not in a
  assert v.get('buffer',0)==0
  return np.ndarray((a['count'],c),dtype=d,buffer=blob,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',d.itemsize*c),d.itemsize)).copy()
 marks={};triangles=[];materials=[]
 def visit(i,M,seen):
  assert i not in seen;seen=seen|{i};n=j['nodes'][i]
  if 'matrix'in n:m=np.array(n['matrix']).reshape(4,4,order='F')
  else:
   x,y,z,w=n.get('rotation',(0,0,0,1));m=np.eye(4);m[:3,:3]=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])@np.diag(n.get('scale',(1,1,1)));m[:3,3]=n.get('translation',(0,0,0))
  m=M@m;name=n.get('name','');assert np.isfinite(m).all()
  if name.startswith('DATUM_'):assert name not in marks;marks[name]=m[:3,3]
  if 'mesh'in n:
   for p in j['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4;v=acc(p['attributes']['POSITION']);q=(np.c_[v,np.ones(len(v))]@m.T)[:,:3];ix=acc(p['indices']).reshape(-1);assert len(ix)%3==0 and max(ix)<len(v);tr=q[ix].reshape(-1,3,3);assert np.isfinite(tr).all();triangles.append(tr);materials.extend([j.get('materials',[])[p['material']]['name']]*len(tr))
  for c in n.get('children',[]):visit(c,m,seen)
 for i in j['scenes'][j.get('scene',0)]['nodes']:visit(i,np.eye(4),set())
 return j,np.concatenate(triangles),marks,materials

def readblend(path):
 b=path.read_bytes();assert b[:7]==b'BLENDER';ptr=8 if b[7:8]==b'-'else 4;e='<'if b[8:9]==b'v'else '>';h=e+'4sI'+('Q'if ptr==8 else 'I')+'II';hs=struct.calcsize(h);o=12;blocks=[]
 while o+hs<=len(b):
  code,n,old,s,c=struct.unpack_from(h,b,o);o+=hs;blocks.append((code,old,s,c,b[o:o+n]));o+=n
  if code==b'ENDB':break
 D=next(d for c,a,s,n,d in blocks if c==b'DNA1');o=8
 def uint():
  nonlocal o
  v=struct.unpack_from(e+'I',D,o)[0];o+=4;return v
 def strs():
  nonlocal o
  arr=[]
  for i in range(uint()):k=D.index(b'\0',o);arr.append(D[o:k].decode());o=k+1
  o=(o+3)&~3;return arr
 names=strs();assert D[o:o+4]==b'TYPE';o+=4;types=strs();assert D[o:o+4]==b'TLEN';o+=4;sizes=struct.unpack_from(e+str(len(types))+'H',D,o);o+=2*len(types);o=(o+3)&~3;assert D[o:o+4]==b'STRC';o+=4;S=[]
 for i in range(uint()):
  t,n=struct.unpack_from(e+'HH',D,o);o+=4;f={};off=0
  for k in range(n):
   ft,fn=struct.unpack_from(e+'HH',D,o);o+=4;name=names[fn];c=math.prod(map(int,re.findall(r'\[(\d+)\]',name)));size=(ptr if '*'in name else sizes[ft])*c;f[name]=(types[ft],off,size);off+=size
  assert off==sizes[t];S.append((types[t],f))
 T=dict(S)
 def field(d,t,n): _,o,l=T[t][n];return d[o:o+l]
 def name(d):return field(d,'ID','name[66]').split(b'\0')[0].decode()
 libs=[];objects={}
 for c,a,s,n,d in blocks:
  t=S[s][0]if s<len(S)else None
  if t=='Library':libs.append(field(d,t,'name[1024]').split(b'\0')[0].decode())
  if t=='Object':
   nm=name(field(d,t,'id'))
   if nm.startswith('OBAST-UNIT-'):objects[nm[2:]]={'loc':struct.unpack(e+'3f',field(d,t,'loc[3]')),'rot':struct.unpack(e+'3f',field(d,t,'rot[3]'))}
 return libs,objects

plan=js(ROOT/'RESIDENTIAL_500_PLAN.json');protos=js(ROOT/'PROTOTYPE_PLAN.json');inst=js(ROOT/'outputs/production_r005/sections/GODOT_BATCH_INSTANCE_MAP.json');byproto={p['prototype_key']:p for p in protos['rooms']}
assert len(plan['rooms'])==500 and len(inst['instances'])==498
assert collections.Counter(r['historical_class']for r in plan['rooms'])=={'standard':200,'family':300}
assert len({r['rebuild_identity']for r in plan['rooms']})==500
assert len({r['census_source_index']for r in plan['rooms']})==500
assert {r['historical_address']for r in inst['preserved_installed']}=={'13017','13041'}
assert sum(len(r['bed_anchors'])for r in plan['rooms'])==1300
assert sha(ROOT/'inputs/REGULAR_500_SOURCE_CROSSWALK.json')==plan['source_crosswalk_sha256']
byaddress={r['address']:r for r in plan['rooms']}
assert len(plan['adjacency_edges'])==668 and all(byaddress[a]['layout']!=byaddress[b]['layout']for a,b in plan['adjacency_edges'])
input_hashes=[]
for r in js(ROOT/'qa/INPUT_RETENTION.json')['files']:input_hashes.append({'path':r['path'],'pass':Path(r['path']).is_file()and sha(r['path'])==r['sha256']})
assert all(r['pass']for r in input_hashes)
rows=[];glbs={};bounds={}
for p in protos['rooms']:
 d=ROOT/'outputs/production_r005'/p['address'];rc=js(d/'SOURCE_RECEIPT.json')
 assert rc['input_plan_sha256']==sha(ROOT/'PROTOTYPE_PLAN.json')
 assert all(sha(d/n)==h for n,h in rc['files'].items())
 j,t,marks,mats=decode(d/'shell.glb');glbs[p['prototype_key']]=(j,t,marks,mats)
 b=t.reshape(-1,3);slo,shi=rc['shell_stats']['source_bounds'];lo=[slo[0],slo[2],-shi[1]];hi=[shi[0],shi[2],-slo[1]];err=float(max(abs(b.min(0)-lo).max(),abs(b.max(0)-hi).max()));assert err<1e-5
 assert len(t)==rc['shell_stats']['triangles'] and len(j['meshes'])<=10
 for a in p['bed_anchors']:
  u,v,w=a['source_xyz'];assert np.linalg.norm(marks['DATUM_bed_'+str(a['historical_anchor_index'])]-[u,w,-v])<1e-5
 assert (any('glass'in m.lower()for m in mats))==(p['view_policy']=='real_atrium_candidate')
 rows.append({'prototype':p['address'],'instances':p['prototype_instance_count'],'hashes_pass':True,'triangles':len(t),'batches':len(j['meshes']),'bounds_error':err,'node_extras_count':sum('extras'in n for n in j['nodes'])})
 bounds[p['prototype_key']]=(b.min(0),b.max(0))
bindings=[];mismatches=[];props=[];worlderr=0
cross={r['source_envelope_index']:r for r in js(ROOT/'inputs/REGULAR_500_SOURCE_CROSSWALK.json')['records']}
for r in inst['instances']:
 assert all(r[k]==byaddress[r['address']][k]for k in byaddress[r['address']] if k!='occupant_props_variant')
 p=byproto[r['prototype_key']];_,_,marks,_=glbs[r['prototype_key']];rc=js(ROOT/'outputs/production_r005'/p['address']/'SOURCE_RECEIPT.json')
 if r.get('requested_occupant_props_variant',r['occupant_props_variant'])!=p['occupant_props_variant']:props.append(r['address'])
 for a in r['bed_anchors']:
  q=[q for q in p['bed_anchors']if q['source_xyz']==a['source_xyz']];assert len(q)==1;q=q[0]
  pi=q['historical_anchor_index'];ai=a['historical_anchor_index'];x,y,z=marks['DATUM_bed_'+str(pi)];ang=r['source_yaw_godot'];world=np.array([math.cos(ang)*x+math.sin(ang)*z,y,-math.sin(ang)*x+math.cos(ang)*z])+r['source_origin_world_xyz'];er=float(np.linalg.norm(world-a['world_xyz']));worlderr=max(worlderr,er);assert er<1e-5
  if pi!=ai:mismatches.append({'address':r['address'],'instance_anchor_index':ai,'prototype_anchor_index':pi})
  bindings.append({'address':r['address'],'instance_anchor_index':ai,'prototype_anchor_index':pi,'prototype_datum':'DATUM_bed_'+str(pi),'source_xyz':a['source_xyz'],'world_xyz':a['world_xyz'],'proposed_slot_id':cross[r['census_source_index']]['proposed_rest_slot_ids'][ai]})
 for k in ['allocation_sha256','allocation_x','allocation_z','historical_door_marker_xz']:assert r[k]==cross[r['census_source_index']][k]
libs,objects=readblend(ROOT/'outputs/production_r005/sections/Astraea_500_regular_family_portable.blend')
assert len(libs)==17 and len(objects)==498
assert all(p.startswith('//')and (ROOT/'outputs/production_r005/sections'/p[2:]).is_file()for p in libs)
maxloc=maxyaw=0
for r in inst['instances']:
 ob=objects[r['rebuild_identity']];x,y,z=r['source_origin_world_xyz'];err=max(abs(a-b)for a,b in zip(ob['loc'],(x,-z,y)));maxloc=max(maxloc,err);ye=abs(ob['rot'][2]-r['source_yaw_godot']);maxyaw=max(maxyaw,ye);assert err<2e-5 and ye<1e-6
report={'status':'PASS_INDEPENDENT_SOURCE_NUMERICAL_CHECKS_WITH_CONTRACT_FINDINGS','scope':'Read-only pure Python audit; no Blender/Godot/process/import/state modifications. Source acceptance only.','input_hashes_checked':len(input_hashes),'all_input_hashes_pass':True,'counts':{'units':500,'new_instances':498,'preserved':2,'prototypes':17,'anchors':1300,'adjacency_edges':668},'prototypes':rows,'max_instance_anchor_world_error_m':worlderr,'blend_decode':{'libraries':libs,'instances':len(objects),'max_location_error_m':maxloc,'max_yaw_error_radians':maxyaw,'all_actual_library_paths_package_relative':True},'prototype_ordinal_mismatches':mismatches,'rooms_with_ordinal_mismatch':len(set(m['address']for m in mismatches)),'per_instance_props_variant_not_realized_in_shared_prototype':props}
(OUT/'NUMERICAL_AUDIT_r005.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'EXPLICIT_ANCHOR_BINDING_REFERENCE_r005.json').write_text(json.dumps(bindings,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['prototypes','prototype_ordinal_mismatches','per_instance_props_variant_not_realized_in_shared_prototype','blend_decode']},indent=2));print('blend errors',maxloc,maxyaw,'unrealized props variants',len(props),'anchor ordinal mismatches',len(mismatches))

assert len({a['unit_slot_key']for r in inst['instances']for a in r['anchor_bindings']})==1296
for r in inst['instances']:
 p=byproto[r['prototype_key']];ref=[a for a in bindings if a['address']==r['address']]
 assert r['occupant_props_variant']==p['occupant_props_variant']
 assert r.get('requested_occupant_props_variant',r['occupant_props_variant'])==byaddress[r['address']]['occupant_props_variant']
 assert len(r['anchor_bindings'])==len(ref)
 for a in r['anchor_bindings']:
  q=next(q for q in ref if q['instance_index']==a['unit_anchor_index']) if any('instance_index'in q for q in ref)else next(q for q in ref if q['instance_anchor_index']==a['unit_anchor_index'])
  assert a['prototype_anchor_index']==q['prototype_anchor_index'] and a['unit_slot_key']==q['proposed_slot_id']
  assert a['source_xyz']==q['source_xyz'] and a['world_xyz']==q['world_xyz']
 assert not Path(r['shell_source']).is_absolute()and (ROOT/r['shell_source']).is_file()
 assert not Path(r['source_detail_props_layer']).is_absolute()and (ROOT/r['source_detail_props_layer']).is_file()
assert all(sha(ROOT/'inputs'/n)==h for n,h in js(ROOT/'qa/CURRENT_INPUT_FILE_HASHES.json')['files'].items())
summary=inst['summary']
for k,v in summary['prototype_sources'].items():
 assert sha(ROOT/v['source'])==v['sha256']and sha(ROOT/v['shell_glb'])==v['shell_glb_sha256']
for n,h in summary['source_files'].items():assert sha(ROOT/'outputs/production_r005/sections'/n)==h
props_rows=[]
for p in protos['rooms']:
 f=ROOT/'outputs/production_r005'/p['address']/'detail_props.glb';j,t,m,ma=decode(f)
 # Book-like possessions are extruded prisms: each contributes twelve triangles.
 expected=(5+p['occupant_props_variant'])*12
 assert len(t)==expected,(p['address'],len(t),expected)
 props_rows.append({'prototype':p['address'],'file':str(f.relative_to(ROOT)),'sha256':sha(f),'triangles':len(t),'expected_triangles':expected})
extra={'status':'PASS_CORRECTED_METADATA_AND_PORTABILITY','revision':'production_r005','explicit_slot_bindings':1296,'slot_keys_match_existing_schedule_proposals':True,'relative_source_paths_resolve':True,'prototype_source_and_section_hashes_pass':True,'current_input_hash_receipt_pass':True,'props_variation_realization_and_deferral_explicit':True,'detail_props':props_rows}
(OUT/'CORRECTED_CONTRACT_AUDIT_r005.json').write_text(json.dumps(extra,indent=2)+'\n')
print('PASS_CORRECTED_METADATA_AND_PORTABILITY')
