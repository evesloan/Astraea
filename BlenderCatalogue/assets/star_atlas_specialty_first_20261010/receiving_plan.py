from pathlib import Path
import json,hashlib,copy
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parts=[]
def cube(name,lo,hi,role='champagne_metal',cat='receiving'):
 v=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];parts.append({'name':name,'verts':v,'faces':[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]],'role':role,'category':cat,'runtime_collision':True})
regions=[]
for path in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json']:regions+=json.loads((R/path).read_text())['regions']
old=unary_union([Polygon(t)for r in regions if float(r['floor_y'])==93 for t in r['triangles']]);desired=[]
for side,lo,hi in [('North',-53,-14),('South',14,53)]:
 poly=box(-86.05,lo,-81.95,hi);assert poly.intersection(old).area<.000001;desired.append(poly)
 cube('SA_D15_'+side+'NewStreetFloor',[-86.05,92.76,lo],[-81.95,93,hi],'warm_stone','floor')
 for x in [-85.8,-82.2]:cube(f'SA_D15_{side}LongitudinalReceiving_{x}',[x-.10,92.6,lo],[x+.10,92.76,hi])
 # Actual source cover edge contact, not another cover or floor cut.
 end=-14 if side=='North'else 14
 cube('SA_D15_'+side+'CoverEdgeTie',[-86.05,92.76,end-.06 if side=='North'else end],[-81.95,93,end if side=='North'else end+.06],'champagne_metal','cover_edge_tie')
 for z in [lo,hi]:
  if abs(z)==14:continue
  cube(f'SA_D15_{side}TerminalGuard_{z}',[-86.05,93,z-.035],[-81.95,94.1,z+.035],'champagne_metal','guard')
 cube('SA_D15_'+side+'WestGuard',[-86.05,93,lo],[-85.98,94.1,hi],'champagne_metal','guard')
 # Source-defined blank east edge to the first habitat; two reserved room entries stay free.
 if side=='North':intervals=[(-38.4,-14),(-45.8,-45.6)]
 else:intervals=[(14,38.4),(45.6,45.8)]
 for k,(a,b)in enumerate(intervals):cube(f'SA_D15_{side}EastGuard_{k}',[-82.02,93,a],[-81.95,94.1,b],'champagne_metal','guard')
 for z in [-49.4,-42]if side=='North'else[42,49.4]:
  cube(f'SA_D15_{side}RoomReceivingCrossbeam_{z}',[-85.9,92.6,z-.1],[-75.6,92.76,z+.1],'champagne_metal','receiving')
# Compact two-mesh commons derivative; original full native remains retained.
source=json.loads((R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/PLAN.json').read_text());patches=[]
for name in ['SA_D15_NorthWall_0','SA_D15_SouthWall_0']:
 oldpart=next(p for p in source['parts']if p['name']==name);lo=[min(v[i]for v in oldpart['verts'])for i in range(3)];hi=[max(v[i]for v in oldpart['verts'])for i in range(3)];start=len(parts)
 for label,a,b in [('West',lo,[-86.05,hi[1],hi[2]]),('East',[-81.95,lo[1],lo[2]],hi),('PortalHeader',[-86.05,96.0,lo[2]],[-81.95,hi[1],hi[2]])]:cube(name+'_'+label,a,b,oldpart['role'],'exact_commons_portal_derivative')
 replacements=parts[start:];parts=parts[:start];patches.append({'name':name,'original_part':oldpart,'replacement_parts':replacements,'portal_bounds':[-86.05,93,-81.95,96],'original_native_objects_unchanged_other_than_two':512})
T={'schema':'astraea.star_atlas_specialty_receiving.v1','parts':parts,'model_file':'StarAtlasSpecialtyFirstReceiving.glb','commons_patch_file':'StarAtlasSpecialtyFirstCommonsPatch.glb','commons_patches':patches,'new_street_area_m2':sum(p.area for p in desired),'new_room_floor_area_m2':sum(12.9*7.2 for r in P['rooms']),'source_cover_preserved':'D15_star_atlas_protected_cover_0 geometry and ownership unchanged; two named vertical wall mouths only','old_floor_overlap_m2':0,'geometry_contacts_vs_capacity':'Exact lower roof post faces/cover edge joins, cantilevered floor/bridge receiver proposal. No certified roof load or primary structural capacity.','path_terminal_holds':'New branches stop with guards atZ+/-53; farther specialty streets remain unfinished.'}
(W/'RECEIVING_PLAN.json').write_text(json.dumps(T,indent=2)+'\n');print('Prepared missing-only319.8m2 streets; two exact named wall apertures; cover preserved')
