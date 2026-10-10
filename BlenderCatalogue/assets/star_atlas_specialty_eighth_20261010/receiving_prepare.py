from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));U=json.load(open(R/'Game/data/architecture/STAR_ATLAS_UNITS.json'));C=json.load(open(R/'Game/data/architecture/STAR_ATLAS_SPECIALTY_FOURTH.json'))['receiving'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[];lower=[];supports=[];joints=[];floor_joints=[];guards=[];floor_sources=[];footprints=[]
def cube(name,lo,hi,category):
 vs=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];parts.append({'name':name,'verts':vs,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'category':category,'runtime_collision':True})
regions=json.load(open(R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'))['regions']
for name in ['structural_meshes.json','received_structural_meshes.json']:regions+=json.load(open(R/'Game/data/generated'/name))['regions']
for q in regions:
 if q['floor_y']==93:footprints.extend(Polygon(t)for t in q['triangles'])
for f in sorted((R/'Game/data/architecture').glob('STAR_ATLAS_SPECIALTY_*.json')):
 if f.name=='STAR_ATLAS_SPECIALTY_EIGHTH.json':continue
 d=json.load(open(f));floor_sources.append(str(f.relative_to(R)))
 for room in d.get('rooms',[]):
  for part in room.get('parts',[]):
   v=np.array(part['verts']);lo=v.min(0);hi=v.max(0)
   if part.get('category')=='floor'and abs(hi[1]-93)<1e-8:footprints.append(box(lo[0],lo[2],hi[0],hi[2]))
 for part in d.get('receiving',d).get('parts',[]):
  v=np.array(part['verts']);lo=v.min(0);hi=v.max(0)
  if part.get('category')=='D15_street_extension_floor'and abs(hi[1]-93)<1e-8:footprints.append(box(lo[0],lo[2],hi[0],hi[2]))
old_floors=unary_union(footprints)
for room in P['rooms']:
 idx=room['allocation']['source_envelope_index'];a=room['allocation'];z=sum(a['allocation_z'])/2;xlo,xhi=a['allocation_x'];u=room['below_unit'];proto=next(p for p in U['prototypes']if p['key']==u['source_recipe_key']);assert sha(R/proto['editable_source'])==proto['editable_source_sha256'];lower.append({'source_index':idx,'owner':u['rebuild_identity'],'allocation_sha256':u['allocation_sha256'],'native_source':proto['editable_source'],'native_sha256':proto['editable_source_sha256'],'runtime_source':proto['model_file'],'runtime_sha256':proto['sha256'],'origin':u['source_origin_world_xyz'],'yaw':u['source_yaw_godot'],'persistent_structure_only':True,'selected_prefixes':['SUI_Floor','SUI_Ceiling_','SUI_Wall_'],'contacts':room['receiving_contacts']})
 for v in [-3.35,-1.7,0,1.7,3.35]:cube(f'SA{idx}_D15FloorJoist_{v}',[xlo,92.6,z+v-.08],[xhi,92.76,z+v+.08],'D15_room_floor_joist')
 for x in [xlo+.1,(xlo+xhi)/2,xhi-.1]:cube(f'SA{idx}_D15RoomTie_{x}',[x-.1,92.6,z-3.5],[x+.1,92.76,z+3.5],'D15_room_transverse_tie')
 for v in [-3.3,0,3.3]:
  zz=z+v;toe=box(-85.9,zz-.1,-85.7,zz+.1);owners=[o for o in regions if o['floor_y']==88.5 and unary_union([Polygon(t)for t in o['triangles']]).buffer(1e-7).covers(toe)];assert len(owners)==1;owner=owners[0];assert owner['thickness']==.24
  cube(f'SA{idx}_D14StreetToD15Pier_{v}',[-85.9,88.5,zz-.1],[-85.7,92.6,zz+.1],'D14_source_street_to_D15_room_and_bridge_pier');supports.append({'name':parts[-1]['name'],'position':[-85.8,88.5,zz],'full_toe_area_m2':.04,'owner':owner['id'],'deck':'D14','new_pier':True})
  cube(f'SA{idx}_D15RoomStreetCrossbeam_{v}',[xlo,92.6,zz-.1],[-81.95,92.76,zz+.1],'D15_outer_room_and_new_street_floor_crossbeam')
  cube(f'SA{idx}_D14WestFloorRimJoin_{v}',[xlo,88.1,zz-.1],[-85.7,88.28,zz+.1],'D14_outer_floor_rim_cantilever_receiving');floor_joints.append({'name':parts[-1]['name'],'source_owner':owner['id'],'floor_y':88.5,'source_thickness':.24,'source_bottom':88.26,'overlap_bounds':[[-85.9,88.26,zz-.1],[-85.7,88.28,zz+.1]],'basis':'Exact0.02m retained slab overlap; cantilever/load capacity held'})
for side,lo,hi,opening in [('North',-97.4,-90,[-95.54,-92.06]),('South',90,97.4,[92.06,95.54])]:
 rect=box(-86.05,lo,-81.95,hi);assert rect.intersection(old_floors).area<1e-6,'Unexpected existing D15 floor overlap';cube(f'SA_D15_{side}_EighthStreetFloor',[-86.05,92.76,lo],[-81.95,93,hi],'D15_street_extension_floor')
 for x in [-85.8,-82.2]:
  zlo,zhi=(lo,-89.9)if side=='North'else(89.9,hi);cube(f'SA_D15_{side}_EighthLongitudinal_{x}',[x-.1,92.6,zlo],[x+.1,92.76,zhi],'D15_missing_street_longitudinal_frame')
  original=next(q for q in C['parts']if q['name']==f'SA_D15_{side}_FourthLongitudinal_{x}');ov=np.array(original['verts']);a,b=([-90,-89.9]if side=='North'else[89.9,90]);joints.append({'name':parts[-1]['name'],'existing_model':C['model_file'],'existing_mesh':original['name'],'overlap_bounds':[[x-.1,92.6,a],[x+.1,92.76,b]],'basis':'Exact0.1m overlap into retained fourth street frame; load capacity held'})
 intervals=[[lo,opening[0]],[opening[1],hi]]
 for n,(a,b)in enumerate(intervals):cube(f'SA_D15_{side}EighthWestGuardSegment_{n}',[-86.05,93,a],[-85.98,94.1,b],'new_street_west_guard_outside_entry')
 guards.append({'side':side,'full_interval':[lo,hi],'entry_openings':[opening],'guard_intervals':intervals})
 cube(f'SA_D15_{side}_EighthEastGuard',[-82.02,93,lo],[-81.95,94.1,hi],'new_street_east_guard')
 end=lo if side=='North'else hi;cube(f'SA_D15_{side}_EighthTerminalGuard',[-86.05,93,end-.035],[-81.95,94.1,end+.035],'new_street_terminal_guard')
paths=['Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/assets/models/'+C['model_file'],'Game/docs/master_source/MASTER_CURRENT_APPLICATION.json','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']+floor_sources
Q={'schema':'astraea.star_atlas_specialty_receiving.v1','base_commit':'f9332c0b27060afa893835c48031c2b34038df10','model_file':'StarAtlasSpecialtyEighthReceiving.glb','parts':parts,'support_toes':supports,'lower_structural_owners':lower,'source_pins':{f:sha(R/f)for f in paths},'culling_preserved':True,'new_units':0,'new_source_ids':0,'structural_capacity_accepted':False,'removed_terminal_guard_names':['SA_D15_North_FourthTerminalGuard','SA_D15_South_FourthTerminalGuard'],'receiving_model_preimage_sha256':sha(R/'Game/assets/models'/C['model_file']),'new_street_floor_area_m2':60.68,'new_street_floor_overlap_m2':0,'new_west_entry_guards':guards,'existing_frame_joints':joints,'D14_source_floor_rim_joints':floor_joints,'new_piers':6,'geometric_load_path':'Six new full-toe piers on retained D14 street support upper room/street crossbeams; four longitudinal joints overlap retained fourth frame by0.1m; eight source-fitted roof posts and44 lower structural objects/30 rails persist; six lower floor rim joins overlap retained D14 slab by0.02m. No D13 floor or engineering load certificate invented.'};(W/'RECEIVING_PLAN.json').write_text(json.dumps(Q,indent=2)+'\n');print('Prepared',len(parts),'frame/floor/guard members;',len(supports),'new exact D14 source pier toes;',len(joints),'old frame joints;60.68m2 missing-only street')
