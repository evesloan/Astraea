"""Blender4.3.2 native connected avenue, offset commons portals and supported streets."""
import bpy,json,math,hashlib,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
G=Path(__file__).resolve().parents[2];B=G.parent/'BlenderCatalogue';N=B/'assets/night_garden_specialty_d15_20261020';P=G/'data/architecture/night_garden_specialty_d15_20261020/PACKAGE.json';p=json.loads(P.read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(G/'assets/models/AST-COM-003.glb'))
# Retain original source materials, not new global material polish.
mats={}
for o in bpy.context.scene.objects:
 if o.type=='MESH' and o.data.materials:
  if 'Wainscot' in o.name:mats['wood']=o.data.materials[0]
  if 'ProfileWall' in o.name:mats['wall']=o.data.materials[0]
  if 'Glass' in o.name or 'glass' in o.name:mats['glass']=o.data.materials[0]
for m in bpy.data.materials:m.use_fake_user=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
if 'glass' not in mats:
 m=bpy.data.materials.new('RetainedHospitalityGlassReceiver');m.diffuse_color=(.5,.7,.68,.2);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.2;mats['glass']=m
parts=[]
def box(name,lo,hi,role='wall',cat='architecture'):
 # Coordinates and contact extents are recorded in Godot world axes.
 x0,y0,z0=lo;x1,y1,z1=hi
 vs=[(x0,-z0,y0),(x1,-z0,y0),(x1,-z1,y0),(x0,-z1,y0),(x0,-z0,y1),(x1,-z0,y1),(x1,-z1,y1),(x0,-z1,y1)]
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],[tuple(reversed(face)) for face in fs]);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mats.get(role,mats['wall']));o['runtime_collision']=True;o['construction_role']=cat;o['material_role']='hospitality_glass' if role=='glass' else role
 parts.append({'name':name,'bounds':[lo,hi],'role':role,'category':cat});return o
# Exact bounded successors for four removed original wall pieces. Original GLB untouched.
patch=[]
for sign in [-1,1]:
 z0,z1=sorted([sign*13.92,sign*14.08])
 for family,y0,y1,role in [('ProfileWall',93.7,97.26,'wall'),('Wainscot',93,93.7,'wood')]:
  original=f'HC_{family}_D15_{sign}_4';names=[]
  for suffix,x0,x1,lo,hi in [('Left',86,89,y0,y1),('Right',92,93,y0,y1)]+([('Header',89,92,95.8,y1)] if family=='ProfileWall' else []):
   name='NG_Portal_'+original+'_'+suffix;box(name,[x0,lo,z0],[x1,hi,z1],role,'bounded_commons_wall_successor');names.append(name)
  patch.append({'source_mesh':original,'replacement_meshes':names,'source_file':'AST-COM-003.glb'})
 # New profiled inner portal reveal, keeping3m clear throat.
 for x in [88.91,92.09]:box(f'NG_PortalJamb_{sign}_{x}',[x-.07,93,z0-.16],[x+.07,95.82,z1+.16],'wood','portal_reveal')
 box(f'NG_PortalCrown_{sign}',[88.84,95.8,z0-.16],[92.16,96.02,z1+.16],'wood','portal_reveal')
 # Disjoint floor cells join existing commons face, turn west, and reach every unchanged room threshold.
 cells=[(89,92,14.08,26),(81.95,92,26,30),(81.95,86.05,30,97.4)]
 for j,(x0,x1,a,b) in enumerate(cells):
  zlo,zhi=sorted([sign*a,sign*b]);box(f'NG_{sign}_AvenueFloor_{j}',[x0,92.76,zlo],[x1,93,zhi],'wood','new_missing_street_floor');box(f'NG_{sign}_AvenueCeiling_{j}',[x0,96.74,zlo],[x1,96.9,zhi],'wall','continuous_ceiling')
  for x in [x0+.12,x1-.12]:box(f'NG_{sign}_LongitudinalBearing_{j}_{x}',[x-.1,92.34,zlo],[x+.1,92.76,zhi],'wood','connected_underside_bearing')
  for k in range(math.ceil((zhi-zlo)/3.7)+1):
   z=min(zhi-.08,zlo+.08+k*3.7)
   box(f'NG_{sign}_CrossBearing_{j}_{k}',[x0,92.44,z-.08],[x1,92.76,z+.08],'wood','connected_cross_bearing')
 # Boundary polyline: open exactly at commons portal and north/south home streets.
 # Short avenue is enclosed, with actual glazed courts, not floating floor strips.
 edges=[((89,14.08),(89,26)),((92,14.08),(92,30)),((81.95,26),(89,26)),((86.05,30),(92,30)),((81.95,26),(81.95,38.4)),((86.05,30),(86.05,38.4))]
 for j,((x0,z0),(x1,z1)) in enumerate(edges):
  z0*=sign;z1*=sign;lo=[min(x0,x1)-.07,93,min(z0,z1)-.07];hi=[max(x0,x1)+.07,93.85,max(z0,z1)+.07]
  box(f'NG_{sign}_CourtWallSill_{j}',lo,hi,'wood','court_enclosure');lo=lo.copy();hi=hi.copy();lo[1]=93.85;hi[1]=96.35;box(f'NG_{sign}_CourtGlass_{j}',lo,hi,'glass','sealed_court_view');lo=lo.copy();hi=hi.copy();lo[1]=96.35;hi[1]=96.74;box(f'NG_{sign}_CourtWallHead_{j}',lo,hi,'wall','court_enclosure')
 # Street terminus and side beyond final inner room. Preserve clear4.1m access lane.
 zz=sign*97.4;box(f'NG_{sign}_StreetEnd',[81.95,93,zz-.07],[86.05,96.74,zz+.07],'wall','end_condition')
 zlo,zhi=sorted([sign*90,sign*97.4]);box(f'NG_{sign}_EndSideSill',[81.88,93,zlo],[82.02,93.85,zhi],'wood','end_condition');box(f'NG_{sign}_EndSideGlass',[81.88,93.85,zlo],[82.02,96.35,zhi],'glass','sealed_court_view');box(f'NG_{sign}_EndSideHead',[81.88,96.35,zlo],[82.02,96.74,zhi],'wall','end_condition')
 for k,z in enumerate([34,45.7,53.1,60.5,67.9,75.3,82.7,90.1]):
  zz=z*sign;box(f'NG_{sign}_StreetRib_{k}',[81.95,96.55,zz-.13],[86.05,96.74,zz+.13],'wood','sectional_rib')
 # Visible integrated fixtures; runtime uses same positions.
 for k,z in enumerate([19,28,35,42,56.8,71.6,86.4,94]):
  x=90.5 if z<26 else (87 if z==28 else 84)
  zz=z*sign;box(f'NG_{sign}_FixtureHousing_{k}',[x-.3,96.48,zz-.22],[x+.3,96.74,zz+.22],'wood','fixture');box(f'NG_{sign}_FixtureLens_{k}',[x-.23,96.45,zz-.16],[x+.23,96.48,zz+.16],'wall','fixture_lens')
 # Supporting transverse floor-joists meet room slabs and street beams without entering lower homes.
 for r in p['rooms']:
  a=r['allocation'];cz=sum(a['allocation_z'])/2
  if cz*sign<0:continue
  x0,x1=a['allocation_x']
  for k,z in enumerate([a['allocation_z'][0]+.22,a['allocation_z'][1]-.22]):box(f'NG_{a["source_envelope_index"]}_RoomBearing_{k}',[x0,92.44,z-.08],[x1,92.76,z+.08],'wood','room_slab_receiving')
# Material-batch optimization retains named contact geometry in native source; glTF remains editable.
native=N/'NightGardenD15ConnectedReceiving_r002.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
out=G/'assets/models/NightGardenD15ConnectedReceiving_r002.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_cameras=False,export_lights=False)
p['receiving']={'model_file':out.name,'model_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native_source':str(native.relative_to(B)),'native_source_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'parts':parts,'commons_patch':patch,'commons_source_sha256':p['preimage_pins']['assets/models/AST-COM-003.glb'],'engineering_load_capacity_accepted':False}
P.write_text(json.dumps(p,indent=2)+'\n');print('RECEIVING_BUILT',len(parts))
