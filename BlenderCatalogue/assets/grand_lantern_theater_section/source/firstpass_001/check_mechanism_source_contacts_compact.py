"""Pure conservative geometry checks, no Blender/Godot. Reads current builder output."""
from pathlib import Path
import json,math,hashlib
O=Path(__file__).resolve().parent;R=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section')
p=json.loads((O/'mechanism_package_compact.json').read_text());g=json.loads((R/'source/geometry.json').read_text());old_removed=set(p['baseline_removal_by_parent_only'])
def bounds(v):return [[min(q[i]for q in v)for i in range(3)],[max(q[i]for q in v)for i in range(3)]]
def overlap(a,b,eps=2e-7):return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>eps for i in range(3))
src=[(o['name'],bounds(o['vertices_world']))for o in g['objects']if o['name']not in old_removed and o['role']!='preview_only']
motions={m['id']:m for m in p['motion_groups']};hits=[];allowed=[];counter=0
for o in p['objects']:
 b=bounds(o['vertices_world']);mid=o['motion_group'];swept=[b[0][:],b[1][:]]
 while mid:
  m=motions[mid];travel=m.get('travel_m',m.get('translation_range_m',[0,0])[-1]);axis=m['axis_world']
  for i in range(3):swept[0][i]+=min(0,travel*axis[i]);swept[1][i]+=max(0,travel*axis[i])
  mid=m.get('parent')
 for name,sb in src:
  if overlap(swept,sb):
   row={'new':o['name'],'existing':name,'swept_bounds':swept,'existing_bounds':sb};tag=o.get('intentional_fixed_bearing',{})
   if o['motion_group'] is None and tag.get('target')==name and tag.get('approved_engagement_m')==.015:allowed.append(row)
   else:hits.append(row)
 counter+=1
# Fixed anchorage witnesses refer to actual existing solid geometry or approved exact foundation polygon.
foundation=json.loads((R/'contracts/D11_FOUNDATION_OWNERSHIP_PROPOSAL.json').read_text());supports=[]
for o in p['objects']:
 tag=o.get('intentional_fixed_bearing',{})
 if tag.get('target')=='approved D11 foundation shaft-side INNER FACE':
  x=tag['plane_world_x'];y0,y1=tag['contact_world_y'];z0,z1=tag['contact_world_z'];segments=[]
  for poly in foundation['polygons']:
   ring=poly['boundary']
   for a,b in zip(ring,ring[1:]+ring[:1]):
    if abs(a[0]-x)<1e-9 and abs(b[0]-x)<1e-9 and min(a[1],b[1])<=z0 and max(a[1],b[1])>=z1:segments.append([a,b])
  ok=bool(segments) and foundation['datum_bottom_y']<=y0<y1<=foundation['datum_top_y'] and y1<69.5
  supports.append({'name':o['name'],'pass':ok,'actual_polygon_edge_witnesses':segments,'y_contact':[y0,y1],'pane_gap_m':69.5-y1})
 if 'targets'in tag:
  area=0;witness=[]
  for name in tag['targets']:
   sb=dict(src)[name];y=tag['plane_world_y'];area+=(sb[1][0]-sb[0][0])*(sb[1][2]-sb[0][2]);witness.append({'source':name,'top_y':sb[1][1],'bounds':sb,'correct_height':abs(sb[1][1]-y)<1e-9})
  supports.append({'name':o['name'],'pass':all(q['correct_height']for q in witness),'top_bearing_area_m2':area,'witnesses':witness})
# Independently test secondary self-contained continuous boxes (exclude the explicitly approved bearing overhang).
plan=json.loads((O/'SECONDARY_INTERFACE_DOOR_PLAN.json').read_text());secondary=[]
for d in plan['doors']:
 pre='THEATER_'+d['id'];b=[d['frame_and_continuous_leaf_sweep_bounds']['min'],d['frame_and_continuous_leaf_sweep_bounds']['max']];bad=[];n=0
 for o in p['objects']:
  if not o['name'].startswith(pre)or o.get('intentional_fixed_bearing'):continue
  q=bounds(o['vertices_world']);m=motions.get(o['motion_group'],{});a=m.get('axis_world',[0,0,0]);t=m.get('travel_m',0)
  for i in range(3):q[0][i]+=min(0,a[i]*t);q[1][i]+=max(0,a[i]*t)
  if any(q[0][i]<b[0][i]-2e-6 or q[1][i]>b[1][i]+2e-6 for i in range(3)):bad.append(o['name'])
  n+=1
 secondary.append({'id':d['id'],'parts_checked':n,'out_of_bounds':bad})
result={'scope':'Actual generated pure mesh vertex AABBs swept continuously; conservative source contact screen. Not Blender/import/runtime or structural strength acceptance.','package_sha256':hashlib.sha256((O/'mechanism_package_compact.json').read_bytes()).hexdigest(),'source_geometry_sha256':hashlib.sha256((R/'source/geometry.json').read_bytes()).hexdigest(),'new_parts_checked':counter,'existing_parts_checked':len(src),'unapproved_positive_aabb_contacts':hits,'exact_approved_secondary_fixed_bearings':allowed,'guide_anchor_source_witnesses':supports,'secondary_continuous_bounds':secondary}
result['pass']=not hits and len(allowed)==24 and all(x['pass']for x in supports)and all(not x['out_of_bounds']for x in secondary)
(O/'mechanism_compact_source_contact_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':result['pass'],'unapproved_contacts':hits,'allowed_secondary_bearings':len(allowed),'guide_anchors':supports,'secondary':secondary},indent=2))
