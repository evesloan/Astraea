"""Read-only retained fixture/source mesh checks. Writes only sibling scratch evidence."""
from pathlib import Path
import json,struct,hashlib,math,collections
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union,polygonize
ROOT=Path('/workspace/shared/astraea-catalogue-continuation-20261002'); OUT=Path(__file__).resolve().parent; PLAN=OUT.parent
EPS=1e-7
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def glb(path):
 b=path.read_bytes(); magic,vers,total=struct.unpack_from('<III',b);assert(magic,vers,total)==(0x46546c67,2,len(b));chunks={};k=12
 while k<len(b):
  size,typ=struct.unpack_from('<II',b,k);chunks[typ]=b[k+8:k+8+size];k+=8+size
 j=json.loads(chunks[0x4e4f534a]);buf=chunks[0x004e4942];meshes=[];markers={}
 def acc(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];d={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']];nc={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dt=np.dtype(d);stride=v.get('byteStride',nc*dt.itemsize);off=v.get('byteOffset',0)+a.get('byteOffset',0)
  assert 'sparse' not in a
  return np.ndarray((a['count'],nc),dtype=dt,buffer=buf,offset=off,strides=(stride,dt.itemsize)).copy()
 def walk(i,T):
  n=j['nodes'][i];A=np.eye(4)
  if 'matrix'in n:A=np.array(n['matrix']).reshape(4,4).T
  else:
   if 'rotation'in n:
    x,y,z,w=n['rotation'];A[:3,:3]=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
   A[:3,:3]=A[:3,:3]@np.diag(n.get('scale',[1,1,1]));A[:3,3]=n.get('translation',[0,0,0])
  A=T@A
  if 'mesh'in n:
   for pr in j['meshes'][n['mesh']]['primitives']:
    assert pr.get('mode',4)==4;v=acc(pr['attributes']['POSITION']).astype(float)@A[:3,:3].T+A[:3,3];f=acc(pr['indices']).reshape(-1,3);meshes.append({'name':n['name'],'v':v,'t':v[f],'material':j['materials'][pr['material']]['name']})
  else:markers[n['name']]={'position':A[:3,3].tolist(),'extras':n.get('extras',{})}
  for c in n.get('children',[]):walk(c,A)
 for i in j['scenes'][j.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return meshes,markers

def normals(t):
 n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);sz=np.linalg.norm(n,axis=1);return n/np.maximum(sz[:,None],1e-30)
def yaw(a):return np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
def ray(o,d,tri,names=None,maxdist=100):
 o=np.array(o,float);d=np.array(d,float);d/=np.linalg.norm(d)
 # AABB broad phase before exact double-sided Moller-Trumbore.
 lo=tri.min(1);hi=tri.max(1);valid=np.ones(len(tri),bool);near=np.full(len(tri),-np.inf);far=np.full(len(tri),np.inf)
 for ax in range(3):
  if abs(d[ax])<1e-12:valid&=(o[ax]>=lo[:,ax]-EPS)&(o[ax]<=hi[:,ax]+EPS)
  else:
   a=(lo[:,ax]-o[ax])/d[ax];b=(hi[:,ax]-o[ax])/d[ax];near=np.maximum(near,np.minimum(a,b));far=np.minimum(far,np.maximum(a,b))
 ix=np.flatnonzero(valid&(far>=np.maximum(near,EPS))&(near<=maxdist+EPS));t=tri[ix]
 if not len(t):return None
 e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);a=np.einsum('ij,ij->i',e1,h);ok=abs(a)>1e-12;f=np.zeros_like(a);f[ok]=1/a[ok];s=o-t[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1);v=f*(q@d);dist=f*np.einsum('ij,ij->i',e2,q);ok&=(u>=-EPS)&(v>=-EPS)&(u+v<=1+EPS)&(dist>EPS)&(dist<=maxdist+EPS)
 ids=np.flatnonzero(ok)
 if not len(ids):return None
 k=ids[np.argmin(dist[ids])];idx=ix[k];return {'distance_m':float(dist[k]),'point':(o+d*dist[k]).tolist(),'triangle_index':int(idx),'object':str(names[idx])if names is not None else None,'normal':normals(tri[idx:idx+1])[0].tolist()}

def plane_section(tri,axis,value):
 # Actual triangle edge intersections, then polygonize bounded closed sections.
 other=[i for i in range(3)if i!=axis];edges=[]
 for t in tri:
  ds=t[:,axis]-value;pts=[]
  if max(ds)<-EPS or min(ds)>EPS:continue
  if max(abs(ds))<EPS:
   continue # coplanar face area handled separately below
  for i in range(3):
   j=(i+1)%3
   if abs(ds[i])<EPS:pts.append(t[i])
   if ds[i]*ds[j]<-1e-16:pts.append(t[i]+(t[j]-t[i])*ds[i]/(ds[i]-ds[j]))
  if len(pts)>=2:
   pts=np.unique(np.round(np.array(pts)[:,other],9),axis=0)
   if len(pts)>=2:edges.append(LineString(pts[:2]))
 polys=list(polygonize(unary_union(edges)))if edges else []
 # Numerical endpoints can affect polygonization: real coplanar triangles included.
 for t in tri:
  if np.max(abs(t[:,axis]-value))<EPS:
   p=Polygon(t[:,other]);
   if p.area>EPS:polys.append(p)
 return unary_union(polys)

def face_area_at_plane(tri,normal,value,world_origin,R):
 # Express source support triangles in fixture local coordinates before slicing.
 local=(tri-world_origin)@R
 return plane_section(local,2,value)

def source_objects():
 g=json.loads((ROOT/'assets/grand_lantern_theater_section/source/geometry.json').read_text());result=[]
 for ob in g['objects']:
  if ob['role']=='preview_only':continue
  v=np.array(ob['vertices_world'],float);f=[]
  for face in ob['faces']:
   for j in range(1,len(face)-1):f.append([face[0],face[j],face[j+1]])
  t=v[np.array(f)];result.append({'name':ob['name'],'role':ob['role'],'v':v,'t':t,'lo':v.min(0),'hi':v.max(0)})
 return result

def clip_triangle(poly,planes):
 for n,c in planes:
  if not len(poly):break
  out=[]
  for i,a in enumerate(poly):
   b=poly[(i+1)%len(poly)];da=np.dot(n,a)-c;db=np.dot(n,b)-c
   if da<=EPS:out.append(a)
   if (da<0 and db>0)or(da>0 and db<0):out.append(a+(b-a)*da/(da-db))
  poly=out
 return np.array(poly)
def embedded_triangle_area(tri,ob):
 # Actual mesh triangles clipped against verified convex source solids. Not AABB claims.
 nn=normals(ob['t']);centre=ob['v'].mean(0);planes=[]
 for n,t in zip(nn,ob['t']):
  if np.linalg.norm(n)<.5:continue
  if np.dot(n,t[0]-centre)<0:n=-n
  c=np.dot(n,t[0]);
  if np.max(ob['v']@n-c)>1e-6:return None
  if not any(np.linalg.norm(n-m)<1e-7 and abs(c-d)<1e-7 for m,d in planes):planes.append((n,c))
 amount=0;depth=0
 for t in tri:
  p=clip_triangle(list(t),planes)
  if len(p)<3:continue
  area=sum(np.linalg.norm(np.cross(p[i]-p[0],p[i+1]-p[0]))/2 for i in range(1,len(p)-1))
  if area>1e-10:
   deep=min(c-np.dot(n,p.mean(0))for n,c in planes)
   if deep>1e-7:amount+=area;depth=max(depth,deep)
 return {'embedded_surface_area_m2':float(amount),'max_test_polygon_centroid_depth_m':float(depth)}

def main():
 L=json.loads((PLAN/'LIGHTING_ENCLOSURE_VIEW_PLAN.json').read_text())['fixtures'];A=json.loads((PLAN/'FIRST_PASS_ADDITIONS_PLAN.json').read_text());source=source_objects();st=np.concatenate([o['t']for o in source]);sn=np.concatenate([np.repeat(o['name'],len(o['t']))for o in source]);byname={o['name']:o for o in source};source_lo=np.array([o['lo']for o in source]);source_hi=np.array([o['hi']for o in source])
 fam={};pins={}
 for family,stem in [('hospitality_lantern','AST-LGT-001'),('auditorium_use','AST-CUL-004')]:
  d=ROOT/'assets'/family;m=json.loads((d/(stem+'.manifest.json')).read_text());pins[stem]={k:{'sha256':sha(d/m[k]),'manifest_matches':sha(d/m[k])==m.get(k+'_sha256',m.get('glb_sha256'))}for k in ['source','export']};assert all(q['manifest_matches']for q in pins[stem].values());fam[stem]=glb(d/m['export'])
 base=ROOT/'assets/grand_lantern_theater_section/source/AST-CUL-005.blend';pins['AST-CUL-005']={'sha256':sha(base),'expected_matches':sha(base)==A['saved_base_sha256']};assert pins['AST-CUL-005']['expected_matches']
 pins['geometry_json']=sha(ROOT/'assets/grand_lantern_theater_section/source/geometry.json');pins['plans']={p:sha(PLAN/p)for p in ['FIRST_PASS_ADDITIONS_PLAN.json','LIGHTING_ENCLOSURE_VIEW_PLAN.json']}
 lp,lm=fam['AST-LGT-001'];lt=np.concatenate([p['t']for p in lp]);ln=np.concatenate([np.repeat(p['name'],len(p['t']))for p in lp]);cer=next(p['t']for p in lp if p['name']=='LANTERN_ivory_enamel');lens=next(p['t']for p in lp if p['name']=='LANTERN_lens');lensn=normals(lens);front=lensn[:,2]>.90
 emitter=np.array(lm['DATUM_light_exit']['position']);mount=np.array(lm['DATUM_wall_mount']['position']);sections={float(z):plane_section(cer,2,z)for z in [-.015,0]}
 family={'AST-LGT-001':{'triangle_count':len(lt),'mesh_bounds':{p['name']:[p['v'].min(0).tolist(),p['v'].max(0).tolist()]for p in lp},'actual_mount_datum':mount.tolist(),'actual_exit_datum':emitter.tolist(),'forward_lens_triangle_normals':lensn[front].tolist(),'forward_facets_mean_normal':(lensn[front].mean(0)/np.linalg.norm(lensn[front].mean(0))).tolist(),'forward_lens_tip':float(lens[:,:,2].max()),'datum_tip_clearance_m':float(emitter[2]-lens[:,:,2].max()),'outward_datum_ray':ray(emitter,[0,0,1],lt,ln,1),'backward_datum_lens_hit':ray(emitter,[0,0,-1],lens,None,1),'real_ceramic_section_areas_m2':{str(k):v.area for k,v in sections.items()}}}
 # Every physical forward lens facet emits along its actual retained triangle normal.
 tests=[]
 for i in np.flatnonzero(lensn[:,2]>.05):
  p=lens[i].mean(0)+lensn[i]*.003;hit=ray(p,lensn[i],lt,ln,1);tests.append({'lens_triangle':int(i),'origin':p.tolist(),'normal':lensn[i].tolist(),'self_blocker':hit})
 family['AST-LGT-001']['forward_hemisphere_triangle_exit_tests']=tests
 results=[];deferred=[]
 for l in L:
  group=l['group'];id=l['id']
  if 'AST-LGT-001'not in l['asset']:
   if l['asset'].startswith('AST-CUL-004')and group in ['original_pier_or_cue','backstage_rehearsal_cue']:continue
   deferred.append({'id':id,'group':group,'reason':'New geometry is not built. Cannot certify support/body contact, self-exit, transformed normals, or final receiver visibility.','existing_support':l.get('source_support')});continue
  ceiling='backplate_support_world'in l
  future=ceiling and l.get('source_support','').startswith('NEW')
  if ceiling:
   theta=math.radians(float(id.rsplit('_a',1)[1]))if group=='gallery_soffit'else 0
   R=np.array([[math.cos(theta),math.sin(theta),0],[0,0,-1],[-math.sin(theta),math.cos(theta),0]]);T=np.array(l['backplate_support_world'])-R@mount
  else:R=yaw(l['yaw_radians']);T=np.array(l['origin_world'])
  wt=lt@R.T+T;wn=R@np.array([0,0,1]);we=R@emitter+T;planned=np.array(l['emitter_world']);lo=wt.reshape(-1,3).min(0);hi=wt.reshape(-1,3).max(0)
  row={'id':id,'group':group,'world_from_gltf_rotation_rows':R.tolist(),'world_translation':T.tolist(),'actual_transformed_mount':(R@mount+T).tolist(),'actual_transformed_emitter':we.tolist(),'planned_emitter_error_m':float(np.linalg.norm(we-planned)),'world_outward_axis':wn.tolist(),'model_bounds_world':[lo.tolist(),hi.tolist()],'body_candidates':[],'support_contact':[],'forward_exit_1m':ray(we,wn,wt,ln,1),'forward_scene_ray':ray(we,wn,st,sn,100)}
  # Actual triangle/solid body clipping for all AABB shortlisted real source objects.
  inds=np.flatnonzero(np.all(source_hi>=lo-EPS,axis=1)&np.all(source_lo<=hi+EPS,axis=1))
  for idx in inds:
   ob=source[idx];parts={}
   for p in lp:
    hit=embedded_triangle_area(p['t']@R.T+T,ob)
    if hit is None:parts[p['name']]={'convex_source_unproven':True}
    elif hit['embedded_surface_area_m2']>1e-9:parts[p['name']]=hit
   if parts:row['body_candidates'].append({'source_object':ob['name'],'actual_triangle_clipping':parts})
  if future:
   row['support_status']='UNBUILT ceiling: no support proof';deferred.append({'id':id,'group':group,'reason':'Top-deck cap unbuilt; rigid transform and retained-fixture exit only. New support and occlusion checks required.'})
  elif group=='added_pier':row['support_status']='UNBUILT mount bracket: existing pier 0.185m behind ceramic rear face';deferred.append({'id':id,'group':group,'reason':'New mount bracket required; retained pier alone cannot reach the fixture.'})
  else:
   # Cross section at actual structural interface: side wall ceramic rear face, otherwise nominal mount plane.
   section_z=-.015 if group=='side_route' else 0.0;shape=sections[section_z];supported=[]
   for idx in inds:
    ob=source[idx];s=face_area_at_plane(ob['t'],wn,section_z,T,R);intersection=shape.intersection(s)
    if intersection.area>1e-9:
     supported.append(s);row['support_contact'].append({'source_object':ob['name'],'actual_ceramic_section_contact_area_m2':intersection.area,'support_section_local_area_m2':s.area})
   covered=unary_union(supported)if supported else Polygon();row['support_status']='Actual triangle section contact'if supported else'FAIL no actual triangle section contact';row['ceramic_section_area_m2']=shape.area;row['supported_ceramic_section_area_m2']=shape.intersection(covered).area;row['ceramic_section_missing_support_area_m2']=shape.difference(covered).area;row['support_section_local_z']=section_z
  # Receiver rays from actual datum toward source surfaces; direct down plus aimed inward/down offsets.
  receiver_tests=[]
  dirs=[('down',np.array([0,-1,0]))]if ceiling else [('inward_down_45',wn+np.array([0,-1,0])),('inward_down_65',wn*.4663+np.array([0,-1,0]))]
  for label,d in dirs:
   d=d/np.linalg.norm(d);own=ray(we,d,wt,ln,100);env=ray(we,d,st,sn,100);receiver_tests.append({'direction_label':label,'direction_world':d.tolist(),'fixture_self_hit':own,'first_actual_source_hit':env,'source_visible':env is not None and(own is None or own['distance_m']>env['distance_m']+EPS)})
  row['receiver_rays']=receiver_tests
  results.append(row)
 # Cue geometry: actual diffuser normals, emitter and precise retained tray/soles checks.
 cp,cm=fam['AST-CUL-004'];ct=np.concatenate([p['t']for p in cp]);cn=np.concatenate([np.repeat(p['name'],len(p['t']))for p in cp]);diff=next(p['t']for p in cp if p['material']=='ASTRAEA_staff_opal');dn=normals(diff);bottom=dn[:,1]<-.9
 family['AST-CUL-004']={'triangle_count':len(ct),'diffuser_bottom_triangles':diff[bottom].tolist(),'diffuser_bottom_normals':dn[bottom].tolist(),'emitter_surface_marker':cm['PROPOSED_EMITTER_SURFACE'],'work_surface_marker':cm['WORK_SURFACE']}
 cues=[]
 for l in L:
  if not l['asset'].startswith('AST-CUL-004')or l['group']not in['original_pier_or_cue','backstage_rehearsal_cue']:continue
  if 'origin_world'in l:T=np.array(l['origin_world']);R=yaw(l['yaw_radians'])
  else:
   p=next(p for p in A['ground_modules']if p['id']+'_task_light'==l['id']);T=np.array(p['position_world']);R=yaw(p['yaw_radians'])
  wt=ct@R.T+T;surface=np.array(cm['PROPOSED_EMITTER_SURFACE']['position']);normal=dn[bottom].mean(0);normal/=np.linalg.norm(normal);we=R@(surface+normal*.003)+T;aim=R@normal;direct=ray(we,aim,wt,cn,3);receiver=np.array(l['receiver_world']);to=receiver-we;rh=ray(we,to,wt,cn,np.linalg.norm(to)+1e-4);soles=[]
  for key in ['LEFT_FRONT_FLOOR','LEFT_REAR_FLOOR','RIGHT_FRONT_FLOOR','RIGHT_REAR_FLOOR']:
   p=R@np.array(cm[key]['position'])+T;hit=ray(p+np.array([0,.0001,0]),[0,-1,0],st,sn,.001);soles.append({'marker':key,'point':p.tolist(),'actual_source_hit':hit})
  cues.append({'id':l['id'],'actual_world_emitter':we.tolist(),'planned_emitter_error_m':float(np.linalg.norm(we-np.array(l['emitter_world']))),'actual_world_normal':aim.tolist(),'downward_first_fixture_receiver':direct,'planned_receiver':receiver.tolist(),'planned_receiver_first_hit':rh,'planned_receiver_hit_error_m':None if rh is None else float(np.linalg.norm(np.array(rh['point'])-receiver)),'actual_sole_to_source_contacts':soles,'forward_exit_0_5m':ray(we,aim,wt,cn,.5)})
 out={'scope':'Pure GLB bytes and retained geometry.json triangle/solid checks. No Blender/Godot/shared writes. No rendering, photometric, build or future-support acceptance.','pins':pins,'method':{'rays':'Exact double-sided Moller-Trumbore triangles after AABB broad phase; emitted actual datum, source face centroids and transformed actual facet normals.','contacts':'Real ceramic cross-section polygons from actual GLB triangle/plane intersections, intersected with actual retained support triangle/plane sections. Body screening clips each actual fixture triangle to each verified convex source solid.','preview_floor':'Excluded single preview-only D11 floor. Missing D11 compiler-owned floor hits are not replaced by phantom receivers.','ceiling_rigid_transform':'Columns are tangent (cos a,0,-sin a), radial (sin a,0,cos a), outward (0,-1,0); translation=support minus rotated actual wall-mount datum.'},'family_checks':family,'lantern_placements':results,'cue_placements':cues,'deferred_geometry_checks':deferred,'postbuild_required':['Repeat on newly authored and reopened source geometry with all new fixture bodies, ceiling/ring/header brackets and furniture present.','Verify real support overlaps/bearings, bracket pier/cap contacts, clearance around actual diffuser normals, emitter self exit and unobstructed occupied-zone receiver samples.','Validate curtain/roof/return occlusion, source floor/compiler floors separately, and normal-eye visual lighting at fixed exposure with zero ambient/fill.','Verify imported/exported fixture transforms and material emission separately before runtime acceptance; no inference from marker count.']}
 (OUT/'PRACTICAL_LIGHT_TRIANGLE_EVIDENCE.json').write_text(json.dumps(out,indent=2)+'\n')
 summary={'lantern_placements':len(results),'cue_placements':len(cues),'groups':dict(collections.Counter(r['group']for r in results)),'no_contact':[(r['id'],r['support_status'])for r in results if r['support_status'].startswith('FAIL')],'datum_self_blocked':[r['id']for r in results if r['forward_exit_1m']],'forward_lens_facet_tests':len(tests),'forward_lens_facet_self_blocked':len([t for t in tests if t['self_blocker']]),'body_embedded_parts':[(r['id'],r['body_candidates'])for r in results if any(any(k!='LANTERN_ivory_enamel'for k in o['actual_triangle_clipping'])for o in r['body_candidates'])],'deferred_count':len(deferred),'cue_receiver_hit_errors':[(r['id'],r['planned_receiver_hit_error_m'])for r in cues]};(OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
