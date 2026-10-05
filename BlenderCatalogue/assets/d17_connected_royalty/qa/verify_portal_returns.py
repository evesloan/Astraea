"""Narrow eight-part correction versus retained afe3102; no engine work."""
from pathlib import Path
import bpy,json,hashlib,subprocess,tempfile
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];C=R.parents[1];BASE='afe3102';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for o in bpy.context.scene.objects:
  row={'type':o.type,'matrix':[list(r)for r in o.matrix_world],'props':{k:o[k]for k in o.keys()},'hide_render':o.hide_render,'display_type':o.display_type}
  if o.type=='MESH':row.update(vertices=[list(v.co)for v in o.data.vertices],faces=[list(f.vertices)for f in o.data.polygons],uv=[list(v.uv)for v in o.data.uv_layers.active.data],materials=[m.name for m in o.data.materials])
  out[o.name]=row
 return out
old_contract=json.loads(subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_connected_royalty/source/connected_contract.json']))
new_contract=json.loads((R/'source/connected_contract.json').read_text());assert new_contract['floor_regions']==old_contract['floor_regions']
for field in ['perimeter_xz','units_preserved','reservations','fixtures','markers','private_arrival','portal','reused_retained_parts']:
 assert new_contract[field]==old_contract[field],field
old_bytes=subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_connected_royalty/source/AST-RES-006.blend'])
with tempfile.NamedTemporaryFile(prefix='d17-portal-preservation-',suffix='.blend')as f:
 f.write(old_bytes);f.flush();old=snap(f.name)
new=snap(R/'source/AST-RES-006.blend');assert all(new.get(k)==v for k,v in old.items()),'Prior source object changed'
expected={f'CR_PortalReturn_{side}_{part}'for side in ['Left','Right']for part in ['Fascia','Base','Glass','Cap']};assert set(new)-set(old)==expected
for path in ['source/AST-COM-003_aft_only.blend','exports/AST-COM-003_aft_only.glb']:
 retained=subprocess.check_output(['git','-C',str(C),'show',BASE+':assets/d17_connected_royalty/'+path]);assert hashlib.sha256(retained).hexdigest()==sha(R/path),path
# Actual side rays through each return cover the entire former gap at four bands/heights.
meshes={};bounds={}
for name in expected:
 o=bpy.data.objects[name];vs=[o.matrix_world@v.co for v in o.data.vertices];meshes[name]=BVHTree.FromPolygons(vs,[list(p.vertices)for p in o.data.polygons]);bounds[name]=[(min(v[i]for v in vs),max(v[i]for v in vs))for i in range(3)]
 assert min(-v.y for v in vs)>=13.65-1e-5 and max(-v.y for v in vs)<=14+1e-5
checks=[]
for side,x,dx,apron in [('Left',78.5,-1,'22'),('Right',81.5,1,'01')]:
 for part,y in [('Fascia',102.01),('Base',102.2),('Glass',102.7),('Cap',103.05)]:
  name=f'CR_PortalReturn_{side}_{part}'
  for j in range(15):
   z=13.6501+(13.9999-13.6501)*j/14;hit,n,fi,dist=meshes[name].ray_cast(Vector((80,-z,y)),Vector((dx,0,0)),3)
   assert hit is not None,(name,z,y);checks.append({'side':side,'band':part,'z':z,'y':y,'hit_world':[hit.x,hit.z,-hit.y]})
  # Both end faces make positive-area joints: jamb at13.65, matching guard at14.
  lo,hi=bounds[name][1];assert abs(-hi-13.65)<1e-5 and abs(-lo-14)<1e-5
  guard_name=('CR_Fascia_'if part=='Fascia'else 'CR_Guard'+part+'_')+apron
  o=bpy.data.objects[guard_name];gv=[o.matrix_world@v.co for v in o.data.vertices];gb=[(min(v[i]for v in gv),max(v[i]for v in gv))for i in range(3)]
  a=bounds[name];area=max(0,min(a[0][1],gb[0][1])-max(a[0][0],gb[0][0]))*max(0,min(a[2][1],gb[2][1])-max(a[2][0],gb[2][0]));assert area>0,(name,'no positive guard joint')
  jo=bpy.data.objects['CR_Portal_'+side];jv=[jo.matrix_world@v.co for v in jo.data.vertices];jb=[(min(v[i]for v in jv),max(v[i]for v in jv))for i in range(3)]
  ja=max(0,min(a[0][1],jb[0][1])-max(a[0][0],jb[0][0]))*max(0,min(a[2][1],jb[2][1])-max(a[2][0],jb[2][0]));assert ja>0 and abs(jb[1][0]+13.65)<1e-5,(name,'no positive jamb joint')
report={'pass':True,'baseline_commit':BASE,'prior_objects_unchanged':len(old),'added_meshes':sorted(expected),'floor_regions_exactly_unchanged':True,'reservations_fixtures_markers_exactly_unchanged':True,'COM_variant_source_and_export_bytes_unchanged':True,'portal_plane_z':13.2,'new_parts_min_z':13.65,'portal_aperture_preserved':True,'gap_closed_z':[13.65,14],'actual_closed_mesh_side_rays':len(checks),'both_ends_positive_contact':True,'ray_checks':checks,'source_sha256':sha(R/'source/AST-RES-006.blend'),'export_sha256':sha(R/'exports/AST-RES-006.glb'),'runtime_small_product_escape_test':'Root pending; no engine/import from source lane'}
(R/'qa/portal_return_verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='ray_checks'},indent=2))
