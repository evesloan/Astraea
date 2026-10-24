"""Receiving successors for retained D05 rooms; no replacement room allocation."""
from pathlib import Path
import json,hashlib,struct,math,sys
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[3]; G=R/'Game'; P=G/'clinical_room_receiving_20261024'; E=P/'evidence'
P.mkdir(exist_ok=True); E.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'BlenderCatalogue/assets/group4_completion_20261011'))
from glb_geometry import triangles
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
clinic=G/'data/architecture/group3_clinical_full_20261011/CLINICAL.json'; c=json.loads(clinic.read_text())
definitions=G/'data/architecture/received_sections.json'; rs={q['programme_key']:q for q in json.loads(definitions.read_text())['sections']}
pins={str(p.relative_to(R)):sha(p)for p in [clinic,definitions,G/'data/generated/structural_meshes.json',G/'data/generated/received_structural_meshes.json',G/'data/architecture/REMAINING_BATCH_FLOORS.json']}
old_floor=[]
for rel in ['data/generated/structural_meshes.json','data/generated/received_structural_meshes.json','data/architecture/REMAINING_BATCH_FLOORS.json']:
 for row in json.loads((G/rel).read_text())['regions']:
  if abs(float(row['floor_y'])-21)<1e-5:old_floor.extend(Polygon(t)for t in row['triangles'])
kit=G/'assets/models/group3_clinical_full_20261011'
for name,expected in c['model_pins'].items():
 path=kit/name;assert sha(path)==expected;pins[str(path.relative_to(R))]=expected
 for n,faces,e in triangles(path):
  for f in faces:
   if abs(f[:,1]-21).max()<.00002:
    poly=Polygon(f[:,[0,2]])
    if poly.area>1e-8:old_floor.append(poly)
floor_union=unary_union(old_floor)
parts=[];rooms=[];ports=[];walls=[];new_floor=[]
def polys(g):return [g]if g.geom_type=='Polygon'else [p for p in g.geoms if p.geom_type=='Polygon']
def extrude(poly,lo,hi,name,role,key):
 from shapely.geometry.polygon import orient
 vs=[];fs=[]
 for p in polys(poly):
  if p.area<1e-8:continue
  p=orient(p,sign=1)
  for t in constrained_delaunay_triangles(p).geoms:
   cs=list(t.exterior.coords)[:3]
   if not t.exterior.is_ccw:cs.reverse()
   k=len(vs);vs += [[x,lo,z]for x,z in cs]+[[x,hi,z]for x,z in cs];fs += [[k,k+1,k+2],[k+5,k+4,k+3]]
  for ring in [p.exterior,*p.interiors]:
   cs=list(ring.coords)
   for (x,z),(xx,zz)in zip(cs,cs[1:]):
    k=len(vs);vs += [[x,lo,z],[xx,lo,zz],[xx,hi,zz],[x,hi,zz]];fs.append([k+3,k+2,k+1,k])
 if vs:parts.append(dict(name=name,verts=vs,faces=fs,role=role,room=key))
def prism_box(name,lo,hi,role,key):extrude(box(lo[0],lo[2],hi[0],hi[2]),lo[1],hi[1],name,role,key)
targets={'D05_directory_04':[-232.,-198.], 'D05_directory_09':[417.,451.], 'D05_directory_10':[418.,446.]}
for key in [f'D05_directory_{i:02d}'for i in range(3,11)]:
 r=rs[key]; source=G/'assets/models'/r['model_file'];assert sha(source)==r['source_sha256'];pins[str(source.relative_to(R))]=sha(source)
 room=dict(key=key,name=r['name'],model=str(source.relative_to(G)),source_hash=sha(source),translation=r['translation_xyz'],source_mesh_count=r['source_mesh_count'],source_floor_ids=r['floor_owner_ids'])
 rooms.append(room)
 for ti,t in enumerate(q for q in c['terminal_interfaces']if q['programme_key']==key):
  x,y,z=t['source_origin']; sign=1 if x>0 else -1; ident=key+'_'+t['role']; gate=None
  if key in targets:
   target=targets[key][ti]; path=[(x,z),(sign*53.15,z),(sign*53.15,target),(sign*50.5,target)]
   footprint=LineString(path).buffer(1.8,cap_style=2,join_style=2)
   # The fixed source pocket cassette bears against the existing wall; its
   # outboard apron is separately clipped against every retained floor.
   apron=box(min(sign*50.9,sign*51.65),target-3.85,max(sign*50.9,sign*51.65),target+3.85)
   footprint=footprint.union(apron)
   gate=[sign*51.3,21,target]
   wall_name='Enclosure_0_6'if key.endswith('09')else'Enclosure_0_5'
   walls.append(dict(room=key,source_name=wall_name,z=target,world_x=sign*51,clear_width=3.6,clear_height=2.4))
  else:
   distance=14 if key=='D05_directory_08'and t['role']=='soiled' else 21
   path=[(x,z),(x-sign*distance,z)];footprint=LineString(path).buffer(1.8,cap_style=2,join_style=2);gate=[x-sign*.22,21,z]
  missing=footprint.difference(floor_union)
  if key not in targets:assert missing.area<.0001,(key,'Existing rectangle must own approach',missing.area)
  if missing.area>1e-6:
   assert missing.intersection(floor_union).area<1e-7
   extrude(missing,20.76,21,ident+'_MissingOnlyFloor','staff_floor',key);new_floor.append(missing)
  extrude(footprint,24.2,24.38,ident+'_ReceivingCeiling','staff_white_paint',key)
  # Entry and interior discharge remain source-sized openings, never arbitrary
  # walls across existing circulation. The pocket apron is not a new room.
  entry=box(min(x-sign*1.1,x+sign*2),z-1.8,max(x-sign*1.1,x+sign*2),z+1.8)
  ex,ez=path[-1];end=box(ex-.35,ez-1.8,ex+.35,ez+1.8)
  if key in targets:end=end.union(box(min(sign*50.45,sign*51.15),ez-3.86,max(sign*50.45,sign*51.15),ez+3.86))
  edges=footprint.boundary.difference(entry.union(end))
  lines=[edges]if edges.geom_type=='LineString'else list(edges.geoms)
  for li,line in enumerate(lines):
   if line.length<.02:continue
   for suffix,w,lo,hi,role in [('Plinth',.16,21,21.16,'staff_zinc'),('Dado',.12,21.16,22.05,'staff_bluegrey_paint'),('Enamel',.12,22.05,24.2,'staff_white_paint'),('Cove',.2,24.04,24.2,'staff_zinc')]:
    extrude(line.buffer(w/2,cap_style=2,join_style=2),lo,hi,f'{ident}_Edge{li}_{suffix}',role,key)
  # Deliberate visible fixture housings, one at each end of long receiving paths.
  lightrows=[]
  length=LineString(path).length
  for i,fraction in enumerate([.25,.75]):
   q=LineString(path).interpolate(length*fraction);lx,lz=q.x,q.y
   prism_box(f'{ident}_Fixture{i}_Housing',[lx-.45,24.04,lz-.18],[lx+.45,24.2,lz+.18],'staff_zinc',key)
   prism_box(f'{ident}_Fixture{i}_Lens',[lx-.38,24.035,lz-.12],[lx+.38,24.055,lz+.12],'staff_opal',key)
   lightrows.append(dict(name=f'{ident}_TaskLight{i}',position=[lx,24.02,lz],range=8,energy=.8,color=[.8,.9,1]))
  ports.append(dict(id=ident,room=key,role=t['role'],source_terminal=t,path=[list(p)for p in path],footprint=[list(poly.exterior.coords)for poly in polys(footprint)],gate_position=gate,gate_yaw=math.pi/2,gate_operational=False,missing_floor_m2=missing.area,lights=lightrows))
assert len(rooms)==8 and len(ports)==16 and len(walls)==6
assert sum(p.area for p in new_floor)-unary_union(new_floor).area<1e-6
# Record the original exact source bounds and materials for the three enclosure
# owners. Geometry is cut from the actually loaded mesh by the runtime adapter.
wall_rows=[]
for room in rooms:
 rows=[w for w in walls if w['room']==room['key']]
 if not rows:continue
 meshes=list(triangles(G/room['model']));same=next(q for q in meshes if q[0]==rows[0]['source_name']);faces=same[1]+np.array(room['translation']);lo=faces.min((0,1));hi=faces.max((0,1))
 wall_rows.append(dict(room=room['key'],source_name=rows[0]['source_name'],source_triangles=len(faces),world_bounds=[lo.tolist(),hi.tolist()],cuts=rows))
native_root=R/'RetainedConstruction/group3/payloads/BlenderCatalogue/assets/group3_crew_service_20261009/extensions/clinical_full_transfer_batch020/source'
for file in ['AST-MED-G3-007.blend','AST-MED-G3-008.blend','AST-MED-G3-009.blend']:
 p=native_root/file;pins[str(p.relative_to(R))]=sha(p)
plan=dict(status='UNFINISHED_RECEIVING_SOURCE',parent='04db85ca5397f282245c499584efedc0e3ebd86b',rooms=rooms,ports=ports,parts=parts,walls=wall_rows,source_pins=pins,source_gate='res://assets/models/group3_clinical_full_20261011/AST-MED-G3-009.glb',native_library=str(native_root.relative_to(R)),new_floor_m2=sum(p.area for p in new_floor),new_room_ids=0,new_capacity=0,clinical_operation=False,source_support_holds=c['held_support_spans'])
(P/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(E/'SOURCE_SELECTION.json').write_text(json.dumps(dict(status='SOURCE_GAP_PROVEN',eight_existing_rooms=True,original_clinical_streets_already_installed=True,retained_floor_reuse_rooms=[r['key']for r in rooms if r['key']not in targets],chamfered_floor_connection_rooms=list(targets),new_floor_m2=plan['new_floor_m2'],parts=len(parts),ports=len(ports),original_meshes_not_rebuilt=True,clinical_gate_admission_unchanged=True),indent=2)+'\n')
print('PREPARED',len(parts),'parts',len(ports),'interfaces','new floor m2',plan['new_floor_m2'])
