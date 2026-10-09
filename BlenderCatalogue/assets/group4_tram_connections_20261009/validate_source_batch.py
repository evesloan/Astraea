from pathlib import Path
import json,struct,hashlib,math,numpy as np
O=Path(__file__).resolve().parent;R=O.parents[2]
rows=json.load(open(O/'MESH_PARTS.json'));meta=json.load(open(O/'BATCH_INTERFACE.json'))
def glb(file):
 b=(O/file).read_bytes();assert b[:4]==b'glTF';assert struct.unpack_from('<I',b,8)[0]==len(b);n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b[28+n:]
def a(d,b,n):
 q=d['accessors'][n];v=d['bufferViews'][q['bufferView']];dt={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[q['componentType']];w={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[q['type']]
 return np.ndarray((q['count'],w),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+q.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dt).itemsize*w),np.dtype(dt).itemsize)).copy()
checks=[]
for f in ['AST-TRM-G4-001_fore_midship_source.glb','AST-TRM-G4-002_cart_tram_component.glb','AST-TRM-G4-003_aft_midship_source.glb','AST-TRM-G4-004_forward_source.glb','AST-TRM-G4-005_central_source.glb','AST-TRM-G4-006_aft_source.glb']:
 d,b=glb(f);cnt=0;tc=0;bad=0
 for n in d['nodes']:
  if 'mesh' not in n:continue
  for pr in d['meshes'][n['mesh']]['primitives']:
   v=a(d,b,pr['attributes']['POSITION']);idx=a(d,b,pr['indices']).reshape(-1);assert np.isfinite(v).all();assert idx.max()<len(v);t=v[idx.reshape(-1,3)];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);bad+=int((area<1e-9).sum());tc+=len(t);cnt+=1
   native=next(row for row in rows if row['mesh']==n['name']);assert np.allclose(v.min(axis=0),native['min'],atol=1e-5) and np.allclose(v.max(axis=0),native['max'],atol=1e-5)
 checks.append({'export':f,'sha256':hashlib.sha256((O/f).read_bytes()).hexdigest(),'mesh_primitives':cnt,'triangles':tc,'degenerate_triangles':bad,'file_size':(O/f).stat().st_size,'node_transforms':'baked Godot Y-up positions; actual import remains root'});assert bad==0
# Compact named floor/ceiling/vehicle dimensions and correct reserved axis.
fore=[r for r in rows if r['collection']=='FORE_MIDSHIP_STATIC_SOURCE'];aft=[r for r in rows if r['collection']=='AFT_MIDSHIP_STATIC_SOURCE'];car=[r for r in rows if r['collection']=='TRAM_EDITABLE_COMPONENT']
assert len(fore)==len(aft)
for r in fore:
 arow=next(a for a in aft if a['mesh']=='Aftmid_'+r['mesh']);assert np.allclose(arow['min'],[r['min'][0],r['min'][1],-r['max'][2]]);assert np.allclose(arow['max'],[r['max'][0],r['max'][1],-r['min'][2]])
axis_obstacles=[r['mesh'] for r in fore if r['min'][0]<2-1e-6 and r['max'][0]>-2+1e-6 and r['min'][1]<55.55-1e-6 and r['max'][1]>52.5+1e-6]
assert not axis_obstacles,axis_obstacles
assert max(r['max'][1] for r in car)<=3.001
assert len([r for r in fore if r['role']=='stair tread; actual top'])==24
# Source does NOT create the old cart or any products.
d,_=glb('AST-TRM-G4-002_cart_tram_component.glb');assert not any(n.get('name','') in ['CustodialCart','custodian_cart_001'] or n.get('name','').startswith('CartCleanerBottle') for n in d['nodes'])
materials={f:hashlib.sha256((R/f).read_bytes()).hexdigest()==v for f,v in meta['source_material_sha256'].items()};assert all(materials.values())
# Actual installed floors, bounded witnesses only. Multiple owners reported, never inferred as new floors.
ss=json.load(open(R/'Game/data/generated/structural_meshes.json'))
def inside(p,t):
 def sg(a,b,c):return (a[0]-c[0])*(b[1]-c[1])-(b[0]-c[0])*(a[1]-c[1])
 vals=[sg(p,t[0],t[1]),sg(p,t[1],t[2]),sg(p,t[2],t[0])];return not(min(vals)<-1e-7 and max(vals)>1e-7)
w=[]
for z in [-248,-240,-232,-224,-216,-208,-200,-192,-184,184,192,200,208,216,224,232,240,248]:
 for x in [-2.4,2.4]:
  owners=[r['id'] for r in ss['regions'] if r['floor_y']==52.5 and any(inside((x,z),t) for t in r['triangles'])];w.append({'xyz':[x,52.5,z],'owners':owners});assert len(owners)==1
pit=[r for r in fore if r['role'] in ['lift enclosure side','lift enclosure rear','pit source; bounded lower recess required']]
boundlo=[min(r['min'][i] for r in pit) for i in range(3)];boundhi=[max(r['max'][i] for r in pit) for i in range(3)]
report={'status':'SOURCE_COMPONENT_GEOMETRY_PASS_WITH_RECEIVING_HOLDS','source_only':True,'export_checks':checks,'native_part_counts':{'foremid':len(fore),'aftmid':len(aft),'vehicle':len(car)},'exact_mirrored_source_geometry':True,'four_m_pedestrian_axis_obstacles':axis_obstacles,'source_clear_headroom_m':3.05,'matched_existing_materials':materials,'guideway_footpad_existing_floor_witnesses':w,'actual_low_lift_housing_and_pan_bounds_xyz':{'min':boundlo,'max':boundhi},'pit_cut_warning':'Use actual exported low envelope with margin, not only cabin4x3.6 sweep; receiving cut requires root compiler proof','unchanged_material_pins_verified':True,'not_run':['Godot imports','actual-main physics','whole-line movement','full scene collision screen','guest transport/controller/state integration','structural capacity','final in-engine visual/user-GPU acceptance']}
(O/'SOURCE_BATCH_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'export_checks':checks,'counts':report['native_part_counts'],'footpad_witnesses':len(w),'axis_obstacles':axis_obstacles,'actual_pit_bounds':report['actual_low_lift_housing_and_pan_bounds_xyz']},indent=2))
