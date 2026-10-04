"""Bounded actual source/GLB marker, join, void and collision checks for guest components."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for mp in sorted((ROOT/'assets/guest_use').glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];gp=mp.parent/m['export'];s=json.loads((OUT/f'independent_source_{ident}.json').read_text())
 assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['glb_sha256']
 a=np.load(ROOT/s['geometry_cache']);tris=a['triangles'];labels=a['object_names'];native=Native(gp);nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};so={o['name']:o for o in s['objects']}
 markers=[];joins=[]
 for mr in m['physical_and_proposal_markers']:
  name=mr['name'];p=np.asarray(mr['source_m']);i=ni[name];sn=np.asarray(so[name]['matrix_world']);gn=native.world[i];world=gn[:3,3]
  r={'name':name,'kind':mr['kind'],'part':mr['physical_part'],'source_world_m':sn[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(sn[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['gltf_m'])-C@p)),'source_parent':so[name]['parent'],'native_parent':nodes[native.parents[i]].get('name') if i in native.parents else None,'extras':nodes[i].get('extras',{})}
  if mr.get('direction_source') is not None:r['direction_conversion_error']=float(np.linalg.norm(C@mr['direction_source']-np.asarray(mr['direction_gltf'])))
  if mr['physical_part']:
   selected=tris[labels==mr['physical_part']];r['distance_to_named_source_surface_m']=float(nearest_distances([p],selected)[0]);r['inside_named_source_solid']=bool(inside_mesh([p],selected)[0]);r['distance_to_native_surface_m']=native.nearest(C@p)['distance_m']
   if mr['kind'].startswith('physical_'):r['physical_contact_on_named_surface']=r['distance_to_named_source_surface_m']<.002
  r['pass']=max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'],r.get('direction_conversion_error',0))<1e-6 and r.get('physical_contact_on_named_surface',True)
  markers.append(r)
 for j in m['joins']:
  p=np.asarray(j['probe_source_m']);partrows=[]
  for part in j['parts']:
   t=tris[labels==part];d=float(nearest_distances([p],t)[0]);ins=bool(inside_mesh([p],t)[0]);partrows.append({'name':part,'probe_surface_distance_m':d,'probe_inside_solid':ins,'contains_probe':ins or d<.0002})
  joins.append({'name':j['name'],'source_probe_m':p.tolist(),'parts':partrows,'pass':all(x['contains_probe']for x in partrows)})
 cp=mp.parent/m['collision_proposal_file'];cr=json.loads(cp.read_text())[ident];hulls=[];frame=[]
 for shape in cr['shapes']:
  if shape['type']=='box':
   lo,hi=np.array(shape['min_source_m']),np.array(shape['max_source_m']);pts=np.asarray(list(itertools.product(*zip(lo,hi))));gpts=pts@C.T
   frame.append(max(np.max(np.abs(gpts.min(axis=0)-shape['min_gltf_m'])),np.max(np.abs(gpts.max(axis=0)-shape['max_gltf_m']))))
  else:pts=np.asarray(shape['points_source_m']);frame.append(float(np.max(np.abs(pts@C.T-shape['points_gltf_m']))))
  hulls.append(Hull(pts,shape))
 tests=[]
 def test(label,p,q,expected=None):
  visual=bool(segment_triangles(p,q,tris));coll=any(h.segment(p,q)is not None for h in hulls);tests.append({'name':label,'source_segment_m':[list(p),list(q)],'visual_blocked':visual,'compound_blocked':coll,'expected_blocked':expected,'pass':(expected is None or visual==expected) and visual==coll})
 for void in cr['preserve_voids']:
  lo,hi=np.asarray(void['min_source_m']),np.asarray(void['max_source_m'])
  for x,z in itertools.product(np.linspace(lo[0]+.003,hi[0]-.003,5),np.linspace(lo[2]+.003,hi[2]-.003,5)):test(void['name'],[x,lo[1]+.002,z],[x,hi[1]-.002,z],False)
 # Distinct expected-blocked controls on structural surfaces, away from allowed trim omissions.
 if ident=='AST-GST-001':controls=[([-.128,-.032,-.02],[-.128,-.032,.10]),([0,.09,.045],[0,.09,.09]),([-.09,.08,.50],[.09,.08,.50])]
 elif ident=='AST-GST-002':controls=[([.04,.02,0],[.04,-.05,0]),([0,-.20,.06],[0,-.20,.20])]
 else:controls=[([-.552,0,-.02],[-.552,0,.1]),([.374,-.11,.80],[.374,-.11,.88]),([.373,-.04,.46],[.373,-.04,.52]),([-.18,.183,.28],[-.18,.183,.36])]
 for i,(p,q)in enumerate(controls):test('blocked_structure_'+str(i),p,q,True)
 wrong=Hull(tris.reshape(-1,3));negative=sum(not t['visual_blocked'] and wrong.segment(*t['source_segment_m'])is not None for t in tests)
 row={'id':ident,'bindings':{'source':{'path':str(sp.relative_to(ROOT)),'sha256':sha(sp)},'export':{'path':str(gp.relative_to(ROOT)),'sha256':sha(gp)},'manifest':{'path':str(mp.relative_to(ROOT)),'sha256':sha(mp)},'collision':{'path':str(cp.relative_to(ROOT)),'sha256':sha(cp)}},'markers':markers,'joins':joins,'collision_shape_count':len(hulls),'collision_frame_max_error_m':float(max(frame)),'void_and_blocked_tests':tests,'whole_asset_hull_wrongly_blocks_clear_controls':negative,'native_animation_clips':len(native.g.doc.get('animations',[])),'native_skin_count':len(native.g.doc.get('skins',[])),'pass':all(x['pass']for x in markers+joins+tests) and max(frame)<1e-6 and negative>0}
 rows.append(row);print(ident,'marker failures',[x['name']for x in markers if not x['pass']],'join failures',[x['name']for x in joins if not x['pass']],'void/control failures',sum(not x['pass']for x in tests),'negative controls',negative)
result={'passed':all(r['pass']for r in rows),'assets':rows,'method':'Read actual evaluated source triangles and actual native GLB node hierarchy. Finite independent void-path grids and blocked structural controls compare triangle intersections with declared convex compounds. Joins use closed-solid winding plus exact point-to-triangle distance. Marker metadata does not replace live native transforms.','limits':['Finite component geometry probes, not continuous collision error certification, engine physics, service procedure, electrical operation, universal actor fit or installed-room testing.','Small switch/retainer ornaments are not separately simulated. No moving parts or animations are claimed in these static components.']}
(OUT/'independent_guest_interfaces.json').write_text(json.dumps(result,indent=2)+'\n')
