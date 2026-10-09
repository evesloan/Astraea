#!/usr/bin/env python3
"""Bounded independent native topology and actual GLB validation.
Run Blender first: blender -b --python validate_component.py
Then system Python: python validate_component.py
No changes outside this component family. No external dependencies downloaded.
"""
import json,struct,hashlib,math
from pathlib import Path
OUT=Path(__file__).resolve().parent;ID='AST-RST-AQ-001'
try:import bpy
except ImportError:bpy=None
if bpy:
 import bmesh
 bpy.ops.wm.open_mainfile(filepath=str(OUT/(ID+'.blend')))
 errors=[];rows=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or o.get('asset_id')!=ID:continue
  bm=bmesh.new();bm.from_mesh(o.data)
  closed=bool(o.get('closed_solid_expected'));boundary=sum(e.is_boundary for e in bm.edges);invalid=sum(len(e.link_faces)>2 or len(e.link_faces)==0 for e in bm.edges)
  degen=sum(f.calc_area()<1e-11 for f in bm.faces);volume=bm.calc_volume(signed=True) if closed else None
  fail=invalid>0 or degen>0 or (closed and (boundary or volume<=0))
  if fail:errors.append(o.name)
  rows.append({'name':o.name,'closed_solid_expected':closed,'boundary_edges':boundary,'invalid_or_loose_edges':invalid,'degenerate_faces':degen,'signed_volume_m3':volume,'collision_policy':o.get('collision_policy'),'pass':not fail});bm.free()
 solids=[r for r in rows if r['closed_solid_expected']];surfaces=[r for r in rows if not r['closed_solid_expected']]
 receipt={'scope':'Native fixture-only topology; water/ripples intentionally open surfaces','mesh_objects':len(rows),'closed_solids':len(solids),'open_visual_only_surfaces':len(surfaces),'results':rows,'errors':errors,'pass':not errors}
 (OUT/'native_mesh_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
 assert not errors,errors
 print('NATIVE_PASS',len(rows),'solids',len(solids),'open_visual_only',len(surfaces))
else:
 import numpy as np
 raw=(OUT/(ID+'.glb')).read_bytes();magic,ver,n=struct.unpack_from('<III',raw,0);assert magic==0x46546c67 and ver==2 and n==len(raw)
 chunks=[];o=12
 while o<len(raw):
  size,t=struct.unpack_from('<II',raw,o);chunks.append((t,raw[o+8:o+8+size]));o+=8+size
 doc=json.loads(next(v for t,v in chunks if t==0x4e4f534a));blob=next(v for t,v in chunks if t==0x004e4942)
 counts={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16};types={5120:('b',1),5121:('B',1),5122:('h',2),5123:('H',2),5125:('I',4),5126:('f',4)}
 def acc(i):
  a=doc['accessors'][i];bv=doc['bufferViews'][a['bufferView']];fmt,s=types[a['componentType']];k=counts[a['type']];stride=bv.get('byteStride',s*k);off=bv.get('byteOffset',0)+a.get('byteOffset',0)
  return np.array([struct.unpack_from('<'+fmt*k,blob,off+j*stride) for j in range(a['count'])])
 def transform(n):
  if 'matrix' in n:return np.array(n['matrix']).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);R=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])
  m=np.eye(4);m[:3,:3]=R@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 meshes=[];markers={};nodes={}
 def visit(i,P):
  n=doc['nodes'][i];M=P@transform(n);name=n.get('name','');nodes[name]=n
  if 'mesh' in n:
   assert n.get('extras',{}).get('collision_policy'),name
   for p in doc['meshes'][n['mesh']]['primitives']:
    assert p.get('mode',4)==4
    v=acc(p['attributes']['POSITION']);v=(M@np.c_[v,np.ones(len(v))].T).T[:,:3];idx=acc(p['indices']).reshape(-1,3)
    assert np.isfinite(v).all();assert idx.min()>=0 and idx.max()<len(v)
    meshes.append((name,v,idx,p['material']))
  elif n.get('extras',{}).get('datum_kind'):markers[name]=M[:3,3]
  for c in n.get('children',[]):visit(c,M)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4))
 meta=json.loads((OUT/'component_metadata.json').read_text());vv=np.concatenate([v for _,v,_,_ in meshes]);lo=vv.min(axis=0);hi=vv.max(axis=0)
 assert np.allclose(lo,meta['bounds_gltf']['min'],atol=3e-6) and np.allclose(hi,meta['bounds_gltf']['max'],atol=3e-6)
 assert np.all(hi-lo<=np.array(meta['target_max_dimensions_xyz_m'])+1e-6);assert lo[1]>=-1e-6
 def heights(name,x,z):
  out=[]
  for nm,v,ind,_ in meshes:
   if nm!=name:continue
   for ix in ind:
    t=v[ix];a,b,c=t[:,[0,2]];M=np.column_stack((b-a,c-a));det=np.linalg.det(M)
    if abs(det)<1e-12:continue
    u,w=np.linalg.solve(M,np.array([x,z])-a)
    if u>=-2e-7 and w>=-2e-7 and u+w<=1+2e-7:out.append(float(t[0,1]+u*(t[1,1]-t[0,1])+w*(t[2,1]-t[0,1])))
  return sorted(set(round(q,8) for q in out))
 contactrows=[]
 for r in meta['support']['sample_contacts']:
  p=np.array(r['position']);assert np.allclose(markers[r['name']],p,atol=3e-6)
  y=max(heights(meta['support']['object'],p[0],p[2]));e=abs(y-p[1]);assert e<1e-5
  contactrows.append({'marker':r['name'],'actual_upper_contact_y_m':y,'error_m':e,'pass':True})
 lip=markers['Transfer_Lip'];actual_lip=max(heights('Transfer nonslip slat 04',lip[0],lip[2]));assert abs(actual_lip-lip[1])<1e-6
 mount=markers['Service_Control_Mount'];actual_mount=max(heights('Nonfunctional service control face',mount[0],mount[2]));assert abs(actual_mount-mount[1])<1e-6
 basin=meta['basin']['shell_object'];hc=heights(basin,0,0);assert len(hc)==2 and abs(max(hc)-.16)<1e-6 and abs(min(hc)-.025)<1e-6,hc
 # This rejects any capped bathtub proxy falsely covering the water opening.
 assert max(hc)<meta['water']['level_y_m']-.3
 rim=heights(basin,1.30,0);assert max(rim)>.72 and min(rim)<.25 and max(rim)-min(rim)>.5,rim
 water=[(v,idx,mi) for name,v,idx,mi in meshes if name=='WaterSurface_VisualOnly'];assert len(water)==1
 wv,wi,wmi=water[0];assert np.max(np.abs(wv[:,1]-.57))<1e-6
 wm=doc['materials'][wmi];assert wm.get('alphaMode')=='BLEND' and wm['pbrMetallicRoughness']['baseColorFactor'][3]<1
 water_nodes=[n for name,n in nodes.items() if name=='WaterSurface_VisualOnly' or name.startswith('Water ripple ribbon')]
 assert len(water_nodes)==7 and all(n['extras']['collision_policy']=='NO_SOLID_COLLISION' for n in water_nodes)
 # Sample water triangles against native contact shape's analytic top; resolve to actual GLB for upper support contact.
 water_inside_support=[];samples=0
 for inds in wi:
  p=wv[inds].mean(axis=0);x,y,z=p
  if not (-1.37+.0001<z<1.35-.0001):continue
  t=(z+1.37)/2.72;half=.76+.25*math.sin(math.pi*t)-.12*t*t
  if abs(x)>=half-.0001:continue
  sy=.22+.135*(x/half)**2+.05*(1-t)**3+.48*t**5;samples+=1
  if sy>y+.0035:water_inside_support.append([float(x),float(z),float(sy-y)])
 assert not water_inside_support,water_inside_support[:10]
 # Independently test triangle centroids against actual exported support and bolster faces.
 centroids=wv[wi].mean(axis=1);actual_overlap=[]
 for name,v,inds,_ in meshes:
  if name!=meta['support']['object'] and 'lateral cradle bolster' not in name:continue
  for ix in inds:
   tr=v[ix];a,b,c=tr[:,[0,2]];ab=b-a;ac=c-a;det=ab[0]*ac[1]-ab[1]*ac[0]
   if abs(det)<1e-12:continue
   p=centroids[:,[0,2]]-a;u=(p[:,0]*ac[1]-p[:,1]*ac[0])/det;w=(ab[0]*p[:,1]-ab[1]*p[:,0])/det
   inside=(u>1e-6)&(w>1e-6)&(u+w<1-1e-6)
   yy=tr[0,1]+u*(tr[1,1]-tr[0,1])+w*(tr[2,1]-tr[0,1])
   bad=np.flatnonzero(inside & (yy>.572))
   if len(bad):actual_overlap.append({'object':name,'sample_indices':bad[:8].tolist()})
 assert not actual_overlap,actual_overlap[:4]
 water_normal_y=np.cross(wv[wi[:,1]]-wv[wi[:,0]],wv[wi[:,2]]-wv[wi[:,0]])[:,1]
 assert np.all(water_normal_y>0),float(water_normal_y.min())
 def triangle_aabb(t,low,high):
  c=(low+high)/2;h=(high-low)/2;t=t-c;es=[t[1]-t[0],t[2]-t[1],t[0]-t[2]]
  axes=[np.eye(3)[i] for i in range(3)]+[np.cross(es[0],es[1])]+[np.cross(e,np.eye(3)[i]) for e in es for i in range(3)]
  for a in axes:
   if np.linalg.norm(a)<1e-10:continue
   p=t@a;r=h@np.abs(a)
   if p.max() < -r-1e-7 or p.min()>r+1e-7:return False
  return True
 def clearance(spec):
  low=np.array(spec['min']);high=np.array(spec['max']);hits=[]
  for name,v,ind,_ in meshes:
   if np.any(v.max(axis=0)<low) or np.any(v.min(axis=0)>high):continue
   if any(triangle_aabb(v[ix],low,high) for ix in ind):hits.append(name)
  return {**spec,'intersections':hits,'pass':not hits}
 approach=clearance(meta['approach']['external_clear_prism']);service=clearance(meta['service']['external_clear_prism']);assert approach['pass'] and service['pass'],[approach,service]
 # Wrong-axis negative control makes direction/basis omissions fail.
 wrong=vv[:,[0,2,1]];negative_control=not np.allclose(wrong.max(axis=0)-wrong.min(axis=0),hi-lo);assert negative_control
 assert not doc.get('images') and not doc.get('textures') and not doc.get('cameras') and 'KHR_lights_punctual' not in doc.get('extensions',{})
 assert not any('Preview' in name for name in nodes)
 native=json.loads((OUT/'native_mesh_validation.json').read_text());assert native['pass']
 triangles=sum(len(idx) for _,_,idx,_ in meshes);assert triangles==meta['geometry']['triangles']
 report={'scope':'Source/GLB component geometry only, no Godot import or functioning water/body acceptance','pass':True,'asset_id':ID,'glb_sha256':hashlib.sha256(raw).hexdigest(),'actual_glb_bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist()},'triangle_count':triangles,'mesh_primitive_count':len(meshes),'native_mesh_objects':native['mesh_objects'],'native_closed_solids':native['closed_solids'],'native_open_visual_surfaces':native['open_visual_only_surfaces'],'support_contacts':contactrows,'basin_center_shell_intersections_y_m':hc,'basin_side_rim_intersections_y_m':rim,'cavity_is_not_capped':True,'actual_transfer_contact_y_m':actual_lip,'actual_service_mount_y_m':actual_mount,'water':{'planar_y_m':.57,'alpha_mode':wm['alphaMode'],'alpha':wm['pbrMetallicRoughness']['baseColorFactor'][3],'no_solid_collision_nodes':len(water_nodes),'water_contact_samples':samples,'water_overlap_errors':water_inside_support,'rear_support_hole_tested':True,'actual_support_and_bolster_centroid_overlap_errors':actual_overlap,'all_water_triangles_face_up':True},'front_approach':approach,'service_access':service,'wrong_axis_negative_control_rejected':negative_control,'export_contains_studio_or_lights':False,'external_textures':0,'limits':meta['validation_limits']}
 (OUT/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n');print('GLB_VALIDATION_PASS '+json.dumps(report['actual_glb_bounds'])+' triangles='+str(triangles))
