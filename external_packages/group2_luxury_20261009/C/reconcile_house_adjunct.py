"""Precisely screen and revise only an unbuilt private adjunct proposal."""
import pathlib,json,sys,shutil
R=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from glb_tools import read_glb,clip
def clip_axis(poly,axis,bound,lower):
 if not poly:return []
 out=[];prev=poly[-1];pin=prev[axis]>=bound if lower else prev[axis]<=bound
 for v in poly:
  cin=v[axis]>=bound if lower else v[axis]<=bound
  if cin!=pin:
   t=(bound-prev[axis])/(v[axis]-prev[axis]);out.append(tuple(prev[k]+t*(v[k]-prev[k]) for k in range(len(v))))
  if cin:out.append(v)
  prev=v;pin=cin
 return out
def clipped(poly,bounds,axis_z=1):
 for axis,bound,lower in [(0,bounds[0],True),(0,bounds[1],False),(axis_z,bounds[2],True),(axis_z,bounds[3],False)]:poly=clip_axis(poly,axis,bound,lower)
 return poly
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
if __name__=='__main__':
 p=R/'EXCLUSIVE_FACILITIES_CROSSWALK.json';c=json.loads(p.read_text());prop=c['source_proposals'][0]
 b=[[-75,-404],[-64,-404],[-64,-386],[-75,-386]];bounds=[-75,-64,-404,-386];conflicts=[]
 inv=json.loads((R/'LUXURY_81_INVENTORY.json').read_text())
 for row in inv['records']:
  a=area(clipped(row['reservation']['proposed_floor_boundary'],bounds))
  if a>1e-5:conflicts.append({'source_unit':row['identity']['source_envelope_index'],'area':a})
 full=json.loads((R/'inputs/BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json').read_text())
 for row in full['records']:
  if row.get('production_lane')!='D17_retained_standard_replan':continue
  layout=row['candidate_layout'];poly=layout.get('proposed_floor_boundary')
  if poly is None:
   x0,x1=layout['proposed_x'];z0,z1=layout['proposed_z'];poly=[[x0,z0],[x1,z0],[x1,z1],[x0,z1]]
  a=area(clipped(poly,bounds))
  if a>1e-5:conflicts.append({'Group1_unit':row['source_envelope_index'],'area':a})
 for poly in [[[-97,-384],[-63,-384],[-63,-356],[-97,-356]],[[-97,-14],[-63,-14],[-63,14],[-97,14]],[[-97,356],[-63,356],[-63,384],[-97,384]]]:
  a=area(clipped(poly,bounds))
  if a>1e-5:conflicts.append({'protected_commons':poly,'area':a})
 struct=json.loads((R/'inputs_9311/Game/data/generated/structural_meshes.json').read_text())
 for row in struct['regions']:
  y=row['floor_y']
  if y<=102.0001 or y-row['thickness']>=105.3:continue
  for tri in row['triangles']:
   a=area(clipped(tri,bounds))
   if a>1e-5:conflicts.append({'structural_region':row['id'],'area':a});break
 _,nodes=read_glb(R/'inputs/Game/assets/models/AST-RES-TIDAL_floor_winding_r002.glb');contacts=[];candidates=[]
 for n in nodes:
  lo,hi=n['bounds']
  if hi[0]<-75 or lo[0]>-64 or hi[2]<-404 or lo[2]>-386 or hi[1]<102 or lo[1]>105.3:continue
  candidates.append(n['name'])
  for tri in n['triangles']:
   q=clipped(clip(clip([n['vertices'][i] for i in tri],102,True),105.3,False),bounds,2)
   if q:contacts.append({'node':n['name'],'triangle':tri,'actual_clipped_vertices':q});break
 print('Ownership conflicts',conflicts,'actual retained contacts',contacts);assert not conflicts and not contacts
 backup=R/'failed_source_attempts/port_forward_adjunct_old_proposal_wall_conflict';backup.mkdir(parents=True,exist_ok=True)
 if not (backup/p.name).exists():shutil.copy2(p,backup/p.name);shutil.copy2(R/'EXCLUSIVE_FACILITIES_PRECISE_LINE_SCREEN.json',backup/'PRECISE_LINE_SCREEN.json')
 prop['old_unbuilt_proposal_boundary']=prop['source_proposal_boundary'];prop['source_proposal_boundary']=b;prop['proposal_reconciliation']={'change':'Unbuilt own proposal translated one metre outboard within house court band','neighbours_moved_or_shrunk':False,'retained_wall_evidence':'failed_source_attempts/port_forward_adjunct_old_proposal_wall_conflict/PRECISE_LINE_SCREEN.json','actual_geometry_screen':'All retained clipped triangles including vertical projected lines clear; all81 units,19 retained standard allocations, commons and overhead structural regions clear'};p.write_text(json.dumps(c,indent=2))
 sp=R/'EXCLUSIVE_FACILITIES_PRECISE_LINE_SCREEN.json';s=json.loads(sp.read_text());s['records'][0]={'house':prop['house'],'boundary':b,'actual_triangles_or_degenerate_projected_lines_touching':contacts,'actual_node_aabb_candidates':candidates,'status':'CLEAR_ACTUAL_TRIANGLES_INCLUDING_LINES','previous_conflict_preserved':str(backup)};sp.write_text(json.dumps(s,indent=2))
