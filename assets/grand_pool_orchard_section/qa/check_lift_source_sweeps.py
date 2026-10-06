"""Actual source cabin and gate meshes swept through new shaft derivatives. Engine interlocks remain pending."""
from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003';D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load_geom(path,choose=lambda o:True):
 bpy.ops.wm.open_mainfile(filepath=str(path));out=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH'or not choose(o):continue
  o.data.calc_loop_triangles();out.append({'name':o.name,'verts':[tuple(o.matrix_world@v.co)for v in o.data.vertices],'tris':[list(t.vertices)for t in o.data.loop_triangles],'parent':o.parent.name if o.parent else None})
 return out

def combined(rows,transform=lambda p:p):
 vv=[];ff=[];labels=[]
 for o in rows:
  k=len(vv);vv += [Vector(transform(p))for p in o['verts']];ff += [[k+i for i in face]for face in o['tris']];labels += [o['name']]*len(o['tris'])
 return vv,ff,labels

def floor_rows(floors):
 out=[]
 for f in floors:
  vv=[];ff=[]
  for t in f['triangles']:
   k=len(vv);vv += [(x,-z,y)for y in[f['floor_y']-f['thickness'],f['floor_y']]for x,z in t];ff += [[k+i for i in face]for face in[(2,1,0),(3,4,5),(0,1,4),(0,4,3),(1,2,5),(1,5,4),(2,0,3),(2,3,5)]]
  out.append({'name':f['id'],'verts':vv,'tris':ff,'parent':None})
 return out
local_static=load_geom(R/'source/AST-AQU-016.blend',lambda o:o.name.startswith('GP_LocalLift'))
staff_static=load_geom(R/'source/AST-STF-009_pool_market.blend',lambda o:o.name.startswith(('STF_Shaft','GPM_STF_Upper','GPM_STF_NewCap')))
assert not any(o['name'].startswith('STF_ShaftTopCap')for o in staff_static)
local_cabin=load_geom(C/'assets/commons_lift_cabin/source/AST-CIR-003.blend')
staff_cabin=load_geom(C/'assets/commons_lift_cabin/source/AST-CIR-003_five_stop.blend')
gates=load_geom(C/'assets/telescoping_gate/source/AST-DOR-003.blend')
gate_manifest=json.loads((C/'assets/telescoping_gate/AST-DOR-003.manifest.json').read_text());leaf_specs=gate_manifest.get('leaves',gate_manifest.get('leaf_specs'))
assert leaf_specs,gate_manifest.keys()
original=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions'];report=[]
for label,static,cabin,cx,cz,lo,hi,stops,spacing in[('local_wet_market',local_static,local_cabin,-13.6,-412.4,46.2,52.5,[46.2,52.5],.05),('preserved_staff_plus_upper',staff_static,staff_cabin,-23.2,-490,0,52.5,[0,6,12,46.2,52.5],.2)]:
 relevant=[f for f in D['floor_regions']+original if f['floor_y']>=lo-.24 and f['floor_y']<=hi+3]
 static=static+floor_rows(relevant);sv,sf,sl=combined(static);tree=BVHTree.FromPolygons(sv,sf,all_triangles=True,epsilon=1e-6)
 cv,cf,cl=combined(cabin,lambda p:(cx-p[1],-(cz-p[0]),p[2]))
 # Gate body travels with cabin0.12m behind the platform front, local gateY maps worldX.
 gv,gf,gl=combined(gates,lambda p:(cx-.12+p[1],-(cz+p[0]),p[2]))
 k=len(cv);base_v=cv+gv;base_f=cf+[[k+i for i in f]for f in gf];base_l=cl+gl
 positions=sorted(set([lo+(hi-lo)*i/max(1,math.ceil((hi-lo)/spacing))for i in range(max(1,math.ceil((hi-lo)/spacing))+1)]+stops));hits=[]
 for y in positions:
  vv=[p+Vector((0,0,y))for p in base_v];t=BVHTree.FromPolygons(vv,base_f,all_triangles=True,epsilon=1e-6);cross=tree.overlap(t)
  if cross:hits.append({'floor_y':y,'pairs':[{'static':sl[a],'moving':base_l[b]}for a,b in cross[:12]]})
 # Landing leaf swept volumes at each actual stop. Static fitted frame overlap is intentional; moving leaves alone must clear.
 leaf_steps=0
 for y in stops:
  for f in[0,.1,.25,.5,.75,.9,1]:
   rows=[]
   for o in gates:
    spec=next((s for s in leaf_specs if s['node']==o['parent']),None)
    if spec is None:continue
    dx=spec['travel_x_m']*f
    rows.append({**o,'verts':[(v[0]+dx,v[1],v[2])for v in o['verts']]})
   v,faces,names=combined(rows,lambda p:(cx+.12+p[1],-(cz+p[0]),y+p[2]));leaf_steps+=1;t=BVHTree.FromPolygons(v,faces,all_triangles=True,epsilon=1e-6);cross=tree.overlap(t)
   if cross:hits.append({'stop_y':y,'open_fraction':f,'pairs':[{'static':sl[a],'leaf':names[b]}for a,b in cross[:12]]})
 report.append({'assembly':label,'pass':not hits,'moving_cabin_and_closed_gate_source_meshes':len(cabin)+len(gates),'moving_triangles':len(base_f),'translation_samples':len(positions),'max_translation_step_m':spacing,'all_stop_y':stops,'landing_leaf_fraction_samples':leaf_steps,'top_cabin_y':hi+2.94,'shaft_cap_bottom_y':55.6,'nominal_roof_gap_m':55.6-(hi+2.94),'hits':hits})
out={'input_sha256':{str(p.relative_to(R)):sha(p)for p in[R/'source/connected_contract.json',R/'source/AST-AQU-016.blend',R/'exports/AST-AQU-016.glb',R/'source/AST-STF-009_pool_market.blend']},'pass':all(r['pass']for r in report),'scope':'Actual held source meshes against new shaft surfaces and declared/current floors. No physics engine, interlock, boarding, loose-load motion or control acceptance','assemblies':report,'cabin_source_hashes':{'AST-CIR-003':sha(C/'assets/commons_lift_cabin/source/AST-CIR-003.blend'),'AST-CIR-003_five_stop':sha(C/'assets/commons_lift_cabin/source/AST-CIR-003_five_stop.blend'),'AST-DOR-003':sha(C/'assets/telescoping_gate/source/AST-DOR-003.blend')}}
(R/'qa/lift_source_sweeps.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert out['pass']
