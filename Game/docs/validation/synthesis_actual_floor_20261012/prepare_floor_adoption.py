import pathlib,json,hashlib,shutil,struct
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
O=pathlib.Path(__file__).parent;R=pathlib.Path('/workspace/astraea-protected-integration-20261012');p=json.loads((O/'source/Game/data/architecture/group8/synthesis_floor_proposal.json').read_text());a=json.loads((O/'ACTUAL_ORIGINAL_FLOOR_COLLIDER.json').read_text());old=unary_union([Polygon(t)for t in a['triangles']]);proposed=unary_union([Polygon(t)for r in p['regions']for t in r['triangles']]);new=proposed.difference(old.buffer(.00005,join_style='mitre'));assert new.is_valid and old.intersection(new).area==0 and proposed.difference(new).area<.005
regions=[]
for idx,poly in enumerate([new]if new.geom_type=='Polygon'else new.geoms):
 tris=[list(t.exterior.coords)[:-1]for t in constrained_delaunay_triangles(poly).geoms];assert abs(sum(Polygon(t).area for t in tris)-poly.area)<1e-7;chunks=[]
 for ix in range(-12,-6):
  for iz in range(-4,4):
   part=poly.intersection(box(ix*8,iz*8,(ix+1)*8,(iz+1)*8))
   if part.area<1e-10:continue
   pieces=[part]if part.geom_type=='Polygon'else[x for x in part.geoms if x.geom_type=='Polygon'];ct=[]
   for piece in pieces:ct.extend(list(t.exterior.coords)[:-1]for t in constrained_delaunay_triangles(piece).geoms)
   chunks.append({'id':f'synthesis_cell_{ix}_{iz}','triangles':ct})
 regions.append({'id':f'G1_synthesis_supporting_floor_{idx}','deck':'D01','floor_y':0.0,'thickness':.24,'rings':[list(poly.exterior.coords)[:-1],*[list(x.coords)[:-1]for x in poly.interiors]],'triangles':tris,'render_chunks':chunks,'structural_area_m2':poly.area,'material_role':'staff_floor','status':'Geometric construction;primary capacity,food-safe segregation and programme quantity unaccepted'})
owned={'schema':1,'source_candidate':'fc08f038a0434b29a42cd622373a345eae65f9f3','source_proposal_sha256':hashlib.sha256((O/'source/Game/data/architecture/group8/synthesis_floor_proposal.json').read_bytes()).hexdigest(),'current_compiled_source_sha256':hashlib.sha256((R/'Game/data/generated/structural_meshes.json').read_bytes()).hexdigest(),'actual_original_collider_triangles':a['triangles'],'actual_original_collider_source_commit':'47eb8359caa5531e04122b6e56292f8c44d4281a','original_floor_unchanged':True,'new_floor_only_boundary_guard_m':.00005,'removed_from_new_proposal_m2':proposed.difference(new).area,'source_proposal_m2':proposed.area,'adopted_missing_only_m2':new.area,'regions':regions,'primary_load_capacity_accepted':False,'new_capacity_or_room_ids':0}
path=R/'Game/data/architecture/GROUP1_SYNTHESIS_SUPPORTING_FLOOR.json';path.write_text(json.dumps(owned,indent=2)+'\n');(O/'FLOOR_ADOPTION_PLAN.json').write_text(json.dumps(owned,indent=2)+'\n');print({'original_proposal_m2':proposed.area,'adopted_m2':new.area,'new_only_removed_m2':proposed.difference(new).area,'chunks':sum(len(x['render_chunks'])for x in regions),'old_positive_overlap':old.intersection(new).area})
# Exact owned source,not the worker's old shared root.
for path in json.loads((O/'OWNED_SOURCE_MATERIALIZATION.json').read_text())['files']:
 if path.endswith('ship_synthesis_plant_after_floor.patch'):continue
 dst=R/path;src=O/'source'/path
 assert not dst.exists()or dst.read_bytes()==src.read_bytes(),path;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
G=O/'asset_import'
for src in(G/'assets/models').iterdir():
 dst=R/'Game/assets/models'/src.name
 if src.name=='G8_SYNTHESIS_PLANT_r002.glb.import':
  # Engine adds remap/dependencies to the retained worker import-parameter fragment.
  shutil.copy2(src,dst)
 elif not dst.exists():shutil.copy2(src,dst)
for src in(G/'.godot/imported').iterdir():
 dst=R/'Game/.godot/imported'/src.name;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
