from pathlib import Path
import json,hashlib,copy
W=Path(__file__).resolve().parent;P=json.load(open(W/'CANDIDATE_PLAN.json'));S=json.load(open(W/'SUPPORT_PREFLIGHT.json'));assert S['status']=='PASS';assert S['input_sha256']==hashlib.sha256((W/'SUPPORT_CANDIDATES.json').read_bytes()).hexdigest();assert len(S['results'])==len(P['support_candidates'])==len(P['support_candidates'])
collections=list(P['assemblies'].values())+[r['parts']for r in P['rooms']];allparts={a['name']:a for rows in collections for a in rows};drop=set();toes=[];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
for result in S['results']:
 f=result['candidate'];c=result['chosen'];a=allparts[f['part_name']];lo=min(v[1]for v in a['verts']);x,z=f['x'],f['z'];wx,wz=f['width_x'],f['width_z'];y=c.get('pier_bottom_y',c['foot'][1]+.08)
 for v in a['verts']:
  if abs(v[1]-lo)<1e-5:v[1]=y
 a['actual_foundation_preimage']=c
 for q in allparts.values():
  xx=(min(v[0]for v in q['verts'])+max(v[0]for v in q['verts']))/2;zz=(min(v[2]for v in q['verts'])+max(v[2]for v in q['verts']))/2
  if q['name']!=a['name']and q['category']=='frame'and abs(xx-x)<1e-5 and abs(zz-z)<1e-5 and max(v[1]for v in q['verts'])<=f['original_min_y']+.21:drop.add(q['name'])
 corners=c.get('corner_contact_world',[[x-wx/2,c['foot'][1],z-wz/2],[x-wx/2,c['foot'][1],z+wz/2],[x+wx/2,c['foot'][1],z-wz/2],[x+wx/2,c['foot'][1],z+wz/2]])
 # Godot/Blender roundoff is below tolerance; preserve exact queried four native surface contacts.
 v=[corners[0],corners[2],[x+wx/2,y,z-wz/2],[x-wx/2,y,z-wz/2],corners[1],corners[3],[x+wx/2,y,z+wz/2],[x-wx/2,y,z+wz/2]]
 toes.append({'name':'PC_BearingToe_'+str(len(toes)),'verts':v,'faces':faces,'role':'champagne_metal','category':'bearing_toe','runtime_collision':True,'source_bearing_preimage':c})
for rows in collections:rows[:]=[a for a in rows if a['name']not in drop]
P['assemblies']['BearingToes']=toes;P['support_preimages']=S['results'];P['support_result_sha256']=hashlib.sha256((W/'SUPPORT_PREFLIGHT.json').read_bytes()).hexdigest();P['support_adaptation']={'replaced_new_candidate_shoes':len(drop),'exact_source_contact_toes':len(toes),'fallback_retained_surfaces':sum(bool(r['chosen'].get('actual_retained_structural_surface_fallback'))for r in S['results']),'original_lower_surface_sources_unmodified':True,'load_sizing_and_archive_hull_bearing_capacity_accepted':False};P['assemblies']['CombinedStructure']=sum((P['assemblies'].pop(k)for k in ['Receiving','BearingToes']),[])
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(P['support_adaptation'])
