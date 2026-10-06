"""Fresh, source-precision-aware proposed geometry check. No scene engines or shared writes."""
from validate_practicals import *
from validate_proposed_architecture import proposed_objects

def quantize(ob):
 q={**ob};q['v']=np.array(ob['v'],dtype=np.float32).astype(float);q['t']=np.array(ob['t'],dtype=np.float32).astype(float);q['lo']=q['v'].min(0);q['hi']=q['v'].max(0);return q

def main():
 archpath=PLAN/'ARCHITECTURE_ADDITIONS_GEOMETRY.json';lpath=PLAN/'LIGHTING_ENCLOSURE_VIEW_PLAN.json';fpath=PLAN/'FIRST_PASS_ADDITIONS_PLAN.json';pins={p.name:sha(p)for p in [archpath,lpath,fpath]};raw=json.loads(archpath.read_text());L=json.loads(lpath.read_text())['fixtures'];new=proposed_objects(archpath);old=[quantize(o)for o in source_objects()];ob={o['name']:o for o in old};nb={o['name']:o for o in new};ol=np.array([o['lo']for o in old]);oh=np.array([o['hi']for o in old]);topo=[]
 for o in raw['objects']:
  edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)])))for f in o['faces']for i in range(len(f)));v=np.array(o['vertices_world']);bad=[]
  for i,f in enumerate(o['faces']):
   q=v[f]
   if len(set(f))<3 or np.linalg.norm(np.sum(np.cross(q,np.roll(q,-1,axis=0)),axis=0))<1e-9:bad.append(i)
  mesh=nb[o['name']];t=mesh['t']-v.mean(0);signed=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);topo.append({'name':o['name'],'vertex_count':len(v),'zero_area_faces':bad,'non_two_incident_edges':sum(n!=2 for n in edges.values()),'signed_closed_volume_m3':signed})
 overlaps=[];unknown=[];compares=0
 for n in new:
  ids=np.flatnonzero(np.all(oh>=n['lo']-EPS,1)&np.all(ol<=n['hi']+EPS,1))
  for i in ids:
   o=old[i];compares+=1;r=embedded_triangle_area(n['t'],o)
   if r is None:unknown.append({'proposed':n['name'],'retained':o['name']});continue
   if r['embedded_surface_area_m2']>1e-8:overlaps.append({'proposed':n['name'],'retained':o['name'],**r,'declared_contact':next(q.get('expected_retained_contact')for q in raw['objects']if q['name']==n['name'])})
 # Float32 correspondence is explicit, not an increased mesh-contact tolerance.
 lp,lm=glb(ROOT/'assets/hospitality_lantern/exports/AST-LGT-001.glb');lt=np.concatenate([p['t']for p in lp]);ln=np.concatenate([np.repeat(p['name'],len(p['t']))for p in lp]);mount=np.array(lm['DATUM_wall_mount']['position']);prev=json.loads((OUT/'PRACTICAL_LIGHT_TRIANGLE_EVIDENCE.json').read_text());lanterns=[]
 for l in L:
  if 'AST-LGT-001'not in l['asset']:continue
  if 'backplate_support_world'in l:
   theta=math.radians(float(l['id'].rsplit('_a',1)[1]))if l['group']=='gallery_soffit'else 0;R=np.array([[math.cos(theta),math.sin(theta),0],[0,0,-1],[-math.sin(theta),math.cos(theta),0]]);T=np.array(l['backplate_support_world'])-R@mount
  else:R=yaw(l['yaw_radians']);T=np.array(l['origin_world'])
  wt=np.float32(lt@R.T+T).astype(float);parts={p['name']:np.float32(p['t']@R.T+T).astype(float)for p in lp};plate=parts['LANTERN_ivory_enamel'];supportpos=np.float32(R@mount+T).astype(float);contacts=[];clips=[]
  candidates=[o for o in old+new if np.all(o['hi']>=wt.min((0,1))-EPS)and np.all(o['lo']<=wt.max((0,1))+EPS)]
  # Contact plane in world cardinal axis; no issue from locally rotated radial plate.
  if 'backplate_support_world'in l:axis=1;value=supportpos[1]
  else:axis=0;value=float(np.float32((R@np.array([0,mount[1],-.015 if l['group']=='side_route'else 0])+T)[0]))
  ceramic=plane_section(plate,axis,value);covered=[]
  for o in candidates:
   s=plane_section(o['t'],axis,value);a=ceramic.intersection(s).area
   if a>1e-9:contacts.append({'object':o['name'],'class':'proposed'if o['name']in nb else'retained','contact_area_m2':a});covered.append(s)
   for name,tris in parts.items():
    r=embedded_triangle_area(tris,o)
    if r is None:clips.append({'object':o['name'],'fixture_part':name,'nonconvex_unresolved':True})
    elif r['embedded_surface_area_m2']>1e-8 and name!='LANTERN_ivory_enamel':clips.append({'object':o['name'],'fixture_part':name,**r})
  me=R@np.array(lm['DATUM_light_exit']['position'])+T;lanterns.append({'id':l['id'],'current_plan_emitter_error_m':float(np.linalg.norm(me-l['emitter_world'])),'actual_contact_plane':{'axis':axis,'value':value},'contacts':contacts,'section_missing_area_m2':ceramic.difference(unary_union(covered)).area if covered else ceramic.area,'unexpected_nonceramic_body_clips':clips,'self_exit':ray(l['emitter_world'],R@np.array([0,0,1]),wt,ln,1)})
 staffparts,_=glb(ROOT/'assets/staff_overhead/exports/AST-STF-006.glb');staff=np.concatenate([p['t']for p in staffparts]);staffnames=np.concatenate([np.repeat(p['name'],len(p['t']))for p in staffparts]);backs=[]
 for l in L:
  if l['group']!='backstage':continue
  T=np.array(l['mount_world']);wt=np.float32(staff+T).astype(float);metal=np.float32(next(p['t']for p in staffparts if p['name']=='AST-STF-006__staff_zinc')+T).astype(float);lens=np.float32(next(p['t']for p in staffparts if p['name']=='AST-STF-006__staff_opal')+T).astype(float);y=float(np.float32(T[1]));shape=plane_section(metal,1,y);contacts=[]
  for n in new:
   if 'backstage'in n['name']and'ceiling'in n['name']:
    support=plane_section(n['t'],1,y);a=shape.intersection(support).area
    if a>1e-9:contacts.append({'ceiling':n['name'],'contact_area_m2':a,'missing_m2':shape.difference(support).area})
  backs.append({'id':l['id'],'current_emitter_world':l['emitter_world'],'matches_corrected_datum':np.linalg.norm(np.array(l['emitter_world'])-(T+[.45,-.564,0]))<1e-9,'actual_plate_support':contacts,'back_ray_actual_lens':ray(l['emitter_world'],[0,1,0],lens,None,.1),'actual_fixture_self_exit':ray(l['emitter_world'],[0,-1,0],wt,staffnames,1)})
 # Ring attachment at precise new actual levels, source ring quantized the same way.
 rt=np.concatenate([o['t']for o in old if o['name'].startswith('canopy_lantern_ring')]);rbot=plane_section(rt,1,float(np.float32(91)));ring=[]
 for i in range(16):
  n=nb[f'FP_ring_opal_segment_{i:02}'];top=plane_section(n['t'],1,n['hi'][1]);l=next(l for l in L if l['id']==f'canopy_ring_emitter_{i:02}');allring=np.concatenate([q['t']for q in new if q['name'].startswith('FP_ring_opal_segment')]);ring.append({'id':l['id'],'top_area_m2':top.area,'missing_retained_bronze_contact_m2':top.difference(rbot).area,'lens_backward_hit':ray(l['emitter_world'],[0,1,0],allring,None,.1),'self_exit':ray(l['emitter_world'],[0,-1,0],allring,None,1)})
 rodrows=[];head=ob['proscenium_head'];headlower=head['lo'][1];headface=plane_section(head['t'],1,headlower)
 for n in new:
  if n['name'].startswith('FP_stage_yoke_saddle'):
   sec=plane_section(n['t'],1,headlower);rodrows.append({'name':n['name'],'retained_head_plane_y':headlower,'actual_rod_section_m2':sec.area,'unsupported_section_m2':sec.difference(headface).area,'rod_end_embedment_m':n['hi'][1]-headlower,'lower_end_y':n['lo'][1],'head_derivative_lower_contact':'UNVERIFIED: actual six optical head/yoke derivatives absent'})
 tabrows=[];cloth=nb['FP_original_navy_cyclorama'];cy=cloth['hi'][1];clothsection=plane_section(cloth['t'],1,cy);rail=nb['FP_cyclorama_top_rail']
 for n in new:
  if n['name'].startswith('FP_cyclorama_tab_'):
   bottom=plane_section(n['t'],1,cy);clotharea=bottom.intersection(clothsection).area;hit=embedded_triangle_area(n['t'],rail);tabrows.append({'name':n['name'],'cloth_top_contact_area_m2':clotharea,'rail_real_triangle_embedment':hit})
 result={'status':'CURRENT_PROPOSED_SOURCE_PRECISION_SCREEN_NOT_ENGINE_OR_SAVED_SOURCE_ACCEPTANCE','input_sha256':pins,'retained_theater_blend_sha256':sha(ROOT/'assets/grand_lantern_theater_section/source/AST-CUL-005.blend'),'retained_geometry_sha256':sha(ROOT/'assets/grand_lantern_theater_section/source/geometry.json'),'source_precision_method':'New proposal is stored at float32 precision. Retained geometry and transformed retained fixture vertices are independently quantized to float32 world positions for like-for-like contact checks. Ray/contact epsilon remains 1e-7 m; not tolerance-relaxed runtime acceptance. Actual reopened derivative remains required.','mesh_topology':topo,'new_to_old_exact_solid_triangle_comparisons':compares,'new_to_old_positive_surface_intrusions':overlaps,'nonconvex_old_source_unresolved':unknown,'current_lantern_contacts':lanterns,'current_backstage_corrected_emitters_and_plates':backs,'current_ring_supports':ring,'present_stage_saddle_rod_to_head_contacts':rodrows,'cyclorama_tab_contacts':tabrows,'optical_heads':'Six actual head/yoke derivative meshes remain absent. Rod upper attachments alone do not certify lower yoke joints, optical placement or moving hood clearance.'};(OUT/'CURRENT_145_LIGHT_SOURCE_EVIDENCE.json').write_text(json.dumps(result,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n')
 summary={'input_sha256':pins,'topology_failures':[r for r in topo if r['zero_area_faces']or r['non_two_incident_edges']or r['signed_closed_volume_m3']<=0],'old_source_positive_intrusions':overlaps,'old_source_unresolved':unknown,'lantern_missing_contacts':[r['id']for r in lanterns if not r['contacts']],'lantern_unexpected_clips':[r for r in lanterns if r['unexpected_nonceramic_body_clips']],'backstage_bad_emitters':[r['id']for r in backs if not r['matches_corrected_datum']or r['actual_fixture_self_exit']],'backstage_missing_plates':[r['id']for r in backs if not r['actual_plate_support']or any(q['missing_m2']>1e-8 for q in r['actual_plate_support'])],'ring_missing_contacts':[r for r in ring if r['missing_retained_bronze_contact_m2']>1e-8],'rod_missing_upper_contact':[r for r in rodrows if r['actual_rod_section_m2']<1e-8 or r['unsupported_section_m2']>1e-8],'tab_missing_cloth_contact':[r['name']for r in tabrows if r['cloth_top_contact_area_m2']<1e-9],'tab_missing_rail_contact':[r['name']for r in tabrows if r['rail_real_triangle_embedment']is None or r['rail_real_triangle_embedment']['embedded_surface_area_m2']<1e-9],'inputs_changed_since_start':{p.name:sha(p)!=pins[p.name]for p in [archpath,lpath,fpath]}};(OUT/'CURRENT_145_LIGHT_SOURCE_SUMMARY.json').write_text(json.dumps(summary,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o))+'\n');print(json.dumps(summary,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o)))
if __name__=='__main__':main()
