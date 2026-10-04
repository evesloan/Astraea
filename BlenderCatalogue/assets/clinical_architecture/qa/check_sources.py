"""Bounded evaluated source QA, no rendering. Each read .blend is left unchanged."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evaluated(ob):
 dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];fs=[tuple(t.vertices)for t in me.loop_triangles];ev.to_mesh_clear();return vs,fs

def parts():return [o for o in bpy.context.scene.objects if o.type=='MESH' and 'material_role'in o]
def bvh(ob):v,f=evaluated(ob);return BVHTree.FromPolygons(v,f,all_triangles=True)
def ray(obs,start,end):
 a,b=Vector(start),Vector(end);d=b-a;hits=[]
 for ob in obs:
  loc,n,idx,dist=bvh(ob).ray_cast(a,d.normalized(),d.length)
  if loc is not None:hits.append({'part':ob.name,'position':list(loc),'distance_m':dist,'normal':list(n)})
 return sorted(hits,key=lambda x:x['distance_m'])

RAYS=[]
for z,eye in [(1.12,'seated_proposal'),(1.60,'standing_proposal')]:
 for x,ang in[(.38,0),(.73,0),(.44,.16),(.70,-.16)]:
  RAYS.append({'name':f'{eye}_{x}_{ang}','eye_source_m':[x+ang,-1.20,z],'target_source_m':[x,.65,z],'expected_closed':'blocked','expected_open':'clear'})
RAYS.extend([{'name':'top_clear_negative_control','eye_source_m':[.55,-1.20,2.39],'target_source_m':[.55,.65,2.39],'expected_closed':'clear','expected_open':'clear'}, {'name':'right_edge_clear_negative_control','eye_source_m':[1.22,-1.20,1.60],'target_source_m':[1.22,.65,1.60],'expected_closed':'clear','expected_open':'clear'}])
records=[];all_geometry={}
for ident in('AST-MED-001','AST-MED-002'):
 path=BASE/'source'/f'{ident}.blend';before=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1);obs=parts();man=json.loads((BASE/f'{ident}.manifest.json').read_text());rec={'catalogue_id':ident,'source_sha256':before,'mesh_parts':len(obs),'source_unchanged':False,'physical_marker_witnesses':[],'joint_witnesses':[]}
 for m in man['physical_and_proposal_markers']:
  if m['physical_part'] and m['kind'].startswith('physical'):
   ob=bpy.data.objects[m['physical_part']];tree=bvh(ob);hit=tree.find_nearest(Vector(m['source_m']));dist=hit[3];ndot=Vector(m.get('normal_source',[0,0,0])).dot(hit[1])if hit[1] is not None else None
   rec['physical_marker_witnesses'].append({'name':m['name'],'part':ob.name,'distance_to_actual_surface_m':dist,'actual_nearest_surface_normal':list(hit[1]),'declared_normal_dot_actual':ndot,'passed':dist<.00002 and (ndot is None or ndot>.93)})
 for j in man['joins']:
  ds=[];norm=[]
  for part,decl in zip(j['parts'],[j['normal_a_source'],j['normal_b_source']]):
   hit=bvh(bpy.data.objects[part]).find_nearest(Vector(j['probe_source_m']));ds.append(hit[3]);norm.append(Vector(decl).dot(hit[1]))
  rec['joint_witnesses'].append({'name':j['name'],'surface_distances_m':ds,'normal_dots':norm,'passed':max(ds)<.00003 and min(norm)>.93})
 states={}
 for state,frame in([('closed',1),('open',117)]if ident=='AST-MED-001'else[('closed',1)]):
  bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();states[state]={'bounds':{},'parts':{}}
  for o in obs:
   vs,fs=evaluated(o);states[state]['parts'][o.name]={'role':o['material_role'],'vertices':[[round(c,8)for c in v]for v in vs],'triangles':fs}
  pts=[p for o in states[state]['parts'].values()for p in o['vertices']];states[state]['bounds']={'min':[min(p[i]for p in pts)for i in range(3)],'max':[max(p[i]for p in pts)for i in range(3)]}
  if ident=='AST-MED-001':
   rr=[]
   for test in RAYS:
    hits=ray(obs,test['eye_source_m'],test['target_source_m']);actual='blocked'if hits else'clear';rr.append(dict(test,actual=actual,hits=hits,passed=actual==test['expected_'+state]))
   rec[state+'_rays']=rr
 all_geometry[ident]=states
 if ident=='AST-MED-001':
  moving=[o for o in obs if o.parent and o.parent.name=='SCREEN_TRANSLATION'];static=[o for o in obs if o not in moving];hits=[];mins=[]
  # Full-motion evaluated triangle intersection check. Own moving internal bearings/joins excluded.
  for frame in range(1,118):
   bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();trees={o.name:bvh(o)for o in moving+static}
   for a in moving:
    for b in static:
     vv=trees[a.name].overlap(trees[b.name])
     if vv:hits.append({'frame':frame,'moving':a.name,'fixed':b.name,'triangle_overlap_pairs':len(vv)})
  rec['motion']={'sample_frames':117,'increment_m':.01,'moving_vs_fixed_intersections':hits,'analytic_clearances_m':{'panel_back_to_fixed_return_front':.120,'panel_back_to_plaque_front':.098,'panel_back_to_raised_fixed_lettering':.095,'open_panel_left_to_fixed_nose_right':.025,'open_panel_left_to_left_post_right':.060,'closed_panel_right_to_right_post_left':.140,'sleeve_radial_design_gap':.0015,'closest_sleeve_end_to_end_stop':.1305},'scope':'Rigid prismatic geometry proposal; sample intersection check plus constant analytical gaps, not physical operation/load/locking proof','passed':not hits}
 rec['source_unchanged']=sha(path)==before;rec['passed']=rec['source_unchanged']and all(w['passed']for w in rec['physical_marker_witnesses'])and all(w['passed']for w in rec['joint_witnesses'])and all(x['passed']for x in rec.get('closed_rays',[])+rec.get('open_rays',[]))and rec.get('motion',{}).get('passed',True);records.append(rec)
(BASE/'qa/evaluated_source_geometry.json').write_text(json.dumps(all_geometry,separators=(',',':'))+'\n');(BASE/'qa/source_checks.json').write_text(json.dumps({'results':records,'all_passed':all(r['passed']for r in records)},indent=2)+'\n')
field={'catalogue_id':'AST-MED-001','source_frame':'metres Xwidth Ydepth Zup front-Y','native_glb_mapping':'(x,y,z)->(x,z,-y)','state_node':'SCREEN_TRANSLATION','closed_translation_source_m':[0,0,0],'open_translation_source_m':[-1.16,0,0],'closed_translation_gltf_m':[0,0,0],'open_translation_gltf_m':[-1.16,0,0],'tested_target_region_source_m':{'x':[.38,.73],'y':.65,'z':[1.12,1.60]},'rays':RAYS,'declared_scope':'Eight finite rays at two proposed eye heights with modest oblique variants; top and edge clear negative controls. Target region is bounded inspection evidence, not a whole-room confidentiality guarantee or a treatment/body position.'}
for r in field['rays']:
 for key in('eye','target'):
  p=r[key+'_source_m'];r[key+'_gltf_m']=[p[0],p[2],-p[1]]
(BASE/'privacy_test_field.json').write_text(json.dumps(field,indent=2)+'\n');print(json.dumps({'all_passed':all(r['passed']for r in records),'records':[{k:v for k,v in r.items()if k not in('closed_rays','open_rays')}for r in records]},indent=2))
