"""Independent GLB, source vertices, floor projection and local contact checks."""
import sys,json,hashlib,importlib.util,math
from pathlib import Path
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
import numpy as np
from shapely.geometry import Polygon,MultiPoint,box
from shapely.ops import unary_union
P=Path(__file__).resolve().parents[1];OLD=P.parent
spec=importlib.util.spec_from_file_location('reader',OLD/'source/check_retained_exports.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
def decode(f):
 d,b=reader.read(f);points=[];tri=[];cats={};count=0
 for im in d.get('images',[]):assert 'uri' not in im and 'bufferView' in im
 for n,m in reader.nodes(d):
  cat=n.get('extras',{}).get('contact_category','family_door_preview')
  for q in d['meshes'][n['mesh']]['primitives']:
   assert q.get('mode',4)==4
   a=reader.acc(d,b,q['attributes']['POSITION']);assert np.isfinite(a).all();a=(np.c_[a,np.ones(len(a))]@m.T)[:,:3]
   idx=reader.acc(d,b,q['indices']).ravel();assert len(idx)%3==0 and idx.max()<len(a)
   for k in ['NORMAL','TEXCOORD_0']:assert k in q['attributes'] and np.isfinite(reader.acc(d,b,q['attributes'][k])).all()
   t=a[idx.reshape(-1,3)];assert (np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-10).all()
   points.append(a);tri.append(t);cats.setdefault(cat,[]).append(t);count+=len(idx)//3
 return np.concatenate(points),np.concatenate(tri),{k:np.concatenate(v) for k,v in cats.items()},count
def vertex_delta(a,b):
 # All geometry is axis/world baked; sorted unique vertices compare independently
 # of exporter duplication at UV/normal seams. A small spatial hash avoids scipy.
 a=np.unique(np.round(a,5),axis=0);b=np.unique(np.round(b,5),axis=0)
 def nearest(src,dst):
  buckets={}
  for v in dst:buckets.setdefault(tuple(np.floor(v/.001).astype(int)),[]).append(v)
  maximum=0
  for v in src:
   k=np.floor(v/.001).astype(int);c=[]
   for x in [-1,0,1]:
    for y in [-1,0,1]:
     for z in [-1,0,1]:c.extend(buckets.get(tuple(k+[x,y,z]),[]))
   assert c,'Missing source/export point';maximum=max(maximum,float(np.linalg.norm(np.array(c)-v,axis=1).min()))
  return maximum
 return max(nearest(a,b),nearest(b,a))
def projected(t):
 return unary_union([p for q in t if (p:=Polygon(q[:,[0,2]])).area>1e-9])
delivery=json.loads((P/'docs/TERMINAL_DELIVERY_R002.json').read_text());plan=json.loads((P/'docs/TERMINAL_PLAN_R002.json').read_text());rows=[];all_floor_count=plan['floor_input_regions']
floors=[]
for base,f in [(OLD/'dependencies/canonical_77a745','Game/data/generated/structural_meshes.json'),(OLD/'dependencies/canonical_77a745','Game/data/architecture/REMAINING_BATCH_FLOORS.json'),(OLD/'dependencies/canonical_9d6f85','Game/data/generated/received_structural_meshes.json')]:floors.extend(json.loads((base/f).read_text())['regions'])
middle_top=[]
for f in (OLD/'exports/exterior').glob('G7_MiddleExterior_E*_r001.glb'):
 _,t,_,_=decode(f)
 top=t[np.max(np.abs(t[:,:,1]-61),axis=1)<1e-4];middle_top.extend(top)
old_top=projected(np.array(middle_top));assert not old_top.is_empty
for row,term in zip(delivery['assemblies'],plan['terms']):
 a,t,cats,nt=decode(P/row['export']);source=json.loads((P/row['source_geometry']).read_text());ss=[g for g in source if g['contact_category']!='family_door_preview'];sv=np.array([v for g in ss for v in g['vertices_world_xyz']]);delta=vertex_delta(sv,a);assert delta<8e-5,delta;assert nt==row['architectural_triangles']
 # Exported roof top triangles, rather than its bounding box, protect the route notch.
 roof=cats['solid_roof'];top=roof[np.max(np.abs(roof[:,:,1]-69.5),axis=1)<1e-4];support=projected(top);expected=unary_union([Polygon(term['roof_boundary_xz']),*[Polygon(q) for q in term['bridge_polygons_xz']]])
 assert support.symmetric_difference(expected).area<.005
 route=box(-4,-530,4,-509.2) if term['sign_z']<0 else box(-4,509.2,4,530)
 assert support.intersection(route).area<1e-7
 conflicts=[]
 for r in floors:
  if min(69.5,r['floor_y'])-max(69.2,r['floor_y']-r['thickness'])<=1e-6:continue
  area=support.intersection(unary_union([Polygon(q) for q in r['triangles']])).area
  if area>1e-5:conflicts.append([r['id'],area])
 assert not conflicts,conflicts
 contact=[];failed=[];normal_error=0
 for g in ss:
  v=np.array(g['vertices_world_xyz']);ymin=v[:,1].min();foot=MultiPoint(v[np.abs(v[:,1]-ymin)<1e-4][:,[0,2]]).convex_hull
  if abs(ymin-69.5)<1e-4 and g['contact_category']!='visual_lens':
   unsupported=foot.difference(support.buffer(1e-4));ok=unsupported.is_empty
   contact.append(g['object']);
   if not ok:failed.append(g['object'])
  if 'true_inward_unit_normal' in g:
   n=np.array(g['true_inward_unit_normal']);lo,hi=g['normal_material_interval_m'];d=np.sum((v[3:]-v[:3])*n,axis=1);normal_error=max(normal_error,float(np.max(np.abs(d-(hi-lo)))))
 assert not failed,failed
 assert normal_error<8e-5
 # First frame hoop supports the inner bearing band of the new 0.4m lower seal.
 lower=[]
 for g in ss:
  if '_LowerSeam_' not in g['object']:continue
  v=np.array(g['vertices_world_xyz']);q=MultiPoint(v[np.abs(v[:,1]-61)<1e-4][:,[0,2]]).convex_hull
  bearing=q.intersection(old_top.buffer(1e-5));assert bearing.area>q.area*.45
  lower.append({'part':g['object'],'seal_projection_area_m2':q.area,'retained_top_contact_area_m2':bearing.area})
 doorrows=[]
 for door in row['doors']:
  da,dt,dc,dnt=decode(P/door['preview_export']);ds=[g for g in source if g['object'] in door['preview_objects']];dsv=np.array([v for g in ds for v in g['vertices_world_xyz']]);dd=vertex_delta(dsv,da);assert dd<8e-5 and dnt==176
  y=da[:,1].min();feet=MultiPoint(da[np.abs(da[:,1]-y)<1e-4][:,[0,2]]).convex_hull;assert abs(y-69.5)<1e-4 and feet.difference(support.buffer(1e-4)).is_empty
  doorrows.append({'id':door['id'],'triangles':dnt,'source_export_max_vertex_error_m':dd,'foot_y':float(y),'source_floor_contact':True,'world_bounds':[da.min(axis=0).tolist(),da.max(axis=0).tolist()]})
 # New footprint is outside the void, bounded occupied models and all private houses.
 zmin=float(np.min(np.abs(a[:,2])));assert zmin>=509.1999
 rows.append({'id':row['id'],'export_sha256':hashlib.sha256((P/row['export']).read_bytes()).hexdigest(),'triangles':nt,'source_export_bidirectional_max_vertex_error_m':delta,'true_normal_material_depth_max_error_m':normal_error,'world_bounds':[a.min(axis=0).tolist(),a.max(axis=0).tolist()],'exported_roof_area_m2':support.area,'upper_wall_and_guard_floor_contacts_checked':len(contact),'missing_contacts':failed,'retained_floor_positive_volume_overlaps':conflicts,'retained_frame_lower_seam_contacts':lower,'doors':doorrows,'min_absolute_z':zmin})
out={'passed':True,'first_delivery_untouched':True,'retained_floor_regions_screened':all_floor_count,'assemblies':rows,'checks':'Binary structure, embedded material images, UV/normals, finite vertices, indices, nondegenerate triangles, full source/export vertices, true-normal depth, actual exported roof top triangle footprint, upper wall/guard/door floor contact and first-frame lower seam bearing. New source z>=509.2 is clear of protected atrium z<=64, current bounded occupied upper models z<=467.98 and Group2 private keepouts z<=459. Not a whole model census.','engine_run':False,'exhaustive_movement_or_carts':False,'engineering_load_pressure_certification':False}
(P/'qa/terminal_checks.json').write_text(json.dumps(out,indent=2)+'\n');print('TERMINAL_CHECKS',[(r['id'],r['source_export_bidirectional_max_vertex_error_m'],r['upper_wall_and_guard_floor_contacts_checked']) for r in rows])
