"""Five retained thermal recovery benches: supported shade, screen and tasks.
No seat/room/floor/capacity addition or original geometry change. Existing source
fittings receive optional scoped runtime bindings; the shared owner reconciles
those bindings on its current root. Day-rest/species/acoustic/service gameplay
and primary loads remain separate.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];SUP=P.parent/'thermal_support';ENTRY=P.parent/'thermal_targets'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
code=(ENTRY/'author_entries.py').read_text();exec(code[code.index('def digest'):code.index('provenance=')])
def bounds(o):
 vs=[o.matrix_world@v.co for v in o.data.vertices];a=[[min(v[k] for v in vs),max(v[k] for v in vs)] for k in range(3)];return [a[0],a[2],[-a[1][1],-a[1][0]]]
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
def in_triangle(p,t):
 x,z=p;a=[(b[0]-q[0])*(z-q[1])-(b[1]-q[1])*(x-q[0]) for q,b in zip(t,t[1:]+t[:1])];return min(a)>=-1e-7 or max(a)<=1e-7
floors=json.loads((R/'Game/data/generated/received_structural_meshes.json').read_text())['regions'];rooms=[]
for previous in json.loads((SUP/'THERMAL_SUPPORT_CONTRACT.json').read_text())['rooms']:
 key=previous['programme_key'];i=key[-2:];source=R/previous['native'];assert sha(source)==previous['native_sha256'];destination=P/f'ThermalRecovery_{i}_r003.blend';assert not destination.exists()
 bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene;originals={o.name:digest(o) for o in S.objects if o.type=='MESH'};packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file};NEW=[]
 M={k:bpy.data.materials[v] for k,v in {'stone':'ASTRAEA_warm_stone','ivory':'ASTRAEA_ivory_enamel','metal':'ASTRAEA_champagne_metal','teal':'ASTRAEA_teal_weave','grip':'ASTRAEA_dark_rubber','lens':'AQD_opal'}.items()}
 def finish(o,n,mat='metal',role='recovery_architecture'):
  o.name=('G6_REST_'+i+'__'+n).replace('.', '_');o['group6_role']=role;o['programme_key']=key;o['construction_only']=True;o.data.materials.clear();o.data.materials.append(M[mat]);o.data.update();uv=o.data.uv_layers.new(name='UV0')
  for f in o.data.polygons:
   axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(f.normal[a]))]
   for li in f.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.5,v[axes[1]]*.5)
  NEW.append(o);return o
 def mesh(n,vs,faces,mat='ivory',role='recovery_architecture'):
  m=bpy.data.meshes.new(n);m.from_pydata([xyz(v) for v in vs],[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o=bpy.data.objects.new(n,m);S.collection.objects.link(o);return finish(o,n,mat,role)
 def box(n,p,d,mat='ivory',role='recovery_architecture',bevel=.018):
  bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=o.modifiers.new('Finished source corners','BEVEL');m.width=min(bevel,min(d)*.2);m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);return finish(o,n,mat,role)
 def rod(n,a,b,r=.026,mat='metal'):
  a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat)
 bays=[];fittings=[]
 centers=[-452,-432,-412] if i=='02' else [-236,-196]
 for j,cz in enumerate(centers):
  n='bay_'+str(j)+'_';length=5 if i=='02' else 7;front=45.7 if i=='02' else -22.15;rear=48.25 if i=='02' else -18.85;fy=46.65;ry=46.65 if i=='02' else 46.85;ends=[cz-length/2-.42,cz+length/2+.42];bench=key+'__'+('dry_recovery' if i=='02' else 'recovery')+str(j)+'_pad';assert bench in originals
  for side,x,y in [('front',front,fy),('rear',rear,ry)]:
   for k,z in enumerate(ends):
    box(n+'foot_'+side+'_'+str(k),(x,44.025,z),(.22,.05,.22),'stone');box(n+'post_'+side+'_'+str(k),(x,(44.05+y-.11)/2,z),(.095,y-.11-44.05,.095),'metal')
   box(n+'long_beam_'+side,(x,y-.055,cz),(.20,.11,length+1.06),'metal')
  for k,z in enumerate(ends):
   # End beam connects both post crowns, with a folded rear rise in Mineral.
   y0,y1=fy-.11,ry-.11;vs=[(x,y+h,z+dz) for dz in [-.08,.08] for x,y in [(front,y0),(rear,y1)] for h in [0,.11]];mesh(n+'end_beam_'+str(k),vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],'metal')
  count=18 if i=='02' else 25
  for k in range(count):
   z=ends[0]+.16+(ends[1]-ends[0]-.32)*k/(count-1);profile=[]
   for a in range(9):
    t=a/8;x=front+(rear-front)*t;y=(fy+.40*math.sin(math.pi*t)) if i=='02' else (fy+(47.05-fy)*t*2 if t<=.5 else 47.05+(ry-47.05)*(t-.5)*2);profile.append((x,y))
   vs=[(x,y+h,z+dz) for dz in [-.055,.055] for x,y in profile for h in [0,.065]];faces=[]
   for a in range(8):
    b=2*a;faces.extend([(b,b+2,b+3,b+1),(18+b,19+b,21+b,20+b),(b,18+b,20+b,b+2),(b+1,b+3,21+b,19+b)])
   faces.extend([(0,1,19,18),(16,34,35,17)]);mesh(n+'canopy_fin_'+str(k),vs,faces,'ivory')
  # Open back screen and low side returns give quieter rest without sealing it.
  screen_x=rear-.16
  for y in [44.35,45.18,46.29]:box(n+'screen_rail_'+str(y),(screen_x,y,cz),(.08,.07,length+.55),'metal')
  for k in range(15 if i=='02' else 21):
   z=cz-length/2+(length*k/(14 if i=='02' else 20));box(n+'screen_leaf_'+str(k),(screen_x,45.28,z),(.045,1.92,.075),'teal')
  for k,z in enumerate(ends):
   box(n+'side_sill_'+str(k),((front+rear)/2,44.82,z),(abs(rear-front)-.12,.09,.08),'stone')
  # Small fixed vessel rests; no duplicate benches or clean/used service niches.
  table_x=46.0 if i=='02' else -21.10
  for k,dz in enumerate([-length*.31,length*.31]):
   z=cz+dz;box(n+'table_foot_'+str(k),(table_x,44.025,z),(.36,.05,.36),'grip');rod(n+'table_pedestal_'+str(k),(table_x,44.05,z),(table_x,44.78,z),.055);box(n+'table_cap_'+str(k),(table_x,44.82,z),(.46,.08,.44),'stone');box(n+'vessel_rest_'+str(k),(table_x,44.871,z),(.23,.022,.23),'ivory',role='visual_vessel_rest')
  lamp_x=46.9 if i=='02' else -20.15;lamp_z=[cz-1.15,cz+1.15] if i=='02' else [cz-2.20,cz,cz+2.20]
  for k,z in enumerate(lamp_z):
   # A real cross-tie under the fins supports each dropped task fitting.
   mount_y=fy-.11+(ry-fy)*(lamp_x-front)/(rear-front)
   rod(n+'task_cross_tie_'+str(k),(front,fy-.11,z),(rear,ry-.11,z),.024);rod(n+'task_drop_'+str(k),(lamp_x,mount_y,z),(lamp_x,46.41,z),.022);box(n+'task_hood_'+str(k),(lamp_x,46.39,z),(.30,.085,.27),'metal');box(n+'task_lens_'+str(k),(lamp_x,46.335,z),(.22,.025,.19),'lens',role='fixture_lens')
   fittings.append({'id':'aquatic_thermal_'+i+'_recovery_'+str(j)+'_task_'+str(k)+'_001','source_xyz':[lamp_x,46.295,z],'target_xyz':[47 if i=='02' else -20,44.60,z],'receiver_mesh':bench,'range_m':4.5,'half_cone_degrees':65,'energy':.65 if i=='02' else .55,'color_rgb':[1,.94,.82] if i=='02' else [.92,.98,1],'mount':'new canopy cross-tie / drop / hood'})
  bays.append({'id':'aquatic_thermal_'+i+'_recovery_'+str(j)+'_001','existing_bench_mesh':bench,'existing_bench_bounds_xyz':bounds(bpy.data.objects[bench]),'front_stance_xyz':[45.3 if i=='02' else -22.5,44,cz],'promenade_xyz':[45 if i=='02' else -25,44,cz],'existing_seat_geometry_and_capacity_unchanged':True,'canopy_form':'curved open fins' if i=='02' else 'folded mineral fins','dayrest_occupation_species_acoustic_service_accepted':False})
 # Existing physical room lenses were unbound in the retained receiving builder.
 # Add optional lights only; the shared owner reconciles current-root ownership.
 legacy=[];original_solids=[o for o in S.objects if o.type=='MESH' and o.name in originals and not o.hide_render and not any(t in o.name for t in ['static_water_surface','mineral_court_water','quiet_court_water']) and o.get('group6_role') not in ['fixture_lens','visual_grip_no_contact','visual_control_interface','visual_soft_furnishing']];bvhs={o.name:tree(o) for o in original_solids}
 for o in S.objects:
  if o.type!='MESH' or not (o.name.startswith(key+'__') and 'lens' in o.name):continue
  b=bounds(o);source_xyz=[sum(b[0])/2,b[1][0]-.025,sum(b[2])/2];start=xyz(source_xyz);hits=[]
  for name,bvh in bvhs.items():
   h=bvh.ray_cast(start,Vector((0,0,-1)),4)
   if h[0] is not None:hits.append((h[3],name,[h[0].x,h[0].z+.04,-h[0].y]))
  floor_ok=any(in_triangle([source_xyz[0],source_xyz[2]],t) for r in floors if r['id'].startswith(key+'_') for t in r['triangles'])
  if hits:_,receiver,target=min(hits)
  else:
   target=[source_xyz[0],44.04,source_xyz[2]]
   if not floor_ok:
    center=[30,-432] if i=='02' else [-30,-216];direction=Vector((center[0]-source_xyz[0],center[1]-source_xyz[2])).normalized()
    for step in range(1,61):
     trial=[source_xyz[0]+direction.x*step*.10,source_xyz[2]+direction.y*step*.10]
     ok=any(in_triangle(trial,t) for r in floors if r['id'].startswith(key+'_') for t in r['triangles'])
     if ok:
      trial=[trial[0]+direction.x*.6,trial[1]+direction.y*.6];assert any(in_triangle(trial,t) for r in floors if r['id'].startswith(key+'_') for t in r['triangles']);target=[trial[0],44.04,trial[1]];break
    else:raise AssertionError((o.name,'no supported inward receiver'))
   receiver='original_compiler_floor'
  legacy.append({'id':'aquatic_thermal_'+i+'_existing_'+o.name.split('__')[1]+'_source_001','source_mesh':o.name,'source_mesh_bounds_xyz':b,'source_xyz':source_xyz,'target_xyz':target,'receiver_mesh':receiver,'range_m':8.0,'half_cone_degrees':65,'energy':.95,'color_rgb':[1,.96,.88],'existing_fitting_geometry_unchanged':True,'binding_optional_for_integration_owner':True})
 assert len(legacy)==7
 assert all(digest(bpy.data.objects[n])==h for n,h in originals.items())
 for im in bpy.data.images:
  if im.packed_file:im.use_fake_user=True
 bpy.ops.wm.save_as_mainfile(filepath=str(destination));bpy.ops.object.select_all(action='DESELECT')
 for o in NEW:o.select_set(True)
 export=P/f'Group6ThermalRecovery_{i}_r003.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
 spec={'programme_key':key,'source_context':str(source.relative_to(R)),'source_context_sha256':sha(source),'original_context_meshes':originals,'original_packed_images':packed,'current_room_runtime':previous['current_room_runtime'],'current_room_runtime_sha256':previous['current_room_runtime_sha256'],'required_support_export':previous['runtime_addition'],'required_support_export_sha256':previous['export_sha256'],'native':str(destination.relative_to(R)),'native_sha256':sha(destination),'export':str(export.relative_to(R)),'export_sha256':sha(export),'runtime_addition':'Game/assets/models/'+export.name,'new_meshes':{o.name:digest(o) for o in NEW},'new_mesh_roles':{o.name:o['group6_role'] for o in NEW},'bays':bays,'new_task_fittings':fittings,'optional_existing_fixture_bindings':legacy,'floor_input_sha256':sha(R/'Game/data/generated/received_structural_meshes.json'),'new_seats_rooms_floor_owners_or_capacity':0,'new_thermal_water_or_player_controller':False}
 (P/f'CONTRACT_{i}.json').write_text(json.dumps(spec,indent=2)+'\n');rooms.append(spec)
(P/'THERMAL_RECOVERY_CONTRACT.json').write_text(json.dumps({'status':'inactive scoped thermal recovery fit-out','rooms':rooms},indent=2)+'\n');print('THERMAL RECOVERY SOURCE',[(r['programme_key'],len(r['new_meshes']),len(r['new_task_fittings']),len(r['optional_existing_fixture_bindings'])) for r in rooms])
