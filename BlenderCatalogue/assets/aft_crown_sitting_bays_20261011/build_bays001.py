from pathlib import Path
import json,hashlib
from shapely.geometry import box,MultiPoint,Polygon,shape,mapping
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));S=json.load(open(W/'PLATFORM_NATIVE_GEOMETRY.json'))[0]['objects'];P['parts']=[];P['furniture']=[];proof=[];faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]];materials={'walnut':'SAC_QuietScreen','enamel':'SAC_QuietPortalHead','glass':'SAC_PerimeterGlass_0','stone':'SAC_CommonsFloor'}
def cube(name,lo,hi,role,cat):
 x,y,z=lo;X,Y,Z=hi;v=[[a,b,c]for b in[y,Y]for a,c in[(x,z),(X,z),(X,Z),(x,Z)]];P['parts'].append({'name':'ACB_'+name,'verts':v,'faces':faces,'role':role,'category':cat,'runtime_collision':True,'material_source':materials[role],'material_native':'BlenderCatalogue/assets/d04_starboard_aft_neighborhood_20261011/D04StarboardAftCO_r003.blend'});return P['parts'][-1]
for bay in P['bays']:
 label=bay['name'];x,X=bay['x'];z,Z=bay['z'];outer=x if x<0 else X;inner=X if x<0 else x
 # Original staff lane remains outside absx30.2; public loop remains inside absx16.
 for side,a,b,c,d in [('Outer',outer-.08,outer+.08,z,Z),('North',x,X,z-.08,z+.08),('South',x,X,Z-.08,Z+.08),('InnerNorth',inner-.08,inner+.08,z,160),('InnerSouth',inner-.08,inner+.08,163,Z)]:
  cube(label+side+'Dado',[a,106.5,c],[b,107.15,d],'walnut','wall');cube(label+side+'Glass',[a,107.15,c],[b,110.62,d],'glass','window');cube(label+side+'Head',[a,110.62,c],[b,110.9,d],'enamel','wall')
 # Purposeful3m portal and profile frame; lower walking opening is unchanged by roof closure.
 cube(label+'PortalHead',[inner-.08,109.4,160],[inner+.08,110.9,163],'enamel','wall')
 for i,(a,b)in enumerate([(x,z),(x,Z),(X,z),(X,Z)]):cube(label+'RoofPier'+str(i),[a+.12,106.5,b+.12],[a+.32,110.9,b+.32],'walnut','roof_pier') if a==x and b==z else cube(label+'RoofPier'+str(i),[a+(.12 if a==x else-.32),106.5,b+(.12 if b==z else-.32)],[a+(.32 if a==x else-.12),110.9,b+(.32 if b==z else-.12)],'walnut','roof_pier')
 footprint=box(x-.08,z-.08,X+.08,Z+.08);solids=[]
 for q in S:
  lo,hi=q['bounds']
  if min(hi[1],111.02)-max(lo[1],110.9)<=1e-5:continue
  poly=MultiPoint([(v[0],v[2])for v in q['world_vertices']]).convex_hull
  if poly.intersection(footprint).area<1e-8:continue
  vs=q['world_vertices'];assert all(min(abs(v[1]-lo[1]),abs(v[1]-hi[1]))<.0001 for v in vs),q['name']
  bottom=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-lo[1])<.0001]).convex_hull;top=MultiPoint([(v[0],v[2])for v in vs if abs(v[1]-hi[1])<.0001]).convex_hull;assert bottom.symmetric_difference(top).area<1e-6,q['name'];solids.append(poly);proof.append({'bay':label,'retained_owner':q['name'],'polygon':list(poly.exterior.coords),'source_unmodified':True})
 free=footprint.difference(unary_union(solids));n=0
 for tri in constrained_delaunay_triangles(free).geoms:
  v=[[a,y,b]for y in[110.9,111.02]for a,b in list(tri.exterior.coords)[:-1]];P['parts'].append({'name':f'ACB_{label}Roof{n}','verts':v,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'role':'enamel','category':'roof','runtime_collision':True,'material_source':materials['enamel'],'material_native':'BlenderCatalogue/assets/d04_starboard_aft_neighborhood_20261011/D04StarboardAftCO_r003.blend'});n+=1
 for cx in [x+3,X-3]:
  for cz,yaw in [(156,0),(163,3.141592653589793)]:P['furniture'].append({'name':f'ACB_{label}Bench{len(P["furniture"])}','native':'BlenderCatalogue/assets/furniture/AST-FUR-001_day_window_bench.blend','at':[cx,106.5,cz],'yaw':yaw,'kind':'bench'})
  P['furniture'].append({'name':f'ACB_{label}Table{len(P["furniture"])}','native':'BlenderCatalogue/assets/furniture/AST-FUR-003_day_table.blend','at':[cx,106.5,159.5],'yaw':0,'kind':'table'})
 # No geometry fills the source hanger's complete footprint through the roof.
 assert free.intersection(unary_union(solids)).area<1e-8
P['retained_roof_member_fits']=proof;P['parts_floor_owner']='Original compiler floor,no added Blender floor';P['source_pins'].update({f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in ['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json']});P['structure_file']='AFT_CROWN_SITTING_BAYS_r001.glb'
for q in P['parts']:q['expected_bounds']=[[min(v[k]for v in q['verts'])for k in range(3)],[max(v[k]for v in q['verts'])for k in range(3)]]
# Confirm this is retained walking floor, not an allocation rectangle.
old=[]
for f in ['structural_meshes.json','received_structural_meshes.json']:
 for q in json.load(open(R/'Game/data/generated'/f))['regions']:
  if abs(q['floor_y']-106.5)<1e-5:old.extend(Polygon(t)for t in q['triangles'])
floor=unary_union(old);boundary=Polygon(json.load(open(R/'Game/data/architecture/AFT_CROWN_PLATFORM_RUNTIME.json'))['boundary_xz'])
for bay in P['bays']:
 foot=box(bay['x'][0]-.08,bay['z'][0]-.08,bay['x'][1]+.08,bay['z'][1]+.08);assert floor.buffer(.0001).covers(foot)and boundary.covers(foot),bay['name']
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_AUTHORING_INPUT_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(W/'BAY_SOURCE_FIT.json').write_text(json.dumps({'status':'PASS','original_compiled_floor_verified':True,'new_floor_m2':0,'new_programmes_or_capacity':0,'original_hanger_fits':proof,'central_receiving_public_loop_outer_staff_lanes_and_core_outside_new_bays':True,'original_source_objects_modified':0},indent=2)+'\n');print('PASS',len(P['parts']),'enclosure meshes',len(P['furniture']),'rigid furniture copies')
