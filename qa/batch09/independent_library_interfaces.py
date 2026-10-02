"""Bounded source/native markers, clear spaces and blocked controls for library additions."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=[]
for mp in sorted((ROOT/'assets/library_use').glob('AST-*.manifest.json')):
 m=json.loads(mp.read_text());ident=m['catalogue_id'];sp=mp.parent/m['source'];gp=mp.parent/m['export'];s=json.loads((OUT/f'independent_source_{ident}.json').read_text())
 assert sha(sp)==s['sha256']==m['source_sha256'];assert sha(gp)==m['export_sha256']
 a=np.load(ROOT/s['geometry_cache']);tris=a['triangles'];labels=a['object_names'];native=Native(gp);nodes=native.g.doc['nodes'];ni={n.get('name'):i for i,n in enumerate(nodes)};so={o['name']:o for o in s['objects']}
 markers=[]
 for mr in m['positions_and_normals']:
  name=mr['node_name'];p=np.asarray(mr['source_blender_zup_m']);i=ni[name];sn=np.asarray(so[name]['matrix_world']);gn=native.world[i];world=gn[:3,3];nearest=native.nearest(C@p)
  r={'name':name,'kind':mr['kind'],'meaning':mr['meaning'],'source_world_m':sn[:3,3].tolist(),'native_world_m':world.tolist(),'source_marker_error_m':float(np.linalg.norm(sn[:3,3]-p)),'native_marker_error_m':float(np.linalg.norm(world-C@p)),'declared_native_error_m':float(np.linalg.norm(np.asarray(mr['exchange_gltf_yup_m'])-C@p)),'direction_conversion_error':float(np.linalg.norm(C@mr['normal_source_blender']-np.asarray(mr['normal_exchange_gltf']))),'source_parent':so[name]['parent'],'native_parent':nodes[native.parents[i]].get('name') if i in native.parents else None,'native_nearest_surface':nearest,'extras':nodes[i].get('extras',{})}
  if mr['kind']in ['physical_contact','physical_surface','interaction_proposal']:r['physical_contact_on_native_surface']=nearest['distance_m']<.002
  r['pass']=max(r['source_marker_error_m'],r['native_marker_error_m'],r['declared_native_error_m'],r['direction_conversion_error'])<1e-6 and r.get('physical_contact_on_native_surface',True)
  markers.append(r)
 cp=mp.parent/(ident+'.collision_proposals.json');cr=json.loads(cp.read_text());hulls=[];frame=[]
 for shape in cr['shapes']:
  if shape['type']=='axis_aligned_box':
   lo,hi=np.array(shape['min_source_m']),np.array(shape['max_source_m']);pts=np.asarray(list(itertools.product(*zip(lo,hi))));gpts=pts@C.T;frame.append(max(np.max(np.abs(gpts.min(axis=0)-shape['min_exchange_m'])),np.max(np.abs(gpts.max(axis=0)-shape['max_exchange_m']))))
  else:pts=np.asarray(shape['vertices_source_m']);frame.append(float(np.max(np.abs(pts@C.T-shape['vertices_exchange_m']))))
  hulls.append(Hull(pts,shape))
 tests=[]
 def test(label,p,q,expected=None):
  visual=bool(segment_triangles(p,q,tris));coll=any(h.segment(p,q)is not None for h in hulls);tests.append({'name':label,'source_segment_m':[list(p),list(q)],'visual_blocked':visual,'compound_blocked':coll,'expected_blocked':expected,'pass':(expected is None or visual==expected) and visual==coll})
 for void in cr['preserved_openings']:
  lo,hi=np.asarray(void['min']),np.asarray(void['max'])
  for x,z in itertools.product(np.linspace(lo[0]+.003,hi[0]-.003,5),np.linspace(lo[2]+.003,hi[2]-.003,5)):test(void['name'],[x,lo[1]+.004,z],[x,hi[1]-.003,z],False)
 if ident=='AST-LIB-008':
  controls=[('mount',[0,0,-.02],[0,0,.05]),('diffuser',[0,-.04,.38],[0,-.04,.415]),('spine',[0,-.05,.25],[0,.07,.25]),('hood',[0,-.06,.45],[0,-.06,.51])]
 elif ident=='AST-LIB-009':
  for x in [-.566,.566]:
   test('side_bearing_triangle_clear_depth_'+str(x),[x,-.06,.45],[x,.12,.45],False)
   test('side_bearing_triangle_clear_lateral_'+str(x),[x-.07,.04,.45],[x+.07,.04,.45],False)
   test('side_bearing_front_leg_blocked_'+str(x),[x,-.18,.45],[x,-.03,.45],True)
   test('side_bearing_rear_leg_blocked_'+str(x),[x,.10,.45],[x,.23,.45],True)
  controls=[('archive_shelf',[.1,0,.22],[.1,0,.29]),('left_divider',[-.18,-.18,.35],[-.18,.18,.35]),('right_divider',[.18,-.18,.35],[.18,.18,.35]),('lower_tray',[.1,-.27,.67],[.1,-.06,.67]),('upper_tray',[.1,-.10,1.03],[.1,.10,1.03])]
 else:
  controls=[('left_foot',[-.283,0,-.02],[-.283,0,.10]),('right_foot',[.283,0,-.02],[.283,0,.10]),('head',[0,-.12,1.20],[0,.12,1.20]),('rear_case',[0,.07,.83],[0,.18,.83])]
 for label,p,q in controls:test('blocked_'+label,p,q,True)
 wrong=Hull(tris.reshape(-1,3));negative=sum(not t['visual_blocked'] and wrong.segment(*t['source_segment_m'])is not None for t in tests)
 row={'id':ident,'bindings':{'source':{'path':str(sp.relative_to(ROOT)),'sha256':sha(sp)},'export':{'path':str(gp.relative_to(ROOT)),'sha256':sha(gp)},'manifest':{'path':str(mp.relative_to(ROOT)),'sha256':sha(mp)},'collision':{'path':str(cp.relative_to(ROOT)),'sha256':sha(cp)}},'markers':markers,'collision_shape_count':len(hulls),'collision_frame_max_error_m':float(max(frame)),'void_and_blocked_tests':tests,'whole_asset_hull_wrongly_blocks_clear_controls':negative,'native_animation_clips':len(native.g.doc.get('animations',[])),'native_skin_count':len(native.g.doc.get('skins',[])),'pass':bool(all(x['pass']for x in markers+tests) and max(frame)<1e-6)}
 rows.append(row);print(ident,'marker failures',[(x['name'],x['native_nearest_surface']['distance_m'])for x in markers if not x['pass']],'void/control failures',[(x['name'],x['visual_blocked'],x['compound_blocked'])for x in tests if not x['pass']],'negative controls',negative)
result={'passed':all(r['pass']for r in rows),'assets':rows,'method':'Read actual evaluated source triangles and actual native GLB node hierarchy. Finite independent clear-space grids and blocked structural controls compare triangle intersections with declared convex compounds. Marker metadata does not replace native transforms.','limits':['Finite component geometry probes, not full collision-coverage/error certification, engine physics, electrical operation, universal actor reach or installed-room testing.','No functioning display, switching, book selection or animation is implemented.']}
(OUT/'independent_library_interfaces.json').write_text(json.dumps(result,indent=2)+'\n')
