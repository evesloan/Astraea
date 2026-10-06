from pathlib import Path
import json,math,collections,hashlib
O=Path(__file__).resolve().parent
old=json.loads((O/'mechanism_package.json').read_text());new=json.loads((O/'mechanism_package_compact.json').read_text());oldnames={o['name']:o for o in old['objects']};newnames={o['name']:o for o in new['objects']}
def hidden(name):return any(q in name for q in ['_SUSP_','_CAP_','_TRACK_','_TROLLEY_','_trolley_'])
visible=[o for o in old['objects']if not hidden(o['name'])]
changed=[o['name']for o in visible if newnames.get(o['name'])!=o]
negative=[];zero=[];degen=[];open_edges=[];compound=[];minimum=1e99
for o in new['objects']:
 v=o['vertices_world'];origin=v[0];vv=[[p[i]-origin[i]for i in range(3)]for p in v];volume=0.;mina=1e99;edges=collections.Counter();keys=[tuple(round(x,7)for x in q)for q in v]
 for f in o['faces']:
  for a,b in zip(f,f[1:]+f[:1]):
   if keys[a]!=keys[b]:edges[tuple(sorted([keys[a],keys[b]]))]+=1
  for k in range(1,len(f)-1):
   a,b,c=[vv[i]for i in [f[0],f[k],f[k+1]]];x=[b[i]-a[i]for i in range(3)];y=[c[i]-a[i]for i in range(3)];cross=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];mina=min(mina,math.sqrt(sum(q*q for q in cross))*.5)
   crossbc=[b[1]*c[2]-b[2]*c[1],b[2]*c[0]-b[0]*c[2],b[0]*c[1]-b[1]*c[0]];volume+=sum(a[i]*crossbc[i]for i in range(3))/6
 if volume< -1e-10:negative.append(o['name'])
 if abs(volume)<1e-12:zero.append(o['name'])
 if mina<1e-14:degen.append(o['name'])
 if any(n%2 for n in edges.values()):open_edges.append(o['name'])
 if any(n>2 for n in edges.values()):compound.append(o['name'])
 minimum=min(minimum,mina)
def bore_vertices(package):
 out=set()
 for o in package['objects']:
  if not('_CAP_'in o['name']and'_roof'in o['name']or'_TRACK_top'in o['name']):continue
  for x,y,z in o['vertices_world']:
   u=z+126;d=x+34.25;uc=round(u/.45)*.45;dc=.055 if d>0 else-.055
   if abs(math.hypot(u-uc,d-dc)-.0035)<2e-8:out.add((round(x,9),round(y,9),round(z,9)))
 return out
oldbores=bore_vertices(old);newbores=bore_vertices(new)
def category(o):
 n=o['name']
 if '_SUSP_'in n:return'main_fasteners'
 if '_CAP_'in n:return'main_caps_heads_exact_bores'
 if '_TRACK_'in n:return'main_tracks_exact_bores'
 if '_TROLLEY_'in n:return'main_trolleys'
 if '_trolley_'in n:return'gate_trolleys'
 if '_rail_'in n:return'gate_tracks'
 if n.startswith('THEATER_GUIDE'):return'lift_guides_posts_head'
 if n.startswith('THEATER_CABIN_CAB_'):return'retained_cabin'
 if '_LEAF_'in n:return'visible_retained_leaves'
 return'visible_frames_controls_brackets'
def costs(p):
 d={}
 for o in p['objects']:
  c=d.setdefault(category(o),{'parts':0,'triangles':0});c['parts']+=1;c['triangles']+=sum(len(f)-2 for f in o['faces'])
 return d
r={'scope':'Actual compact pure mesh topology, volume, unchanged visible/source geometry and exact cap-bore coordinates. No Blender/import/runtime.','full_package_sha256':hashlib.sha256((O/'mechanism_package.json').read_bytes()).hexdigest(),'compact_package_sha256':hashlib.sha256((O/'mechanism_package_compact.json').read_bytes()).hexdigest(),'motion_groups_exactly_unchanged':old['motion_groups']==new['motion_groups'],'markers_exactly_unchanged':old['markers']==new['markers'],'visible_objects_checked':len(visible),'changed_visible_objects':changed,'old_cap_bore_vertex_count':len(oldbores),'new_cap_bore_vertex_count':len(newbores),'cap_bore_vertices_identical':oldbores==newbores,'cap_bore_vertices_removed':list(oldbores-newbores)[:10],'cap_bore_vertices_added':list(newbores-oldbores)[:10],'negative_volumes':negative,'zero_volumes':zero,'degenerate_objects':degen,'open_boundaries':open_edges,'closed_compound_objects':compound,'minimum_triangle_area_m2':minimum,'before_costs':costs(old),'after_costs':costs(new)}
r['pass']=not any([changed,negative,zero,degen,open_edges])and oldbores==newbores and r['motion_groups_exactly_unchanged']and r['markers_exactly_unchanged']
(O/'mechanism_compact_mesh_checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in['closed_compound_objects','before_costs','after_costs']},indent=2));print('COSTS',json.dumps(r['after_costs'],indent=2))
