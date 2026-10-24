"""Source-owned D01/D06 transfer successors; no operating admission."""
from pathlib import Path
import json,hashlib,sys,math
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[3];G=R/'Game';P=G/'clinical_transfer_junctions_20261024';E=P/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(R/'BlenderCatalogue/assets/group4_completion_20261011'));from glb_geometry import triangles
old=json.loads((G/'clinical_return_links_20261024/PLAN.json').read_text());recv=json.loads((G/'clinical_room_receiving_20261024/PLAN.json').read_text());native=old['native_library'];legacy=json.loads((R/native/'CLINICAL_COMPLETE_ARCHITECTURE.json').read_text());contract=json.loads((G/'data/architecture/group3_clinical_full_20261011/CLINICAL.json').read_text())
pins=dict(old['source_pins'])
for rel in ['Game/clinical_return_links_20261024/PLAN.json','Game/clinical_return_links_20261024/adapter.gd','Game/clinical_room_receiving_20261024/adapter.gd','Game/assets/models/SOL_D05_directory_01_remaining_batch.glb','Game/assets/models/SOL_D05_directory_06_source001.glb']:
 pins[rel]=sha(R/rel)
parts=[]
def polys(g):
 if g.is_empty:return []
 return [g]if g.geom_type=='Polygon'else [p for p in g.geoms if p.geom_type=='Polygon']
def extrude(g,lo,hi,name,role,zone):
 from shapely.geometry.polygon import orient
 vs=[];fs=[]
 for p in polys(g):
  if p.area<1e-8:continue
  p=orient(p,sign=1)
  for t in constrained_delaunay_triangles(p).geoms:
   cs=list(t.exterior.coords)[:3]
   if not t.exterior.is_ccw:cs.reverse()
   k=len(vs);vs += [[x,lo,z]for x,z in cs]+[[x,hi,z]for x,z in cs];fs += [[k,k+1,k+2],[k+5,k+4,k+3]]
  for ring in [p.exterior,*p.interiors]:
   for (x,z),(xx,zz)in zip(list(ring.coords),list(ring.coords)[1:]):
    k=len(vs);vs += [[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,zz]];fs.append([k+3,k+2,k+1,k])
 if vs:parts.append(dict(name=name,role=role,zone=zone,verts=vs,faces=fs))
def facepolys(rows,y):
 out=[]
 for row in rows:
  vs=np.array(row['verts'])
  for ids in row['faces']:
   f=vs[ids]
   if abs(f[:,1]-y).max()<.00003:
    p=Polygon(f[:,[0,2]])
    if p.area>1e-8:out.append(p)
 return out
floors=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 for row in json.loads((G/rel).read_text())['regions']:
  if abs(row['floor_y']-21)<.00001:floors.extend(Polygon(t)for t in row['triangles'])
for name in contract['model_pins']:
 for n,faces,e in triangles(G/'assets/models/group3_clinical_full_20261011'/name):
  for f in faces:
   if abs(f[:,1]-21).max()<.00002:
    q=Polygon(f[:,[0,2]])
    if q.area>1e-8:floors.append(q)
floors.extend(facepolys(old['parts']+recv['parts'],21));floors=unary_union(floors)
# Core chamber polygon has a deliberate notch around the unchanged Pool bearing.
pool=box(-58.85,-403.85,-55.15,-398.15)
configs=[dict(id='D01_Pool',chamber=pool,paths=[[[-57,-411],[-57.45,-411],[-57.45,-402],[-57,-402],[-57,-392]],[[-48,-402],[-57,-402],[-57,-400],[-63.4,-400]]],gates=[[-57.45,21,-406.4,0],[-57,21,-396,0],[-53.05,21,-402,math.pi/2],[-61.3,21,-400,math.pi/2]],original='D05_directory_01',endcaps=[]),dict(id='D06_Royalty',chamber=box(98.6,18,106.6,26),paths=[[[102,12],[102.6,12],[102.6,38],[102,38]],[[95.1,30],[95.1,22],[110.6,22]]],gates=[[102.6,21,18,0],[102.6,21,26,0],[98.6,21,22,math.pi/2],[106.6,21,22,math.pi/2]],original='D05_directory_06',endcaps=[[97.0,28.08,97.14,31.92],[104.46,28.06,104.6,31.94]])]
# Add narrow cassette-pocket aprons without creating new rooms or doubling floor.
for c in configs:
 clear=unary_union([LineString(p).buffer(1.85,cap_style=3,join_style=2)for p in c['paths']]);foot=c['chamber'].union(clear)
 if c['id']=='D01_Pool':
  # Keep the protected bearing recess out of floor/wall authoring and source cuts.
  foot=foot.difference(box(-61.5,-406.14,-59.45,-403.78))
 c['clear']=clear;c['foot']=foot
 for x,y,z,yaw in c['gates']:
  apron=box(x-3.78,z-.15,x+3.78,z+.15)if yaw==0 else box(x-.15,z-3.78,x+.15,z+3.78)
  foot=foot.union(apron)
 c['foot']=foot
# Physical supports must not be touched by either footprint or cassette solids.
protected=[box(107.6,29,108.4,30.2),box(107.6,49.8,108.4,51),box(99.6,29,100.4,30.2),box(-61.3,-406.08,-59.9,-403.92),box(-53.6,-460.2,-53.4,-406)]
for c in configs:
 for b in protected:assert c['foot'].intersection(b).area<1e-7,(c['id'],b.bounds,c['foot'].intersection(b).area)
# Source-defined old coverage and retained successor footprint allow missing-only walls/ceilings.
def legacy_at(lo,hi):return unary_union([Polygon(q['boundary'],q['holes'])for q in legacy['parts']if q['y'][0]<hi and q['y'][1]>lo])
old_foot=unary_union([Polygon(q)for r in old['routes']for q in r['footprint']]);old_ceil=unary_union(facepolys(old['parts'],25.2));old_walls=unary_union(facepolys(old['parts'],21))
zones=[];gate_rows=[];cut_boxes=[]
for c in configs:
 zone=c['id'];foot=c['foot'];outer=foot.buffer(.14,join_style=2);missing=outer.difference(floors)
 # Native floor never occupies a retained support.
 missing=missing.difference(unary_union(protected))
 extrude(missing,20.76,21,zone+'_MissingOnlyFloor','staff_floor',zone)
 ceiling=outer.difference(unary_union(protected)).difference(legacy_at(25.2,25.38).union(old_ceil));extrude(ceiling,25.2,25.38,zone+'_Ceiling','staff_white_paint',zone)
 opens=[]
 for path in c['paths']:
  for end,adj in [(path[0],path[1]),(path[-1],path[-2])]:
   x,z=end;dx,dz=x-adj[0],z-adj[1]
   opens.append(box(x-2.1,z-.3,x+2.1,z+.3)if abs(dz)>abs(dx)else box(x-.3,z-2.1,x+.3,z+2.1))
 # Branch endpoints lie on existing route interiors; open all coincident route overlaps.
 wall=outer.difference(foot).difference(unary_union(protected).buffer(.02,join_style=2)).difference(unary_union(opens)).difference(old_foot)
 for suffix,lo,hi,role in [('Dado',21,22.02,'staff_bluegrey_paint'),('Enamel',22.02,25.2,'staff_white_paint')]:
  existing=legacy_at(lo,hi).difference(foot)
  for i,p in enumerate(polys(wall.difference(existing))):extrude(p,lo,hi,f'{zone}_{suffix}_{i}',role,zone)
 for i,b in enumerate(c['endcaps']):extrude(box(*b),21,25.2,f'{zone}_RetiredSpurClosure{i}','staff_white_paint',zone)
 for i,g in enumerate(c['gates']):
  x,y,z,yaw=g;ident=c['original']+'_crossing_'+str(i);before=next(q for q in contract['proposed_gate_bindings']if q['name']==ident)
  gate_rows.append(dict(name=ident,zone=zone,position=g[:3],yaw=yaw,prior_position=before['position'],prior_yaw=before['yaw'],existing=i>=0 and c['id']=='D06_Royalty',aperture=[3.7,3.3],original_aperture=[3.6,2.4],persistent_id=None,axis=before['axis']))
  transom=box(x-3.77,z-.14,x+3.77,z+.14)if yaw==0 else box(x-.14,z-3.77,x+.14,z+3.77)
  extrude(transom,24.45,25.2,ident+'_TallCassetteTransom','staff_white_paint',zone)
 lights=[]
 for i,path in enumerate(c['paths']):
  line=LineString(path)
  for j,t in enumerate([.3,.7]):
   q=line.interpolate(line.length*t);x,z=q.x,q.y;name=f'{zone}_Task{i}_{j}'
   extrude(box(x-.45,z-.18,x+.45,z+.18),25.04,25.2,name+'_Housing','staff_zinc',zone);extrude(box(x-.38,z-.12,x+.38,z+.12),25.035,25.055,name+'_Lens','staff_opal',zone);lights.append(dict(name=name,position=[x,25.02,z],energy=.8,range=8,color=[.8,.9,1]))
 # Orthogonal polygons are triangulated into rectangles by unique coordinate cuts.
 xs=sorted(set(round(x,6)for p in polys(foot)for ring in [p.exterior,*p.interiors]for x,z in ring.coords));zs=sorted(set(round(z,6)for p in polys(foot)for ring in [p.exterior,*p.interiors]for x,z in ring.coords))
 boxes=[]
 for xa,xb in zip(xs,xs[1:]):
  for za,zb in zip(zs,zs[1:]):
   b=box(xa,za,xb,zb)
   if foot.covers(b.representative_point()):boxes.append([xa,za,xb,zb])
 assert unary_union([box(*b)for b in boxes]).symmetric_difference(foot).area<1e-7
 # Merge contiguous cells to avoid quadratic runtime triangle clipping.
 merged=unary_union([box(*b)for b in boxes]);rects=[]
 for za,zb in zip(zs,zs[1:]):
  segments=[]
  for xa,xb in zip(xs,xs[1:]):
   if merged.covers(box(xa,za,xb,zb).representative_point()):
    if segments and abs(segments[-1][2]-xa)<1e-7:segments[-1][2]=xb
    else:segments.append([xa,za,xb,zb])
  for b in segments:
   match=next((r for r in rects if r[0]==b[0]and r[2]==b[2]and r[3]==b[1]),None)
   if match:match[3]=b[3]
   else:rects.append(b)
 cut_boxes+=rects;zones.append(dict(id=zone,paths=c['paths'],footprint=[dict(boundary=list(p.exterior.coords),holes=[list(r.coords)for r in p.interiors])for p in polys(foot)],new_floor_m2=missing.area,lights=lights))
plan=dict(parent='1d0753d31a6315920e8a11f1cf98e3f182626579',status='UNFINISHED_TRANSFER_LAYOUT_SUCCESSOR',source_pins=pins,native_library=native,parts=parts,zones=zones,gates=gate_rows,cut_boxes_xz=cut_boxes,protected_supports=old['protected_supports'],pool_bearing=old['pool_bearing'],source_gate='res://assets/models/group3_clinical_full_20261011/AST-MED-G3-009.glb',provider_status={'runtime_providers_installed':False,'retained_slider':'RetainedConstruction/group3/payloads/Game/scripts/group3_clinical_full_20261011/sliding_gate.gd','full_crossing_controller':'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_full_transfer_batch020/qa/rejected_runtime_contract_candidate003/crossing_buffer.gd','adoption':'HELD; rejected crossing source not adopted; original slider dimensions require reviewed successor'},new_floor_m2=sum(z['new_floor_m2']for z in zones),new_capacity=0,operating_ids_added=0,clinical_operation=False,aperture_successor={'original_height':2.4,'clear_height':3.3,'preserve_bottom_detail_to_y':.04,'top_detail_from_y':2.36,'top_offset':.9,'original_width':3.6,'width':3.7,'pocket':1.9})
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('Prepared',len(parts),'parts',len(cut_boxes),'cut rectangles',plan['new_floor_m2'],'floor m2')
# Exact installed preimages are inherited from the bounded actual-world survey.
survey=json.loads((E/'INSTALLED_NEIGHBORS.json').read_text());patches=[]
for row in survey['owners'].values():
 path=row['mesh_path']
 if '/screen_wall_' in path or '/ThroughRouteBatch_' in path:
  patches.append(dict(path=path,bounds=row['bounds'],triangles=row['faces'],max_y=25.21))
# Receiving room batches are deterministic local material groups, including its
# lower ceiling. The new dogleg avoids both pre-existing fixture housings.
groups={}
for part in recv['parts']:groups.setdefault(part['room']+'/'+part['role'],[]).append(part)
for index,(key,rows)in enumerate(groups.items()):
 if not key.startswith('D05_directory_06/')or key.split('/')[1]not in ['staff_white_paint','staff_bluegrey_paint','staff_zinc']:continue
 vs=np.array([v for p in rows for v in p['verts']]);count=sum(len(f)-2 for p in rows for f in p['faces']);path='ShipSpace/Districts/ReceivedSections/D05_directory_06/ClinicalRoomReceiving20261024/ReceivingBatch_%03d'%index
 patches.append(dict(path=path,bounds=[vs.min(0).tolist(),vs.max(0).tolist()],triangles=count,max_y=24.39))
# These six names are partition jambs/heads, not load-bearing ship supports.
roomcuts=[]
for name,faces,e in triangles(G/'assets/models/SOL_D05_directory_01_remaining_batch.glb'):
 if name in ['A_Service_separator_-50_pier1','A_Service_separator_-50_head1','A_Service_separator_-50_pier2','A_soiled_receiving_notch_pier0','A_soiled_receiving_notch_head0','A_soiled_receiving_notch_pier1']:
  roomcuts.append(dict(name=name,bounds=[faces.min((0,1)).tolist(),faces.max((0,1)).tolist()],triangles=len(faces),boxes=[[-53.25,-403.85,-47.9,-400.15]],max_y=24.3))
assert len(roomcuts)==6
plan.update(patches=patches,room_cuts=roomcuts,room_key='D05_directory_01',room_source='res://assets/models/SOL_D05_directory_01_remaining_batch.glb',room_receiving='D05_directory_01Receiving_WIP')
# Seal exposed skin edges from authored prism boundaries. This adds only reveal
# faces; retained UV-bearing outside skins are cut from their actual loaded mesh.
clear=unary_union([box(*b)for b in cut_boxes]);sources=[]
priorclear=unary_union([box(*b)for b in old['cut_boxes_xz']])
for i,row in enumerate(legacy['parts']):
 if row['category']=='screen_wall':sources.append((f'Legacy{i}',Polygon(row['boundary'],row['holes']).difference(priorclear),row['y'],row['role']))
for package,rows in [('Through',old['parts']),('Receiving',recv['parts'])]:
 for i,row in enumerate(rows):
  if package=='Receiving'and row['room']!='D05_directory_06':continue
  vs=np.array(row['verts']);lo,hi=vs[:,1].min(),vs[:,1].max()
  if lo<20.99 or hi<=21.01 or lo>=25.2:continue
  footprint=unary_union([Polygon(vs[f][:,[0,2]])for f in row['faces']if Polygon(vs[f][:,[0,2]]).area>1e-8])
  if footprint.is_empty:continue
  sources.append((package+str(i),footprint,[float(lo),float(hi)],row['role']))
for name,poly,ys,role in sources:
 if not poly.intersects(clear):continue
 edges=poly.difference(clear).boundary.intersection(clear.boundary);lines=[edges]if edges.geom_type=='LineString'else list(edges.geoms)
 for j,line in enumerate(lines):
  if line.geom_type!='LineString' or line.length<1e-7:continue
  for k,((x,z),(xx,zz))in enumerate(zip(list(line.coords),list(line.coords)[1:])):
   lo,hi=ys;zone='D01_Pool'if x<0 else'D06_Royalty';dx,dz=xx-x,zz-z;length=math.hypot(dx,dz)
   from shapely.geometry import Point
   inward=clear.covers(Point((x+xx)/2-dz/length*.0001,(z+zz)/2+dx/length*.0001));face=[0,1,2,3]if inward else[3,2,1,0]
   parts.append(dict(name=f'{name}_Reveal{j}_{k}',role=role,zone=zone,verts=[[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,z]],faces=[face]))
# Six source jamb/head caps retain the rest of the original beveled meshes.
for row in roomcuts:
 lo,hi=row['bounds'];x0,x1=lo[0],hi[0];y0,y1=lo[1],hi[1]
 for z in [-403.85,-400.15]:
  if lo[2]<z<hi[2]:parts.append(dict(name=row['name']+'_CutCap'+str(z),role='staff_white_paint',zone='D01_Pool',verts=[[x0,y0,z],[x1,y0,z],[x1,24.3,z],[x0,24.3,z]],faces=[[0,1,2,3]if z==-403.85 else[3,2,1,0]]))
 if y0<24.3<y1:
  za=max(lo[2],-403.85);zb=min(hi[2],-400.15)
  parts.append(dict(name=row['name']+'_HeadSoffit',role='staff_white_paint',zone='D01_Pool',verts=[[x0,24.3,za],[x1,24.3,za],[x1,24.3,zb],[x0,24.3,zb]],faces=[[0,1,2,3]]))
plan['parts']=parts
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('Final',len(parts),'parts',len(patches),'installed partition preimages',len(roomcuts),'streamed receiver successors')
