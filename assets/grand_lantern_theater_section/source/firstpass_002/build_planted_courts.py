"""Actual bounded planted-court source mesh/instance package; no engine/shared writes."""
from pathlib import Path
import json,math,copy,numpy as np,ast
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');objects=[]
# Reuse pure closed mesh constructors, not the source generator's side effects.
t=ast.parse((R/'build_luminous_fixture_geometry.py').read_text());defs=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in ['emit','rect','prism']];exec(compile(ast.Module(body=defs,type_ignores=[]),'<reviewed_geometry_helpers>','exec'))
base=json.loads((R.parent/'FIRST_PASS_ADDITIONS_PLAN.json').read_text());M=json.loads((R.parent/'RETAINED_MODULE_MEASUREMENTS.json').read_text());M.update(json.loads((R/'RETAINED_FOCAL_ASSET_BOUNDS.json').read_text()));S=json.loads((P/'contracts/surface_manifest.json').read_text());old=json.loads((P/'source/geometry.json').read_text())['objects'];routes=json.loads((P/'contracts/route_reservations.json').read_text())['routes']
instances=[];courts=[];new_ground=[]
for deck,floor in [('D11',69.5),('D12',78),('D13',84)]:
 for code,x,z,purpose in [('A',-69.5,-143,'Programme/usher arrival garden'),('B',-89.5,-142,'Conversation and intermission planted court'),('C',-106.5,-123.4,'Quiet rear arrival garden')]:
  pre=f'FP2_{deck}_GROVE_{code}';outer=rect(4.8,1.8,.16);inner=rect(4.5,1.5,.13);n=8
  prism(pre+'_grounded_plinth',rect(4.66,1.66,.13),floor,floor+.15,'warm_stone','fixed_furnishing',origin=(x,z),contact='Full support on the exact owned walking-floor candidate/surface; no structural load certification')
  verts=[[x+a,h,z+b]for poly,h in [(outer,floor+.12),(inner,floor+.12),(outer,floor+.72),(inner,floor+.72)]for a,b in poly];faces=[]
  for i in range(n):
   j=(i+1)%n;faces.extend([[i,n+i,n+j,j],[2*n+i,2*n+j,3*n+j,3*n+i],[i,j,2*n+j,2*n+i],[n+i,3*n+i,3*n+j,n+j]])
  emit(pre+'_profiled_ivory_basin',verts,faces,'ivory_enamel','fixed_furnishing',provenance='Bounded theater derivative of retained planted-seat basin/profile vocabulary; no existing catalogue source is scaled or edited')
  prism(pre+'_real_soil_volume',rect(4.5,1.5,.13),floor+.15,floor+.65,'botanical_soil','plant_root_receiver',origin=(x,z),soil_depth_m=.5)
  # A narrow actual bronze reveal over the already supported exterior wall.
  ot=rect(4.812,1.812,.16);it=rect(4.772,1.772,.155);verts=[[x+a,h,z+b]for poly,h in[(ot,floor+.665),(it,floor+.665),(ot,floor+.700),(it,floor+.700)]for a,b in poly];emit(pre+'_bronze_reveal',verts,faces,'champagne_metal','fixed_furnishing')
  roots=[]
  layouts=[('AST-BOT-007',u,-.05,math.radians(5 if j==0 else 185))for j,u in enumerate([-1.1,1.1])]
  layouts += [('AST-BOT-002',u,.40,math.radians(13 if j%2==0 else 193))for j,u in enumerate([-1.8,-.6,.6,1.8])]
  layouts += [('AST-BOT-009',u,-.42,math.radians(185 if j%2 else 5))for j,u in enumerate([-1.55,0,1.55])]
  layouts += [('AST-BOT-003',u,.53,math.radians(j*55))for j,u in enumerate([-1.2,0,1.2])]
  for index,(asset,u,v,yaw)in enumerate(layouts):
   row={'id':pre+'_P'+str(index).zfill(2),'asset':asset,'position_world':[x+u,floor+.647,z+v],'yaw_radians':yaw,'scale':[1,1,1],'root_receiver':pre+'_real_soil_volume','root_embed_m':.003,'purpose':'Layered large fan crown / broad-leaf lower bank / flower colour / low rosette; full retained sculpted meshes and textures'};instances.append(row);roots.append(row['id'])
  courts.append({'id':pre,'deck':deck,'floor_y':floor,'centre_world':[x,floor,z],'physical_basin_size':[4.8,.72,1.8],'soil_y':floor+.65,'purpose':purpose,'plant_instances':roots,'front_approach':'Court is a planted focal feature, not an added seat; existing separate seats face it. No people placed under foliage.'})
  new_ground.append({'id':pre,'asset':'THEATER_DERIVED_PLANTER','position_world':[x,floor,z],'yaw_radians':0,'conservative_footprint_xz':[[x-2.4,z-.9],[x+2.4,z-.9],[x+2.4,z+.9],[x-2.4,z+.9]],'bounds_y':[floor,floor+.72]})
# Move only new first-pass furniture instances. All original2200 audience chairs stay exact.
changes={
'D11_programme_0':(-67,-129.7,0),'D13_programme_0':(-68,-130,0),
'D11_waiting_bench_0':(-102.5,-130.5,0),'D11_waiting_table_0':(-102.5,-128.9,0),'D11_waiting_bench_1':(-107,-130.5,0),'D11_waiting_table_1':(-107,-128.9,0),
'D11_waiting_bench_2':(-91,-136.8,math.pi),'D11_waiting_table_2':(-91,-138.4,0),'D11_waiting_bench_3':(-86.5,-136.8,math.pi),'D11_waiting_table_3':(-86.5,-138.4,0),
'D12_waiting_bench_0':(-107,-130.5,0),'D12_waiting_table_0':(-107,-128.9,0),'D12_waiting_bench_1':(-91,-136.8,math.pi),'D12_waiting_table_1':(-91,-138.4,0),
'D12_waiting_chair_2':(-71,-136.8,math.pi),'D12_waiting_chair_3':(-69,-136.8,math.pi),'D12_waiting_table_3':(-70,-138.1,0),
'D13_waiting_bench_0':(-107,-130.5,0),'D13_waiting_table_0':(-107,-128.9,0),'D13_waiting_bench_1':(-87,-136,math.pi),'D13_waiting_table_1':(-87,-137.6,0),'D13_programme_1':(-112,-126,0),
'D13_waiting_chair_0':(-92,-136.8,math.pi),'D13_waiting_chair_1':(-90,-136.8,math.pi),'D13_waiting_table_2':(-91,-138.1,0),
'D11_backstage_08':(-67.5,-261.4,-math.pi/2),'D11_backstage_09':(-70.1,-261.4,math.pi/2)}
plan=copy.deepcopy(base);moves=[]
for row in plan['ground_modules']:
 if row['id']in changes:
  before=copy.deepcopy(row);x,z,yaw=changes[row['id']];row['position_world']=[x,row['position_world'][1],z];row['yaw_radians']=yaw;moves.append({'id':row['id'],'before_position':before['position_world'],'before_yaw':before['yaw_radians'],'position_world':row['position_world'],'yaw_radians':yaw})
 lo,hi=[M[row['asset']]['bounds_gltf'][k]for k in ['min','max']];x,y,z=row['position_world'];a=row['yaw_radians'];c,s=math.cos(a),math.sin(a);row['conservative_footprint_xz']=[[x+u*c+v*s,z-u*s+v*c]for u,v in[(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])]];row['bounds_y']=[y+lo[1],y+hi[1]]
plan['ground_modules']+=new_ground
(R/'FIRST_PASS_ADDITIONS_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
out={'status':'Authored source geometry/placement correction; source build and actual visual review pending','base_source_sha256':'a3f1d01b0927ddd873986b2d1f2dbb44f234bced2b034c2cff42c2c0bfd8d0ce','objects':objects,'courts':courts,'plant_instances':instances,'furniture_pose_changes':moves,'retained_asset_measurements':{k:M[k]for k in {r['asset']for r in instances}},'small_table_contents_follow_moved_tables':True,'protected_original_audience_chairs':2200,'seat_focus':'Waiting benches face planted courts. Paired reading chairs retain conversational focus; repositioned pairs face programme garden. Rehearsal chairs face actual stage, dressing chairs actual work surfaces; rotated backstage bench faces reoriented illuminated cue/notes stand.'}
(R/'PLANTED_COURT_GEOMETRY_002.json').write_text(json.dumps(out,indent=2)+'\n');print('Authored basins',len(courts),'closed meshes',len(objects),'retained plant instances',len(instances),'furniture pose changes',len(moves))
