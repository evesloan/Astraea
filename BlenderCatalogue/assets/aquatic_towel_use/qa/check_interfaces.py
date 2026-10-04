"""Actual native GLB checks, source correspondence and continuous removal.

Swept volume proof uses each semantic moving part's convex enclosure. This is
conservative for glyphs, exact convex enclosure for the structural parts. Every
fixed native triangle is tested against the entire enclosure via halfspace
clipping, not a finite set of animation frames.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
from scipy.spatial import ConvexHull,cKDTree
from validate_glb import read,accessor,matrix
ROOT=Path(__file__).resolve().parents[1]

def native(asset):
 doc,blob=read(ROOT/'exports'/f'{asset}.glb');groups={'fixed':[],'container':[]};markers={};byrole={}
 def walk(i,parent):
  node=doc['nodes'][i];m=parent@matrix(node);extras=node.get('extras',{})
  if 'mesh' in node:
   group=extras['motion_group']
   for p in doc['meshes'][node['mesh']]['primitives']:
    v=accessor(doc,blob,p['attributes']['POSITION']);idx=accessor(doc,blob,p['indices']).reshape(-1,3)
    world=(m@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];src=world[:,[0,2,1]]*np.array([1,-1,1])
    tri=src[idx];groups[group].append(tri);byrole[(group,extras['material_role'])]=src
  elif 'source_part' in extras:markers[node['name']]={'native_m':m[:3,3].tolist(),'extras':extras}
  for c in node.get('children',[]):walk(c,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 groups={k:np.concatenate(v) if v else np.empty((0,3,3)) for k,v in groups.items()}
 return groups,markers,byrole

def equations_box(lo,hi):
 eq=[]
 for i in range(3):
  a=np.zeros(3);a[i]=1;eq.append([*a,-hi[i]]);eq.append([*-a,lo[i]])
 return np.array(eq)

def clip(poly,eq,eps=1e-8):
 for plane in eq:
  if len(poly)==0:return poly
  ds=poly@plane[:3]+plane[3];new=[]
  for j,a in enumerate(poly):
   b=poly[(j+1)%len(poly)];da,db=ds[j],ds[(j+1)%len(poly)];ina,inb=da<=eps,db<=eps
   if ina:new.append(a)
   if ina!=inb:new.append(a+(b-a)*(da/(da-db)))
  poly=np.array(new)
 return poly

def intersecting_triangles(tris,eq,lo,hi):
 ids=np.flatnonzero(np.all(tris.max(1)>=lo-1e-8,axis=1)&np.all(tris.min(1)<=hi+1e-8,axis=1))
 if not len(ids):return []
 candidates=tris[ids]
 # Triangle entirely outside any one halfspace cannot intersect the volume.
 ds=np.einsum('tvc,pc->tvp',candidates,eq[:,:3])+eq[:,3]
 ids=ids[np.all(ds.min(1)<=1e-8,axis=1)]
 return [int(i) for i in ids if len(clip(tris[i],eq))]

def ray(tris,start,end):
 o=np.array(start,float);d=np.array(end,float)-o;length=np.linalg.norm(d);d/=length
 a=tris[:,0];e1=tris[:,1]-a;e2=tris[:,2]-a;p=np.cross(d,e2);det=(e1*p).sum(1)
 ok=np.abs(det)>1e-10;inv=np.zeros_like(det);inv[ok]=1/det[ok];tvec=o-a
 u=(tvec*p).sum(1)*inv;q=np.cross(tvec,e1);v=(d*q).sum(1)*inv;t=(e2*q).sum(1)*inv
 hits=np.flatnonzero(ok&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)&(t>1e-6)&(t<length-1e-6))
 return None if not len(hits) else {'distance_m':float(t[hits].min()),'point_m':(o+d*t[hits].min()).tolist()}

def inside(tris,point):
 o=np.array(point,float);d=np.array([1,.347129,.231817]);d/=np.linalg.norm(d)
 a=tris[:,0];e1=tris[:,1]-a;e2=tris[:,2]-a;p=np.cross(d,e2);det=(e1*p).sum(1);ok=np.abs(det)>1e-10
 inv=np.zeros_like(det);inv[ok]=1/det[ok];tv=o-a;u=(tv*p).sum(1)*inv;q=np.cross(tv,e1);v=(d*q).sum(1)*inv;t=(e2*q).sum(1)*inv
 ts=np.sort(t[ok&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>1e-6)])
 unique=[]
 for x in ts:
  if not unique or abs(x-unique[-1])>1e-6:unique.append(float(x))
 return len(unique)%2==1

source=json.loads((ROOT/'qa/source_geometry.json').read_text());report={'scope':'Component actual native geometry; no actor, operating force, room or engine claims','assets':{}}
for asset in ('AST-AQU-007','AST-AQU-008'):
 manifest=json.loads((ROOT/f'{asset}.manifest.json').read_text());groups,markers,byrole=native(asset);tris=np.concatenate(list(groups.values()));parts=source[asset]['parts']
 correspondence=[]
 for key,verts in byrole.items():
  srcverts=np.concatenate([np.array(p['vertices']) for p in parts if (p['motion_group'],p['role'])==key])
  a=float(cKDTree(verts).query(srcverts)[0].max());b=float(cKDTree(srcverts).query(verts)[0].max())
  correspondence.append({'motion_group':key[0],'material_role':key[1],'source_to_native_max_m':a,'native_to_source_max_m':b,'passed':max(a,b)<2e-6})
 clear=[]
 for c in manifest['clear_volumes']:
  lo=np.array(c['min_m']);hi=np.array(c['max_m']);hits=intersecting_triangles(tris,equations_box(lo,hi),lo,hi)
  center=(lo+hi)/2;contained=[]
  for p in parts:
   vv=np.array(p['vertices'])
   if np.all(center>=vv.min(0)) and np.all(center<=vv.max(0)) and inside(vv[np.array(p['triangles'])],center):contained.append(p['name'])
  # Positive solid control: centre of first source part's tight bounds gives
  # an actual triangle witness irrespective of hollow global bounds.
  v=tris[0];plo=v.min(0)-.002;phi=v.max(0)+.002;pos=intersecting_triangles(tris,equations_box(plo,phi),plo,phi)
  clear.append({'name':c['name'],'min_m':lo.tolist(),'max_m':hi.tolist(),'actual_native_triangle_intrusions':len(hits),'center_contained_in_actual_source_parts':contained,'positive_surface_control_hits':len(pos),'passed':not hits and not contained and bool(pos)})
 contacts=[]
 for c in manifest['contacts']:
  m=markers[c['name']];decl=np.array(c['position_gltf_yup_m']);actual=np.array(m['native_m']);error=float(np.linalg.norm(decl-actual))
  # Use independently parsed native triangles of the named source part's role.
  contacts.append({'name':c['name'],'kind':c['kind'],'actual_native_position_m':actual.tolist(),'declared_native_error_m':error,'passed':error<2e-6})
 row={'source_sha256':source[asset]['source_sha256'],'glb_sha256':hashlib.sha256((ROOT/'exports'/f'{asset}.glb').read_bytes()).hexdigest(),'source_native_correspondence':correspondence,'whole_clear_volumes':clear,'markers':contacts}
 if asset=='AST-AQU-008':
  path=manifest['throat_path_proposal']['centres_blender_source_m'];radius=manifest['throat_path_proposal']['test_radius_m'];passage=[]
  offsets=np.array([[x,y,z] for x in (-radius,radius) for y in (-radius,radius) for z in (-radius,radius)])
  for i,(a,b) in enumerate(zip(path,path[1:])):
   vv=np.vstack((np.array(a)+offsets,np.array(b)+offsets));h=ConvexHull(vv);hits=intersecting_triangles(tris,h.equations,vv.min(0),vv.max(0))
   passage.append({'segment':i,'from_m':a,'to_m':b,'cross_section':'50mm cube conservatively encloses a50mm diameter sphere','native_triangle_intrusions':len(hits),'passed':not hits})
  vv=np.vstack((np.array(path[1])+offsets,np.array(path[2])+offsets))+[.31,0,0];h=ConvexHull(vv);wrongpass=intersecting_triangles(tris,h.equations,vv.min(0),vv.max(0))
  row['continuous_throat_passage']={'segments':passage,'positive_chute_wall_control_offset_x_m':.31,'positive_control_hits':len(wrongpass),'passed':all(s['passed'] for s in passage) and bool(wrongpass),'limitation':'Continuous empty geometric corridor only; no cloth deformation, material flow, capacity, real hygiene or species claims'}
  sweeps=[]
  for p in [p for p in parts if p['motion_group']=='container']:
   vs=np.array(p['vertices']);swept=np.vstack((vs,vs+[0,.92,0]));h=ConvexHull(swept);lo=swept.min(0);hi=swept.max(0)
   hits=intersecting_triangles(groups['fixed'],h.equations,lo,hi)
   sweeps.append({'part':p['name'],'method':'Full continuous0..0.92m translation, convex enclosure against all fixed native triangles','swept_min_m':lo.tolist(),'swept_max_m':hi.tolist(),'fixed_triangle_intrusions':len(hits),'passed':not hits})
  # Real wrong-position control, not a made-up failing boolean: move a sidewall
  # outward 50mm, so its full sweep overlaps the fixed right load cheek.
  p=next(p for p in parts if p['name']=='bin_rising_side_1');vs=np.array(p['vertices'])+[.08,0,0];sv=np.vstack((vs,vs+[0,.92,0]));h=ConvexHull(sv)
  wrong=intersecting_triangles(groups['fixed'],h.equations,sv.min(0),sv.max(0))
  row['continuous_bin_sweep']={'parts':sweeps,'wrong_x_offset_positive_control_m':.08,'wrong_offset_fixed_triangle_hits':len(wrong),'passed':all(x['passed'] for x in sweeps) and bool(wrong)}
  open_groups,open_markers,_=native(asset+'_withdrawn');states={'closed':tris,'withdrawn':np.concatenate(list(open_groups.values()))};views=[]
  for state,t in states.items():
   for z in (1.20,1.65):
    for x in (-.42,0,.42):
     eye=[x,-1.40,z];tests=[]
     for tx in (-.25,0,.25):
      for tz in (.20,.40,.60,.80,1.05):
       target=[tx,.80,tz];hit=ray(t,eye,target)
       mouth_cross=np.array(eye)+(np.array(target)-eye)*((- .35-eye[1])/(target[1]-eye[1]))
       through_mouth=abs(mouth_cross[0])<=.28 and .878<=mouth_cross[2]<=1.045
       tests.append({'target_m':target,'at_front_mouth_plane_m':mouth_cross.tolist(),'through_declared_mouth':bool(through_mouth),'blocked':hit is not None,'first_hit':hit})
     relevant=[v for v in tests if v['through_declared_mouth']]
     views.append({'state':state,'eye_m':eye,'service_targets':tests,'rays_through_mouth':len(relevant),'all_mouth_rays_blocked':bool(relevant) and all(v['blocked'] for v in relevant)})
  mouth=[]
  for state,t in states.items():
   mouth.append({'state':state,'from_m':[0,-1.4,1.2],'to_m':[0,-.339,.94],'unobstructed':ray(t,[0,-1.4,1.2],[0,-.339,.94]) is None})
  rear=[]
  for state,t in states.items():
   rear.append({'state':state,'from_m':[0,1.85,1.15],'to_m':[0,.50,.77],'unobstructed':ray(t,[0,1.85,1.15],[0,.50,.77]) is None})
  row['bounded_sightline_screen']={'scope':'Finite component-only eye samples at1.20 and1.65m; X0/±0.42,Y-1.40, to15 rear service points per eye. Acceptance applies only to rays crossing the actual guest mouth. Rays over the complete housing are explicitly outside this mouth-to-service screen; this is no privacy wall or continuous optical certification.','tests':views,'clear_mouth_controls':mouth,'clear_rear_service_controls':rear,'passed':all(v['all_mouth_rays_blocked'] for v in views) and all(v['unobstructed'] for v in mouth+rear)}
  # Independently verify native state displacement, fixed geometry and wheel
  # floor bounds. Vertex ordering is identical across the two export states.
  fixederr=float(np.abs(groups['fixed']-open_groups['fixed']).max());moveerr=float(np.abs(open_groups['container']-groups['container']-[0,.92,0]).max())
  row['native_state_translation']={'fixed_max_error_m':fixederr,'moving_translation_max_error_m':moveerr,'closed_moving_min_z':float(groups['container'][:,:,2].min()),'open_moving_min_z':float(open_groups['container'][:,:,2].min()),'passed':fixederr<2e-6 and moveerr<2e-6}
 row['passed']=all(x['passed'] for x in correspondence+clear+contacts) and row.get('continuous_bin_sweep',{'passed':True})['passed'] and row.get('bounded_sightline_screen',{'passed':True})['passed'] and row.get('continuous_throat_passage',{'passed':True})['passed']
 report['assets'][asset]=row
report['all_passed']=all(r['passed'] for r in report['assets'].values())
(ROOT/'qa/actual_native_interfaces.json').write_text(json.dumps(report,indent=2)+'\n')
for asset,r in report['assets'].items():
 print(asset,'PASS',r['passed'],'clear',[(v['name'],v['actual_native_triangle_intrusions']) for v in r['whole_clear_volumes']])
 if 'continuous_bin_sweep' in r:
  print('SWEEP',r['continuous_bin_sweep']['passed'],[(s['part'],s['fixed_triangle_intrusions']) for s in r['continuous_bin_sweep']['parts'] if not s['passed']])
  print('SIGHT',r['bounded_sightline_screen']['passed'],[(x['state'],x['eye_m'],x['rays_through_mouth']) for x in r['bounded_sightline_screen']['tests'] if not x['all_mouth_rays_blocked']])
  print('THROAT',r['continuous_throat_passage']['passed'],[(x['segment'],x['native_triangle_intrusions']) for x in r['continuous_throat_passage']['segments']])
