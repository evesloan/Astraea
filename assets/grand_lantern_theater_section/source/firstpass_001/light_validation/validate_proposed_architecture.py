"""Proposed new-architecture triangle checks, separately labelled from retained evidence."""
from validate_practicals import *
from validate_receivers_and_soles import candidate_indices
from shapely import constrained_delaunay_triangles

def proposed_objects(path):
 out=[]
 for o in json.loads(path.read_text())['objects']:
  v=np.array(o['vertices_world']);tri=[]
  for face in o['faces']:
   p=v[face]
   if len(set(face))<3 or np.linalg.norm(np.sum(np.cross(p,np.roll(p,-1,axis=0)),axis=0))<1e-9:continue
   if len(face)==3:tri.append(p);continue
   nn=np.sum(np.cross(p,np.roll(p,-1,axis=0)),axis=0);axis=np.argmax(abs(nn));other=[i for i in range(3)if i!=axis];poly=Polygon(p[:,other]);assert poly.is_valid,(o['name'],face);parts=constrained_delaunay_triangles(poly)
   assert abs(sum(q.area for q in parts.geoms)-poly.area)<1e-7
   for q in parts.geoms:
    projected=np.array(q.exterior.coords)[:3]; ix=[int(np.argmin(np.linalg.norm(p[:,other]-point,axis=1)))for point in projected]; assert max(np.linalg.norm(p[ix][:,other]-projected,axis=1))<1e-8; vv=p[ix].copy()
    if np.dot(np.cross(vv[1]-vv[0],vv[2]-vv[0]),nn)<0:vv=vv[[0,2,1]]
    tri.append(vv)
  out.append({'name':o['name'],'role':o['role'],'v':v,'t':np.array(tri),'lo':v.min(0),'hi':v.max(0)})
 return out

def main():
 path=PLAN/'ARCHITECTURE_ADDITIONS_GEOMETRY.json';new=proposed_objects(path);old=source_objects();oldby={o['name']:o for o in old};newby={o['name']:o for o in new};nt=np.concatenate([o['t']for o in new]);nn=np.concatenate([np.repeat(o['name'],len(o['t']))for o in new]);st=np.concatenate([o['t']for o in old]);sn=np.concatenate([np.repeat(o['name'],len(o['t']))for o in old]);nl=np.array([o['lo']for o in new]);nh=np.array([o['hi']for o in new]);L=json.loads((PLAN/'LIGHTING_ENCLOSURE_VIEW_PLAN.json').read_text())['fixtures'];prior=json.loads((OUT/'PRACTICAL_LIGHT_TRIANGLE_EVIDENCE.json').read_text());archsha=sha(path)
 # Actual retained chairs remain in the first-hit receiver scene.
 chairparts,_=glb(ROOT/'assets/auditorium_use/exports/AST-CUL-003.glb');ct=np.concatenate([p['t']for p in chairparts]);cn=np.concatenate([np.repeat(p['name'],len(p['t']))for p in chairparts]);instances=[]
 for p in json.loads((ROOT/'assets/grand_lantern_theater_section/contracts/place_instances.json').read_text())['places']:
  R=yaw(p['orientation_yaw_radians']);T=np.array(p['position']);v=ct.reshape(-1,3)@R.T+T;instances.append({'id':p['id'],'R':R,'T':T,'lo':v.min(0),'hi':v.max(0)})
 il=np.array([i['lo']for i in instances]);ih=np.array([i['hi']for i in instances])
 def scene_ray(o,d,maxdist=100):
  o=np.array(o);d=np.array(d);d=d/np.linalg.norm(d);h=ray(o,d,st,sn,maxdist)
  if h:h['class']='retained_structure';maxdist=h['distance_m']
  p=ray(o,d,nt,nn,maxdist)
  if p:p['class']='PROPOSED_new_architecture';h=p;maxdist=h['distance_m']
  for i in candidate_indices(o,d,il,ih,maxdist):
   ins=instances[i];R=ins['R'];T=ins['T'];q=ray((o-T)@R,d@R,ct,cn,maxdist)
   if q:q['point']=(np.array(q['point'])@R.T+T).tolist();q['normal']=(np.array(q['normal'])@R.T).tolist();q['class']='retained_chair';q['instance']=ins['id'];h=q;maxdist=q['distance_m']
  return h
 # Proposed-architecture contact/body screen for all retained-lantern transforms.
 lp,lm=glb(ROOT/'assets/hospitality_lantern/exports/AST-LGT-001.glb');lt=np.concatenate([p['t']for p in lp]);ln=np.concatenate([np.repeat(p['name'],len(p['t']))for p in lp]);cer=next(p['t']for p in lp if p['name']=='LANTERN_ivory_enamel');shape=plane_section(cer,2,0);lanterns=[]
 for prev in prior['lantern_placements']:
  R=np.array(prev['world_from_gltf_rotation_rows']);T=np.array(prev['world_translation']);wt=lt@R.T+T;lo=wt.reshape(-1,3).min(0);hi=wt.reshape(-1,3).max(0);ids=np.flatnonzero(np.all(nh>=lo-EPS,1)&np.all(nl<=hi+EPS,1));body=[];contacts=[]
  for i in ids:
   ob=new[i];partresults={}
   for p in lp:
    hit=embedded_triangle_area(p['t']@R.T+T,ob)
    if hit is None:partresults[p['name']]={'nonconvex_cannot_use_solid_clipper':True}
    elif hit['embedded_surface_area_m2']>1e-9:partresults[p['name']]=hit
   if partresults:body.append({'proposed_object':ob['name'],'actual_fixture_triangle_clipping':partresults})
   section=plane_section((ob['t']-T)@R,2,0);area=shape.intersection(section).area
   if area>1e-8:contacts.append({'proposed_object':ob['name'],'contact_area_m2':area})
  added=[]
  if prev['group']=='added_pier':
   bracket=newby[prev['id']+'_actual_bracket'];port=bracket['v'].mean(0)[0]<-76;axis_x=bracket['lo'][0]if port else bracket['hi'][0];bp=plane_section(bracket['t'],0,axis_x);pier=oldby[f"lantern_pier_{-105 if port else -47}_{int(round(bracket['v'].mean(0)[2]))}"];pp=plane_section(pier['t'],0,axis_x);added={'proposed_bracket':bracket['name'],'retained_pier':pier['name'],'whole_interface_area_m2':bp.area,'missing_area_m2':bp.difference(pp).area}
  lanterns.append({'id':prev['id'],'new_architecture_contacts':contacts,'new_architecture_body_clips':body,'new_bracket_retained_pier_interface':added,'proposed_architecture_ray_from_actual_datum':ray(prev['actual_transformed_emitter'],prev['world_outward_axis'],nt,nn,100)})
 # Ring opal full upper-face bearing on the retained bronze ring.
 rt=np.concatenate([o['t']for o in old if o['name'].startswith('canopy_lantern_ring')]);support=plane_section(rt,1,91);rings=[]
 for i in range(16):
  ob=newby[f'FP_ring_opal_segment_{i:02}'];top=plane_section(ob['t'],1,91);low=plane_section(ob['t'],1,90.97);norm=normals(ob['t']);faces=np.flatnonzero(norm[:,1]<-.9);rays=[]
  for k in faces:
   o=ob['t'][k].mean(0)+norm[k]*.003;own=ray(o,norm[k],ob['t'],np.repeat(ob['name'],len(ob['t'])),1);rays.append({'triangle':int(k),'actual_face_normal':norm[k].tolist(),'self_hit':own,'scene_first_hit':scene_ray(o,norm[k])})
  l=next(l for l in L if l['id']==f'canopy_ring_emitter_{i:02}');o=l['emitter_world'];back=ray(o,[0,1,0],nt,nn,.1);rings.append({'id':l['id'],'proposed_opal_segment':ob['name'],'top_area_m2':top.area,'unsupported_top_area_m2':top.difference(support).area,'planned_emitter_lens_back_ray':back,'planned_emitter_down_first_hit':scene_ray(o,[0,-1,0]),'actual_downward_face_count':len(faces),'actual_face_exit_and_receiver_rays':rays})
 ringcontacts=[]
 for i in range(4):
  ob=newby[f'FP_ring_short_contact_{i}'];bottom=plane_section(ob['t'],1,91.35);top=plane_section(ob['t'],1,91.4);ringtop=plane_section(rt,1,91.35);capbottom=plane_section(newby['FP_ring_backing_cap']['t'],1,91.4);ringcontacts.append({'id':ob['name'],'bottom_area_m2':bottom.area,'missing_ring_top_contact_m2':bottom.difference(ringtop).area,'top_area_m2':top.area,'missing_cap_contact_m2':top.difference(capbottom).area})
 # Staff fixture actual plates, body, modeled lens and guard. Old plan ray must not be accepted.
 spath=ROOT/'assets/staff_overhead';manifest=json.loads((spath/'AST-STF-006.manifest.json').read_text());assert sha(spath/manifest['source'])==manifest['source_sha256'];assert sha(spath/manifest['export'])==manifest['glb_sha256'];sp,_=glb(spath/manifest['export']);stf=np.concatenate([p['t']for p in sp]);sfn=np.concatenate([np.repeat(p['name'],len(p['t']))for p in sp]);metal=next(p['t']for p in sp if p['name']=='AST-STF-006__staff_zinc');mountshape=plane_section(metal,1,0);slens=next(p['t']for p in sp if p['name']=='AST-STF-006__staff_opal');sln=normals(slens);optical=[]
 for k in np.flatnonzero(sln[:,1]<-.7):
  o=slens[k].mean(0)+sln[k]*.003;optical.append({'lens_triangle':int(k),'local_emitter':o.tolist(),'normal':sln[k].tolist(),'self_hit':ray(o,sln[k],stf,sfn,1)})
 candidates=[[.58,-.564,.04],[.45,-.564,0]];backs=[]
 for l in L:
  if l['group']!='backstage':continue
  T=np.array(l['mount_world']);wt=stf+T;lo=wt.reshape(-1,3).min(0);hi=wt.reshape(-1,3).max(0);ids=np.flatnonzero(np.all(nh>=lo-EPS,1)&np.all(nl<=hi+EPS,1));contact=[];body=[]
  for i in ids:
   ob=new[i];section=plane_section(ob['t']-T,1,0);area=mountshape.intersection(section).area
   if area>1e-9:contact.append({'proposed_ceiling':ob['name'],'real_mount_top_contact_area_m2':area,'missing_mount_area_m2':mountshape.difference(section).area})
   hit=embedded_triangle_area(wt,ob)
   if hit is None:body.append({'object':ob['name'],'nonconvex':True})
   elif hit['embedded_surface_area_m2']>1e-9:body.append({'object':ob['name'],**hit})
  corr=[]
  for candidate in candidates:
   w=np.array(candidate)+T;corr.append({'local_emitter':candidate,'world_emitter':w.tolist(),'normal_world':[0,-1,0],'actual_lens_back_ray':ray(w,[0,1,0],slens+T,np.repeat('AST-STF-006 real opal',len(slens)),.1),'fixture_down_exit_ray':ray(w,[0,-1,0],wt,sfn,1),'scene_down_receiver':scene_ray(w,[0,-1,0])})
  backs.append({'id':l['id'],'proposed_mount':T.tolist(),'real_ceiling_mount_islands':len(mountshape.geoms),'real_mount_total_area_m2':mountshape.area,'proposed_ceiling_contacts':contact,'proposed_architecture_body_clips':body,'old_planned_emitter':l['emitter_world'],'old_planned_emitter_first_self_hit':ray(l['emitter_world'],[0,-1,0],wt,sfn,1),'center_at_real_lens_minus3mm_still_hits_guard':ray(T+np.array([.6,-.564,0]),[0,-1,0],wt,sfn,1),'verified_alternative_candidates':corr})
 # Every bay ceiling has genuine side-face contact with retained walls/partitions or new closures.
 ceilingrows=[];joiners=[o for o in old+new if ('backstage'in o['name'])and not any(q in o['name']for q in ['ceiling','soffit'])]
 for ob in new:
  if not (ob['name'].startswith('FP_backstage')and('ceiling'in ob['name']or'soffit'in ob['name'])):continue
  contacts=[]
  for ax in [0,2]:
   for plane in [ob['lo'][ax],ob['hi'][ax]]:
    shape=plane_section(ob['t'],ax,plane)
    for wall in joiners:
     if wall['lo'][ax]-EPS<=plane<=wall['hi'][ax]+EPS:
      wp=plane_section(wall['t'],ax,plane);area=shape.intersection(wp).area
      if area>1e-9:contacts.append({'support':wall['name'],'plane_axis':ax,'plane_value':float(plane),'actual_side_face_contact_area_m2':area,'support_class':'PROPOSED'if wall['name'].startswith('FP_')else'retained'})
  ceilingrows.append({'proposed_ceiling':ob['name'],'actual_side_contacts':contacts})
 data={'status':'PROPOSED_NEW_GEOMETRY_SCREEN_ONLY_NOT_BUILT_SOURCE_ACCEPTANCE','proposed_architecture_sha256':archsha,'retained_base_sha256':sha(ROOT/'assets/grand_lantern_theater_section/source/AST-CUL-005.blend'),'current_lighting_plan_sha256':sha(PLAN/'LIGHTING_ENCLOSURE_VIEW_PLAN.json'),'staff_source_sha256':sha(spath/manifest['source']),'staff_glb_sha256':sha(spath/manifest['export']),'architecture_object_count':len(new),'triangulation':'Constrained planar triangulation of each declared face; winding preserved. No fan fill of concave faces.','lantern_new_architecture_checks':lanterns,'ring_opal_checks':rings,'ring_to_cap_short_contacts':ringcontacts,'staff_downward_actual_lens_facet_tests':optical,'backstage_fixture_checks':backs,'backstage_ceiling_real_side_attachment':ceilingrows,'still_missing':['Six stage header/yoke/saddle derivative bodies are absent in this proposed architecture file. Their exact attachment and self-clearance remain unproved.','No new geometry has yet been authored/reopened in Blender. Proposed-geometry checks cannot replace that.'],'plan_mutated_during_run':sha(PLAN/'LIGHTING_ENCLOSURE_VIEW_PLAN.json')!=prior['pins']['plans']['LIGHTING_ENCLOSURE_VIEW_PLAN.json']};assert sha(path)==archsha; (OUT/'PROPOSED_ARCHITECTURE_LIGHT_EVIDENCE.json').write_text(json.dumps(data,indent=2)+'\n')
 summary={'new_architecture_fixture_unexpected_nonceramic_clips':[r for r in lanterns if any(any(k!='LANTERN_ivory_enamel'for k in c['actual_fixture_triangle_clipping'])for c in r['new_architecture_body_clips'])],'new_added_bracket_missing_interfaces':[r for r in lanterns if r['new_bracket_retained_pier_interface']and r['new_bracket_retained_pier_interface']['missing_area_m2']>1e-8],'ring_missing_contact':[(r['id'],r['unsupported_top_area_m2'])for r in rings if r['unsupported_top_area_m2']>1e-8],'ring_emitter_missing_backhit':[r['id']for r in rings if not r['planned_emitter_lens_back_ray']],'staff_missing_plate_contacts':[r['id']for r in backs if not r['proposed_ceiling_contacts']or any(c['missing_mount_area_m2']>1e-8 for c in r['proposed_ceiling_contacts'])],'staff_body_contacts':[r for r in backs if r['proposed_architecture_body_clips']],'staff_old_emitters_blocked':[r['id']for r in backs if r['old_planned_emitter_first_self_hit']],'ceilings_without_contacts':[r['proposed_ceiling']for r in ceilingrows if not r['actual_side_contacts']],'ring_actual_face_self_blockers':sum(x['self_hit']is not None for r in rings for x in r['actual_face_exit_and_receiver_rays'])};(OUT/'PROPOSED_ARCHITECTURE_LIGHT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
