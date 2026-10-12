"""Full private pit terraces, preserving source originals and declared low routes."""
import json,pathlib,sys,gzip,hashlib
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon,MultiPoint,LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];P=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'BlenderCatalogue/assets/group2_private_vertical_20261011/retained_authoring'))
from premium_frame import PremiumFrame
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for part in g.geoms for p in polys(part)]
rows=[]
for key in ['787','792','794','795','797']:
 path=ROOT/'Game/data/group2_completion/contracts'/f'{key}.json';c=json.loads(path.read_text());frame=PremiumFrame(c['floor_proposal']['boundary'])
 def world(uv):return [(frame.world(u,v)[0],frame.world(u,v)[2])for u,v in uv]
 def rect(u0,u1,v0,v1):return Polygon(world([(u0,v0),(u1,v0),(u1,v1),(u0,v1)]))
 saved=ROOT/'BlenderCatalogue/assets/group2_completion_20261011/retained_evidence'/key/'SAVED_NATIVE_VERTICES.json.gz'
 vertices=json.loads(gzip.decompress(saved.read_bytes()))
 low_routes=unary_union([LineString([(p[0],p[2])for p in r[1]]).buffer(r[2]+.03)for r in c['source_routes_world']])
 # The existing viewing route stays level and enters the original seating court.
 pit_uv=[(10.8,7.8),(16.95,7.8),(16.95,12.6),(11.3,12.6),(11.3,10.9),(10.8,10.9)]
 pit=Polygon(world(pit_uv))
 dining=rect(4.9,10.0,5.1,9.1)
 fore=rect(10.8,17.7,6.3,7.8)
 bridge=rect(9.9,11.0,5.1,6.3)
 rear=rect(9.0,17.7,11.0,14.0)
 outer=rect(16.95,17.7,7.8,12.6)
 # Supreme has a wider outer gallery; retain the same bounded pit package.
 raised=unary_union([dining,fore,bridge,rear,outer]).difference(pit).difference(low_routes)
 allowed=Polygon(c['floor_proposal']['boundary'])
 assert allowed.covers(raised)and raised.intersection(low_routes).area<1e-7
 selected=[]
 for name,pts in vertices.items():
  if name.startswith(('PrivateDiningChair','FittedOvalDining','DiningPedestal','ReadingChair','ReadingBooks',
                      'ReadingCounter','ReadingBayBacking','ReadingShelf','PrivatePlant','PlantPlinth'))and not name.startswith('Upper'):
   selected.append(name)
 # All actual low support contacts must bear wholly on the new source receiver.
 unsupported=[]
 for name in selected:
  pts=vertices[name];low=min(p[1]for p in pts)
  if low>102.021:continue
  feet=MultiPoint([(p[0],p[2])for p in pts if p[1]<102.021]).convex_hull
  if feet.area>1e-8 and feet.difference(raised).area>1e-6:unsupported.append({'name':name,'outside_m2':feet.difference(raised).area})
 regions=[]
 for i,part in enumerate(polys(raised)):
  triangles=[list(t.exterior.coords)[:3]for t in constrained_delaunay_triangles(part).geoms]
  assert abs(sum(Polygon(t).area for t in triangles)-part.area)<1e-6
  regions.append({'id':f'G2P_{key}_TERRACE_{i:02d}','boundary':list(part.exterior.coords)[:-1],
                  'holes':[list(h.coords)[:-1]for h in part.interiors],'triangles':triangles,'base_y':102,'top_y':102.45})
 rows.append({'source_index':int(key),'source_native_sha256':c['native_sha256'],'source_runtime_sha256':c['export_sha256'],
              'contract_sha256':sha(path),'saved_vertices_sha256':sha(saved),'same_private_unit':True,'new_unit':False,
              'pit_boundary_uv':pit_uv,'pit_boundary_xz':world(pit_uv),'pit_floor_y':102,'raised_top_y':102.45,
              'raised_regions':regions,'raised_area_m2':raised.area,'low_source_routes_preserved':True,
              'low_route_overlap_m2':0,'furniture_pose_patch':{'world_delta':[0,.45,0],'exact_mesh_names':selected},
              'unsupported_selected_feet':unsupported,'original_files_modified':False,
              'previous_receiver':{'file':f'Game/assets/group2_private_vertical/CONVERSATION_{key}_r001.glb',
                                   'sha256':sha(ROOT/f'Game/assets/group2_private_vertical/CONVERSATION_{key}_r001.glb'),
                                   'deactivate_only':['ConversationOverlook','Fore_Infill','Fore_Foot','Fore_Handrail',
                                    'Outer_Infill','Outer_Foot','Outer_Handrail','Inner_Infill','Inner_Foot','Inner_Handrail',
                                    'RearClosed_Infill','RearClosed_Foot','RearClosed_Handrail'],
                                   'rear_ramp_and_its_guards_preserved':True},
              '790_excluded':True,'production_adoption':False})
 print(key,'raised_m2',round(raised.area,3),'pose_meshes',len(selected),'unsupported',unsupported[:3],flush=True)
out=ROOT/'Game/data/group2_pit_perimeters/PLAN_r001.json';out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists()
out.write_text(json.dumps({'schema':'astraea.group2_complete_pit_source_plan.v1','parent_checkpoint':'92cef6aa45ee2420a6a5794407f4358d52a27217',
 '790_excluded':True,'new_units':0,'new_decks':0,'shared_root_changed':False,'production_adoption':False,'suites':rows},indent=2)+'\n')
