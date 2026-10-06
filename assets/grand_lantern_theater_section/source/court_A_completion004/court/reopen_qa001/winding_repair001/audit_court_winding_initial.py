import json,collections,math,numpy as np
from pathlib import Path
R=Path('/workspace/scratch/375c2e438292/theater_resume/first_pass_plan/arrival_revision02/court_A_completion004/geometry_contract001')
c=json.loads((R/'COURT_A_GEOMETRY_CONTRACT.json').read_text());f=json.loads((R/'FULLER_REAR_MASS_CANDIDATE.json').read_text());p=json.loads((R/'printed_materials001/PRINTED_MATERIALS_CONTRACT.json').read_text())
rows=[(r,'architecture')for r in c['objects']]+[(r,r['surface_kind'])for r in f['asset']['parts']]+[(r,'printed')for r in [p['display_plate']]+p['pieces']]
results=[]
for r,kind in rows:
 name=r['name']; v=np.array(r.get('vertices_world',r.get('vertices')),dtype=np.float32).astype(float);faces=r['faces'];edges=collections.defaultdict(list)
 for i,face in enumerate(faces):
  for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))].append((a,b,i))
 bad_uses=[(e,u)for e,u in edges.items()if len(u)!=2];same=[(e,u)for e,u in edges.items()if len(u)==2 and u[0][:2]==u[1][:2]]
 adjacency=collections.defaultdict(list)
 for edge,uses in edges.items():
  if len(uses)==2:
   a,b=uses;adjacency[a[2]].append((b[2],int(a[:2]==b[:2])));adjacency[b[2]].append((a[2],int(a[:2]==b[:2])))
 signs={};components=[];contradictions=[]
 for i in range(len(faces)):
  if i in signs:continue
  signs[i]=0;todo=[i];comp=[]
  while todo:
   j=todo.pop();comp.append(j)
   for k,x in adjacency[j]:
    if k not in signs:signs[k]=signs[j]^x;todo.append(k)
    elif signs[k]!=(signs[j]^x):contradictions.append([j,k])
  components.append(comp)
 volume=lambda comp:sum(np.dot(v[face[0]]-v[0],np.cross(v[face[k]]-v[0],v[face[k+1]]-v[0]))/6 for i in comp for face in [faces[i][::-1] if signs[i] else faces[i]]for k in range(1,len(face)-1))
 volumes=[]
 if kind!='open_shaped_leaf':
  for comp in components:
   vol=volume(comp)
   if vol<0:
    for i in comp:signs[i]^=1
   volumes.append(abs(vol))
 else:
  for comp in components:
   if sum(signs[i]for i in comp)>len(comp)/2:
    for i in comp:signs[i]^=1
 flips=[i for i in range(len(faces))if signs[i]]
 negative_normals=[]
 if kind=='closed_support':
  sides=r['shape_controls']['sides'];rings=len(r['shape_controls']['centerline']);centers=[v[i*sides:(i+1)*sides].mean(0) for i in range(rings)]
  for fi,raw in enumerate(faces):
   face=raw[::-1]if signs[fi]else raw; pts=v[face];normal=np.cross(pts,np.roll(pts,-1,axis=0)).sum(0);normal=normal/np.linalg.norm(normal)
   direction=pts.mean(0)-(centers[fi//sides]+centers[fi//sides+1])/2 if fi<sides*(rings-1)else(centers[0]-centers[1]if fi==len(faces)-2 else centers[-1]-centers[-2]);dot=float(np.dot(normal,direction/np.linalg.norm(direction)))
   if dot<=0:negative_normals.append([fi,dot])
 row={'name':name,'kind':kind,'vertices':len(v),'faces':len(faces),'boundary_edges':sum(len(u)==1 for u in edges.values()),'nonmanifold_edges':sum(len(u)>2 for u in edges.values()),'same_direction_edges':len(same),'components':len(components),'contradictions':contradictions,'face_indices_to_reverse':flips,'component_volumes_after':volumes,'closed_support_inward_faces_after':negative_normals,'euler':len(v)-len(edges)+len(faces)}
 if same:row['same_direction_edge_witnesses']=[{'edge':e,'uses':u}for e,u in same]
 results.append(row)
print(json.dumps({'total':len(rows),'affected':[{k:v for k,v in r.items()if k!='same_direction_edge_witnesses'}for r in results if r['face_indices_to_reverse']or r['nonmanifold_edges']or r['contradictions']or r['closed_support_inward_faces_after']or(r['kind']!='open_shaped_leaf'and r['boundary_edges'])]},indent=2))
with (Path(__file__).resolve().parent/'ALL_157_ORIGINAL_TOPOLOGY_RERUN.json').open('x') as handle:
 json.dump(results,handle,indent=2)
