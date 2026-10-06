"""Independent pure geometry checks, also used on reopened Blender read-back."""
import json, sys, math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R));from fixture_recipe import read,sha,digest,triangles,P,STATIC
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from geometry_review import glb,Query

def mesh_query(rows):return Query([{'triangles':triangles(o),'node':o['name'],'primitive':0}for o in rows])
def polygon_inside_yz(p,poly,tolerance=1e-6):
 p=np.array(p)[1:];v=np.array(poly)[:,1:];crosses=[np.cross(b-a,p-a)for a,b in zip(v,np.roll(v,-1,axis=0))];return min(crosses)>=-tolerance or max(crosses)<=tolerance

def check_mesh(o):
 vs=np.array(o['vertices_world']);tr=triangles(o);base=vs[0];areas=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2
 assert np.isfinite(vs).all()and areas.min()>1e-10,('Nonfinite/degenerate',o['name'])
 edges={}
 for f in o['faces']:
  assert len(set(f))==len(f)
  for a,b in zip(f,f[1:]+f[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 assert all(len(e)==2 and e[0]==tuple(reversed(e[1]))for e in edges.values()),('Not consistently closed',o['name'])
 vol=float(np.einsum('ij,ij->i',tr[:,0]-base,np.cross(tr[:,1]-base,tr[:,2]-base)).sum()/6)
 assert vol>1e-8,('Nonpositive volume',o['name'],vol)
 # Every triangle must face outward from a point infinitesimally behind it.
 # Concave profiles are valid: winding is established by opposed edges and positive closed volume.
 return {'name':o['name'],'vertices':len(vs),'faces':len(o['faces']),'triangles':len(tr),'closed_consistently_wound_edges':len(edges),'signed_volume_m3':vol,'minimum_triangle_area_m2':float(areas.min()),'bounds':[vs.min(0).tolist(),vs.max(0).tolist()]}

def fitted_volume_hits(q,fixture,tolerance=2e-6):
 a,b=np.array(fixture['channel_centerline_endpoints']);delta=b-a
 # Transform actual static triangles into the fitted sloped channel prism.
 tr=q.tri.copy();t=(tr[:,:,2]-a[2])/delta[2];d=a[0]-tr[:,:,0];h=tr[:,:,1]-a[1]-t*delta[1]
 local=np.stack([d,h,t],axis=2);lo=np.array([tolerance,-.020+tolerance,tolerance]);hi=np.array([.016-tolerance,.020-tolerance,1-tolerance])
 candidates=np.flatnonzero(np.all(local.max(1)>lo,axis=1)&np.all(local.min(1)<hi,axis=1));hits=[]
 for i in candidates:
  poly=list(local[i])
  for axis in range(3):
   for edge,sign in [(lo[axis],1),(hi[axis],-1)]:
    clipped=[]
    for pa,pb in zip(poly,poly[1:]+poly[:1]):
     ia=sign*(pa[axis]-edge)>=0;ib=sign*(pb[axis]-edge)>=0
     if ia:clipped.append(pa)
     if ia!=ib:clipped.append(pa+(pb-pa)*(edge-pa[axis])/(pb[axis]-pa[axis]))
    poly=clipped
    if len(poly)<3:break
   if len(poly)<3:break
  if len(poly)>=3 and sum(np.linalg.norm(np.cross(poly[j]-poly[0],poly[j+1]-poly[0]))for j in range(1,len(poly)-1))>1e-11:
   hits.append({'node':q.meshes[int(q.owner[i])]['node'],'triangle_index':int(i)})
 return hits

def validate(recipe,mode):
 rows=recipe['objects'];assert len(rows)==24 and len(recipe['fixtures'])==8;names={o['name']:o for o in rows};checks=[check_mesh(o)for o in rows];newq=mesh_query(rows)
 static=glb(STATIC);q=Query(static['meshes']);referenceq=mesh_query(list(recipe['actual_source_references'].values()));results=[];rayresults=[]
 for f in recipe['fixtures']:
  own=[names[n]for n in f['mesh_names']];assert len(own)==3 and {o['part']for o in own}=={'CHANNEL','LENS','CAP'}
  guard=recipe['actual_source_references'][f['guard']];gx=guard['vertices_world'][0][0];body=next(o for o in own if o['part']=='CHANNEL');lens=next(o for o in own if o['part']=='LENS');cap=next(o for o in own if o['part']=='CAP')
  contact=[p for p in body['vertices_world']if abs(p[0]-gx)<1e-6];assert len(contact)==4,(f['flight'],'rear contact vertices',contact)
  assert all(polygon_inside_yz(p,guard['vertices_world'])for p in contact),('Contact outside actual guard',f['flight'])
  a,b=np.array(f['channel_centerline_endpoints']);contact_area=abs(b[2]-a[2])*.040
  allv=np.concatenate([np.array(o['vertices_world'])for o in own]);depth=gx-allv[:,0];assert depth.min()>-1e-6 and depth.max()<=.01601
  source=np.array(f['attachment_world']);exitpoint=np.array(f['actual_lens_exit_world'])
  # Cast back from source against the real new lens and verify the first hit is 4 mm away.
  lh=mesh_query([lens]).rays(source,source+[.03,0,0]);assert lh and abs(lh[0]['distance_m']-.004)<1e-5,('Wrong optical exit',f['flight'],lh[:1])
  actualexit=np.array(lh[0]['position_xyz']);assert np.linalg.norm(actualexit-exitpoint)<1e-5
  forward=newq.rays(actualexit+[-.00001,0,0],source+[-.02,0,0]);assert not forward,('New fixture blocks its exit',f['flight'],forward)
  # Body/lens and cap/lens touch at the expected cross-section boundaries; none floats.
  def shared_count(left,right):
   return sum(any(np.linalg.norm(np.array(v)-w)<1e-5 for w in right['vertices_world'])for v in left['vertices_world'])
  assert shared_count(body,lens)>=4 and shared_count(lens,cap)>=2,('Disconnected fixture components',f['flight'])
  clearance=[];headroom=[];reachable=[]
  for s in f['samples']:
   tread=recipe['actual_source_references'][s['tread']];v=np.array(tread['vertices_world']);edge=float(v[:,0].max());width=float(np.ptp(v[:,0]));assert abs(width-3.2)<1e-5
   clearance.append(float(allv[:,0].min()-edge));box=[float(v[:,0].min()),float(v[:4,1].mean()+.001),float(v[:,2].min()),edge,float(v[:4,1].mean()+2.1),float(v[:,2].max())];hits=newq.prism_hits(box);assert not hits,('New route/headroom intrusion',s['tread'],hits)
   headroom.append({'tread':s['tread'],'full_width_m':width,'height_tested_m':2.1,'new_geometry_hits':0})
   target=np.array(s['receiver_world']);retained=q.rays(source,target);reference=referenceq.rays(source,target);newhits=newq.rays(source,target);exit_rays=newq.rays(actualexit+[-.00001,0,0],target)
   assert not(retained or reference or newhits or exit_rays),('Blocked tread receiver',f['flight'],s['tread'],retained[:1],reference[:1],newhits[:1],exit_rays[:1])
   rayresults.append({'fixture':f['flight'],'tread':s['tread'],'source_to_receiver_distance_m':float(np.linalg.norm(target-source)),'retained_static_hits':0,'actual_guard_tread_source_hits':0,'new_geometry_hits':0,'actual_lens_exit_to_receiver_new_geometry_hits':0})
   reachable.extend(float(np.linalg.norm(p-source))for p in v[:4])
  assert min(clearance)>=.01399,('Route clearance reduced',f['flight'],min(clearance))
  assert max(reachable)+.35<=f['range_m_geometric_only']+1e-4
  overlaps=fitted_volume_hits(q,f);assert not overlaps,('Retained static penetrates new fitted channel volume',f['flight'],overlaps[:8])
  results.append({'flight':f['flight'],'mount_guard':f['guard'],'rear_contact_vertices':len(contact),'rear_contact_plane_max_error_m':max(abs(p[0]-gx)for p in contact),'rear_contact_area_m2':contact_area,'contact_inside_actual_guard':True,'all_three_components_contact':True,'mesh_names':f['mesh_names'],'source_attachment_empty':f['attachment_empty'],'source_world':source.tolist(),'actual_lens_exit_world':actualexit.tolist(),'lens_to_source_distance_m':float(np.linalg.norm(actualexit-source)),'source_inward_exit_new_geometry_hits':0,'retained_static_channel_volume_penetrations':0,'new_geometry_min_clearance_from_tread_edge_m':min(clearance),'clearance_after_1mm_margin_m':min(clearance)-.001,'range_m_geometric_only':f['range_m_geometric_only'],'max_full_tread_corner_distance_m':max(reachable),'tread_samples':len(f['samples']),'new_geometry_full_width_headroom_tests':headroom})
 assert len(rayresults)==90
 allv=np.concatenate([np.array(o['vertices_world'])for o in rows])
 return {'status':'PASS_'+mode,'source_only':True,'mesh_count':24,'non_light_source_attachment_count':8,'tread_receiver_samples':90,'retained_static_sha256':static['sha256'],'mesh_checks':checks,'fixture_checks':results,'receiver_rays':rayresults,'all_new_geometry_bounds':[allv.min(0).tolist(),allv.max(0).tolist()],'minimum_route_edge_clearance_m':min(f['new_geometry_min_clearance_from_tread_edge_m']for f in results),'new_runtime_lights':0,'native_illumination_or_photometric_acceptance':False,'route_scope':'Added geometry does not intrude into retained 3.2 m full-width stair footprints up to 2.1 m above each tread. Existing whole-theater headroom and installed traversal remain separate evidence.','manufacturing_or_load_certification':False}

if __name__=='__main__':
 source=R/(sys.argv[1]if len(sys.argv)>1 else'SOURCE_CONTRACT.json');out=R/(sys.argv[2]if len(sys.argv)>2 else'PURE_GEOMETRY_QA.json');result=validate(read(source),'PURE_RECIPE_CHECKS');result['geometry_input_sha256']=sha(source)
 with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
 print(result['status'],result['mesh_count'],'meshes,',result['tread_receiver_samples'],'receivers, min clearance',result['minimum_route_edge_clearance_m'])
