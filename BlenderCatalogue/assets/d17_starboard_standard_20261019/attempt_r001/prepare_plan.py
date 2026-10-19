from pathlib import Path
import json,hashlib,math,copy
from shapely.geometry import box,Polygon,mapping
from shapely.ops import unary_union,triangulate
R=Path('/workspace/Astraea');W=R/'BlenderCatalogue/assets/d17_starboard_standard_20261019';W.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(R/'BlenderCatalogue/assets/star_atlas_d17_standard_batch_20261011/build_plan.py').read_text();helpers=s[s.index('def finish'):s.index('# Reuse the proven')];parts=[];source_native='BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17ReceivingFirst.blend';exec(helpers)
adoption=json.load(open(R/'Game/data/architecture/D17_STARBOARD_STANDARD_ADOPTION_20261019.json'));donor=json.load(open(R/'Game/data/architecture/STAR_ATLAS_D17_STANDARD823.json'))
regions=json.load(open(R/'Game/data/generated/structural_meshes.json'))['regions'];existing=unary_union([Polygon(t)for r in regions if r['floor_y']==102 for t in r['triangles']]);fore=box(60,-71.6,63.05,-16);aft=unary_union([box(60,14.5,63.05,60.8),box(63.05,14.5,78.5,17.5)]);floor=unary_union([fore,aft]).difference(existing)
for i,g in enumerate(floor.geoms):prism(f'SBS_Floor{i}',g,101.78,102,role='ivory_enamel');prism(f'SBS_Roof{i}',g,106.26,106.5,role='ivory_enamel',category='roof',material='D17R_ReceivedRoof')
feet=[]
for bank,lo,hi,stations in [('Fore',-71.6,-16,[-71.4,-64.2,-57,-49.8,-42.6,-35.8,-32]),('Aft',14.5,60.8,[32.2,39.4,46.6,53.8,60.6])]:
 for j,x in enumerate([60.25,62.75,67.5,71.5,75.79]):cube(f'SBS_{bank}_FloorLong{j}',[x-.12,101.56,lo if x<63 else (-71.6 if bank=='Fore'else 32)],[x+.12,101.8,hi if bank=='Aft'or x<63 else -35.6])
 for j,z in enumerate(stations):
  cube(f'SBS_{bank}_Pier{j}',[85.66,97.5,z-.16],[85.98,101.8,z+.16],category='source_bearing_pier');cube(f'SBS_{bank}_Cross{j}',[60.09,101.56,z-.12],[85.98,101.8,z+.12]);feet.append({'name':f'SBS_{bank}_Pier{j}','at':[85.82,97.5,z],'owner':'D16_NIGHT_GARDEN_MISSING_STREET_'+('0'if bank=='Fore'else'1')})
 for j,x in enumerate([60.25,62.75]):
  cube(f'SBS_{bank}_Upper{j}',[x-.12,105.98,lo],[x+.12,106.26,hi]);cube(f'SBS_{bank}_Lower{j}',[x-.12,104.8,lo],[x+.12,105.04,hi])
  stations2=sorted(set([lo,hi]+[r['adopted_z'][0]for r in adoption['rooms']if (r['adopted_z'][0]<0)==(bank=='Fore')]))
  for k,z in enumerate(stations2):cube(f'SBS_{bank}_Hanger{j}_{k}',[x-.07,101.56,z-.07],[x+.07,106.26,z+.07])
 guard(f'SBS_{bank}_Outer',[60.06,lo+.06],[60.06,hi-.06]);end=lo if bank=='Fore'else hi;guard(f'SBS_{bank}_End',[60.06,end],[62.94,end])
 # Hall inner edge stays protected outside the nine recessed source entries.
 intervals=[(r['entry_origin'][2]-1.75,r['entry_origin'][2]+1.75)for r in adoption['rooms']if (r['entry_origin'][2]<0)==(bank=='Fore')]
 cursor=lo if bank=='Fore'else 17.5
 for a,b in sorted(intervals):
  if a>cursor:guard(f'SBS_{bank}_Inner_{cursor}',[63,cursor],[63,a])
  cursor=b
 if cursor<hi:guard(f'SBS_{bank}_InnerLast',[63,cursor],[63,hi])
guard('SBS_AftNorthReturn',[60.06,14.56],[63.05,14.56])
# Bridge branch below the existing west roof beam; no change to its retained hanger at Z18.
for j,z in enumerate([14.65,17.35]):
 cube(f'SBS_BranchFloorBeam{j}',[60.09,101.56,z-.12],[78.62,101.8,z+.12]);cube(f'SBS_BranchRoofBeam{j}',[60.13,105.98,z-.12],[78.42,106.26,z+.12]);guard(f'SBS_BranchGuard{j}',[63.05,z],[78.49,z])
 for k,x in enumerate([63.1,70.7,78.3]):cube(f'SBS_BranchHanger{j}_{k}',[x-.06,101.56,z-.06],[x+.06,106.26,z+.06])
# Small end seals on newly clipped metal rail faces.
for x in [60.05,62.95]:
 for y in [102.55,103.05]:cube(f'SBS_ForeCap_{x}_{y}',[x-.001,y-.03,-16.03],[x+.001,y+.03,-15.97],category='guard')
fixtures=[]
for r in adoption['rooms']:
 idx=r['allocation']['source_envelope_index'];dz=r['rigid_room_transform']['translation'][2]
 for q0 in donor['fixture_instances']:
  q=copy.deepcopy(q0);q['name']=f'SBS_{idx}_'+q['name'];q['at']=[-q['at'][0],q['at'][1],-q['at'][2]+dz];q['emitter']=[-q['emitter'][0],q['emitter'][1],-q['emitter'][2]+dz];q['yaw']+=math.pi;fixtures.append(q)
 for q0 in donor['parts']:
  if q0['category']!='fixture_mount':continue
  q=copy.deepcopy(q0);q['name']=f'SBS_{idx}_'+q['name'];q['verts']=[[-x,y,-z+dz]for x,y,z in q['verts']];finish(q)
pins=dict(adoption['source_pins']);pins['Game/assets/models/'+adoption['source_room_model']]=adoption['source_room_sha256']
for f in [source_native,'BlenderCatalogue/assets/star_atlas_d17_receiving_first_20261010/StarAtlasD17Standard823Recess.blend','Game/assets/models/AST-RES-006.glb','Game/assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.glb','Game/data/generated/structural_meshes.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json']:pins[f]=sha(R/f)
p={'schema':'astraea.d17.starboard.receiving.candidate.v1','base_commit':adoption['base_commit'],'active':False,'parts':parts,'fixture_instances':fixtures,'furniture':[],'source_pins':pins,'protected_native_exports':pins,'structure_file':'D17_STARBOARD_STANDARD_FRAME_r001.glb','rooms':adoption['rooms'],'source_room_model':adoption['source_room_model'],'source_room_sha256':adoption['source_room_sha256'],'floor_geometry':mapping(floor),'new_floor_area_m2':floor.area,'bearings':feet,'walls':json.load(open('/workspace/d17-starboard-integration/RUNTIME_PREIMAGES.json')),'revision_note':'Candidate only. Fore existing adjunct guard branch; aft Z14.5..17.5 branch preserves structural hanger at Z18. Physical clashes, exact patch/fixture geometry and original-controller routes must pass before integration.','construction_accepted':False,'new_units':0,'new_rest_places':0}
(W/'PLAN.json').write_text(json.dumps(p,indent=2)+'\n');print(len(parts),floor.area,len(fixtures))
