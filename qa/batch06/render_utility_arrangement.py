"""Source-matched utility component assembly, with no fluid/room simulation."""
from pathlib import Path
import bpy,math,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06/arrangement';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'standards'));from qa_frame import assert_full_frame,frame_report
bpy.ops.wm.read_factory_settings(use_empty=True)
instances={};records=[];component=[]
def bring(rel,name,pos):
 p=ROOT/rel;before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));obs=list(set(bpy.data.objects)-before)
 root=bpy.data.objects.new('QA instance '+name,None);bpy.context.collection.objects.link(root)
 for ob in obs:
  if ob.parent is None:ob.parent=root
 root.location=pos;bpy.context.view_layer.update();meshes=[o for o in obs if o.type=='MESH'];component.extend(meshes);instances[name]={'root':root,'objects':obs,'meshes':meshes,'position':Vector(pos)}
 pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 records.append({'name':name,'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_position_m':pos,'glb_yup_position_m':[pos[0],pos[2],-pos[1]],'min_m':[min(v[k] for v in pts) for k in range(3)],'max_m':[max(v[k] for v in pts) for k in range(3)]})

def bvh(meshes):
 v=[];t=[]
 for ob in meshes:
  me=ob.data;me.calc_loop_triangles()
  for tri in me.loop_triangles:
   base=len(v);v.extend(ob.matrix_world@me.vertices[i].co for i in tri.vertices);t.append((base,base+1,base+2))
 assert t
 return BVHTree.FromPolygons(v,t,all_triangles=True),len(t)

machine=json.load(open(ROOT/'assets/utility_machines/connection_api.json'))['assets'];pipe=json.load(open(ROOT/'assets/utility_pipework/port_and_seam_api.json'))['ports_by_asset']
valve_len=next(p for p in pipe['AST-ENG-006'] if p['name']=='OUTLET')['position_blender_source_m'][0]
pump_pos=(-1.70,0,0);straight_pos=(-.85,0,.60);valve_pos=(-.05,0,.60);filter_pos=(-.05+valve_len+.64,0,0);elbow_pos=(filter_pos[0]+.64,0,.60);console_pos=(3.20,1.20,1.45)
for rel,name,pos in [('assets/utility_machines/exports/AST-ENG-001.glb','pump',pump_pos),('assets/utility_machines/exports/AST-ENG-002.glb','filter',filter_pos),('assets/utility_pipework/exports/AST-ENG-004.glb','straight',straight_pos),('assets/utility_pipework/exports/AST-ENG-006.glb','valve',valve_pos),('assets/utility_pipework/exports/AST-ENG-005.glb','elbow',elbow_pos),('assets/utility_console/AST-ENG-003.glb','console',console_pos)]:bring(rel,name,pos)
for name,data in instances.items():data['bvh'],data['triangles']=bvh(data['meshes'])
ports={};port_checks=[]
for name,recs in [('pump',machine['AST-ENG-001']['ports']),('filter',machine['AST-ENG-002']['ports']),('straight',pipe['AST-ENG-004']),('valve',pipe['AST-ENG-006']),('elbow',pipe['AST-ENG-005'])]:
 data=instances[name]
 for rec in recs:
  expected=Vector(rec['position_blender_source_m'])+data['position'];normal=Vector(rec['normal_blender_source']);candidates=[o for o in data['objects'] if o.type=='EMPTY' and 'normal_blender_source' in o]
  assert candidates,(name,'no actual port marker nodes')
  marker=min(candidates,key=lambda o:(o.matrix_world.translation-expected).length);error=(marker.matrix_world.translation-expected).length;assert error<1e-5
  actual=marker.matrix_world.translation.copy();n=Vector(marker['normal_blender_source']).normalized();assert (n-normal).length<1e-6
  port_checks.append({'asset':name,'port':rec['name'],'actual_imported_node':marker.name,'node_world_m':list(actual),'expected_world_m':list(expected),'position_error_m':error,'normal_m':list(n)})
  ports[(name,rec['name'])]={'point':actual,'normal':n,'record':rec,'data':data}
seams=[]
for left,right in [(('pump','pump_right'),('straight','INLET')),(('straight','OUTLET'),('valve','INLET')),(('valve','OUTLET'),('filter','filter_left')),(('filter','filter_right'),('elbow','INLET'))]:
 a,c=ports[left],ports[right];dist=(a['point']-c['point']).length;dot=a['normal'].dot(c['normal']);assert dist<1e-5 and abs(dot+1)<1e-6
 ba=[Vector(p)+a['data']['position'] for p in a['record']['bolt_centres_blender_source_m']];bb=[Vector(p)+c['data']['position'] for p in c['record']['bolt_centres_blender_source_m']];phase=max(min((p-q).length for q in bb) for p in ba);assert phase<1e-5
 samples=[]
 for side in (a,c):
  n=side['normal'];u=Vector(side['record']['radial_zero_blender_source']);v=n.cross(u)
  for radius in (.10,.145):
   for i in range(12):
    p=side['point']+radius*(u*math.cos(i*math.tau/12)+v*math.sin(i*math.tau/12));hit=side['data']['bvh'].ray_cast(p+n*.012,-n,.025)[0];assert hit is not None and abs((hit-p).dot(n))<1e-5
    samples.append({'asset':left[0] if side is a else right[0],'face_error_m':abs((hit-p).dot(n))})
  # Clear centre through the declared neck; only geometric obstruction is checked.
  hit=side['data']['bvh'].ray_cast(side['point']+n*.01,-n,.105)[0];assert hit is None,(left,right,'blocked shared bore')
 seams.append({'a':left,'b':right,'position_gap_m':dist,'normal_dot':dot,'bolt_phase_error_m':phase,'actual_face_samples':samples,'neck_centre_clear':True})
# Source-owned maintenance prisms remain clear of OTHER components.
clearances=[]
for owner,ident in [('pump','AST-ENG-001'),('filter','AST-ENG-002')]:
 for box in machine[ident]['maintenance_clearances']:
  lo=Vector(box['min_blender_source_m'])+instances[owner]['position'];hi=Vector(box['max_blender_source_m'])+instances[owner]['position'];checks=[]
  for name,data in instances.items():
   if name==owner:continue
   for ob in data['meshes']:
    pts=[ob.matrix_world@Vector(c) for c in ob.bound_box];a=[min(v[k] for v in pts) for k in range(3)];b=[max(v[k] for v in pts) for k in range(3)];ov=[min(b[k],hi[k])-max(a[k],lo[k]) for k in range(3)];assert any(x<=0 for x in ov),(owner,box['name'],name,ob.name,ov);checks.append(ob.name)
  clearances.append({'owner':owner,'name':box['name'],'min_world_m':list(lo),'max_world_m':list(hi),'other_meshes_separate':len(checks),'scope':'Conservative other-component bounds only; own moving-part clearances separately checked by source review'})
console=json.load(open(ROOT/'assets/utility_console/AST-ENG-003.manifest.json'));mounts=[]
for m in console['mounts']:
 p=Vector(m['point_blender_source_m'])+Vector(console_pos);assert abs(p.y-console_pos[1])<1e-6;mounts.append({'name':m['name'],'world_m':list(p),'qa_wall_plane_y_m':console_pos[1]})
floors=[]
for name in ('pump','filter'):
 row=next(r for r in records if r['name']==name);assert abs(row['min_m'][2])<1e-6;floors.append({'name':name,'lowest_m':row['min_m'][2],'floor_datum_m':0})

def material(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.95;return m
floor=material('QA neutral floor',(.18,.205,.215));wall=material('QA console backing only',(.27,.285,.29))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.data.materials.append(floor);bpy.context.object.name='QA neutral floor only'
bpy.ops.mesh.primitive_cube_add(size=1,location=(console_pos[0],console_pos[1]+.06,1.0));ob=bpy.context.object;ob.name='QA console receiving wall only';ob.dimensions=(.95,.12,2.0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(wall)
# Deliberately empty approach. No enclosing room, service network or simulation.
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('QA neutral world');sc.world.color=(.18,.18,.18);sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.threads_mode='FIXED';sc.render.threads=4;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
for name,pos,power,size,col in [('key',(-4,-4,6),1100,5,(.98,.99,1)),('fill',(5,-2,4),750,4,(.94,.98,1)),('back',(0,4,5),900,5,(1,1,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.sensor_width=36;d.clip_start=.04;d.clip_end=200
views=[('overview_1280',(6.8,-8.6,4.1),(.2,.15,.85),1280,720,36,True),('standing_640',(6.2,-8,1.65),(.2,.15,.83),640,360,33,True),('operator_controls_640',(3.20,.20,1.65),(3.20,.95,1.44),640,360,31,False)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];frames=[]
for name,pos,target,w,h,lens,full in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.resolution_percentage=100;fr=assert_full_frame(sc,cam,component,.025) if full else frame_report(sc,cam,component)
 visible_end = None
 if full:
  end = ports[('elbow','OUTLET')]['point']
  other_meshes = [o for o in sc.objects if o.type=='MESH' and o not in instances['elbow']['meshes']]
  other_bvh, other_triangles = bvh(other_meshes)
  segment=end-Vector(pos);hit=other_bvh.ray_cast(Vector(pos),segment.normalized(),segment.length-.003)[0]
  assert hit is None, (name,'elbow outlet occluded by another asset or QA support',list(hit) if hit else None)
  visible_end={'outlet_world_m':list(end),'other_triangles_tested':other_triangles,'ray_clear':True,'scope':'Other-component/support occlusion only; actual silhouette visually reviewed'}
 frames.append({'name':name,'eye_m':pos,'target_m':target,'full_assembly_frame':full,'frame':fr,'elbow_outlet_visibility':visible_end})
 if '--preflight' in selected or (selected and name not in selected):continue
 sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'component_fixture.blend'),compress=True)
(OUT/'evidence.json').write_text(json.dumps({'scope':'Actual GLBs connected by measured geometric port interfaces on a neutral inspection floor/backing. No working fluid circuit, room, device logic or engine simulation. Open ends remain visible as interfaces.','imports':records,'actual_port_node_checks':port_checks,'actual_mating_seams':seams,'maintenance_prisms':clearances,'wall_mounts':mounts,'floor_contacts':floors,'views':frames,'render_only_supports':'Neutral floor and local console backing are QA-only, excluded from catalogue assets.'},indent=2)+'\n')
