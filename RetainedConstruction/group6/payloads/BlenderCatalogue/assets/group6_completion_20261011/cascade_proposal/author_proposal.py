"""Inactive cascade maintenance console on the original Group6 shoulder.
All source context and registered watercourse reference remain intact; only new
console/control/fitting meshes are exchanged. Group8 owns onward connection.
"""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent;R=P.parents[3];A=P.parent
source=A/'AquaticCompletion_r019.blend';reference=R/'BlenderCatalogue/assets/vesper_watercourse/source/AST-AQU-015.blend'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='bfdb836e5e189fb1209f1ff7ae731caf7034d1960d2e659e78c7b5dfc532fb28'
destination=P/'Group6CascadeInterfaceProposal_r002.blend';assert not destination.exists()
bpy.ops.wm.open_mainfile(filepath=str(source));S=bpy.context.scene
code=(A/'author_completion.py').read_text();exec(code[code.index('def digest(o):'):code.index('before={')])
originals={o.name:digest(o) for o in S.objects if o.type=='MESH'};packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
with bpy.data.libraries.load(str(reference),link=False) as (available,loaded):loaded.objects=available.objects
reference_hashes={}
for o in loaded.objects:
 if o is None:continue
 S.collection.objects.link(o);o.parent=None;o.matrix_world=Matrix.Translation(Vector((21.5,-207,61)))@o.matrix_world;o['group6_role']='registered_cascade_context_only'
 if o.type=='MESH':reference_hashes[o.name]=digest(o)
NEW=[]
M={k:bpy.data.materials[v] for k,v in {'stone':'ASTRAEA_warm_stone','ivory':'ASTRAEA_ivory_enamel','metal':'ASTRAEA_champagne_metal','teal':'ASTRAEA_teal_weave','lens':'AQD_opal'}.items()}
def xyz(p):return Vector((p[0],-p[2],p[1]))
def finish(o,n,material='metal',kind='architecture'):
 o.name=('G6_CASCADE__'+n).replace('.', '_');o['group6_role']=kind;o['programme_key']='D08_directory_08';o['construction_status']='inactive shared-interface proposal';o.data.materials.clear();o.data.materials.append(M[material]);o.data.update()
 uv=o.data.uv_layers.new(name='UV0')
 for f in o.data.polygons:
  axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(f.normal[j]))]
  for li in f.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.5,v[axes[1]]*.5)
 NEW.append(o);return o
def box(n,p,d,material='ivory',bevel=.025,kind='architecture'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 q=o.modifiers.new('Source crafted edges','BEVEL');q.width=min(bevel,min(d)*.2);q.segments=2;bpy.ops.object.modifier_apply(modifier=q.name)
 return finish(o,n,material,kind)
def rod(n,a,b,r=.035,material='metal',kind='architecture'):
 a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,material,kind)
# Narrow enclosure stays on the original north edge. No floor/guard/receiver cut.
box('cabinet_foot',(21.9,44.04,214.45),(1.30,.08,.24),'metal')
box('cabinet_body',(21.9,44.70,214.45),(1.25,1.24,.24),'ivory')
box('cabinet_recess',(21.9,45.02,214.582),(1.07,.69,.025),'teal')
box('counter_cap',(21.9,45.36,214.45),(1.34,.10,.31),'stone')
for x in [21.34,22.46]:box('panel_side_'+str(x),(x,45.04,214.60),(.065,.80,.07),'metal')
box('panel_crown',(21.9,45.41,214.60),(1.20,.07,.07),'metal')
valves=[]
for i,(x,circuit) in enumerate([(21.60,'cascade supply'),(22.20,'cascade return')]):
 rod('isolator_'+str(i)+'_stem',(x,45.14,214.57),(x,45.14,214.69),.04)
 bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=8,location=xyz((x,45.14,214.71)),major_radius=.145,minor_radius=.018);wheel=bpy.context.object;wheel.rotation_euler.x=math.pi/2;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(wheel,'isolator_'+str(i)+'_handwheel_source','metal','mechanical_wheel')
 # Spokes share the same moving mesh, around a full actual source pivot.
 spokes=[]
 for j in range(3):
  a=j*math.tau/3;spokes.append(rod('isolator_'+str(i)+'_spoke_'+str(j),(x,45.14,214.71),(x+.135*math.cos(a),45.14+.135*math.sin(a),214.71),.012))
 bpy.ops.object.select_all(action='DESELECT');wheel.select_set(True)
 for o in spokes:o.select_set(True);NEW.remove(o)
 bpy.context.view_layer.objects.active=wheel;bpy.ops.object.join();wheel['group6_role']='mechanical_wheel'
 valves.append({'id':'aquatic_cascade_isolator_'+str(i)+'_proposal_001','mesh':wheel.name,'pivot_xyz':[x,45.14,214.71],'travel_radians':math.pi/2,'axis':'z','circuit':circuit,'mechanical_only':True,'fluid_temperature_pressure_or_permissions_implemented':False})
 # Paired local terminals stop before the original east guard. Group8 routes onward.
 terminals=[]
for i,circuit in enumerate(['supply','return']):
 y=44.82+i*.22;rod(circuit+'_local_header',(22.35,y,214.42),(22.73,y,214.42),.035)
 rod(circuit+'_internal_terminal',(22.69,y,214.42),(22.75,y,214.42),.060)
 terminals.append({'circuit':circuit,'terminal_xyz':[22.75,y,214.42],'normal_xyz':[1,0,0],'radius_m':.06,'onward_owner':'Group8/shared integration','connected_network':False})
 # Real enclosed task fitting bears on the original acoustic hood underside.
rod('task_mount',(21.9,46.53,215.10),(21.9,46.41,215.10),.025)
box('task_hood',(21.9,46.39,215.10),(.40,.12,.35),'metal')
box('task_lens',(21.9,46.31,215.10),(.29,.04,.25),'lens',kind='fixture_lens')
task={'id':'aquatic_cascade_console_task_proposal_001','source_xyz':[21.9,46.265,215.10],'target_xyz':[21.9,45.05,214.65],'energy':.55,'range_m':3.0,'half_cone_degrees':55,'mounted_to':'Original AQD__cascade_acoustic_hood; contact below original underside46.53'}
assert all(digest(bpy.data.objects[n])==h for n,h in originals.items())
for im in bpy.data.images:
 if im.packed_file:im.use_fake_user=True
bpy.ops.wm.save_as_mainfile(filepath=str(destination))
bpy.ops.object.select_all(action='DESELECT')
for o in NEW:o.select_set(True)
export=P/'Group6CascadeInterfaceProposal_r002.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_materials='EXPORT')
contract={'status':'inactive proposal; Group8/shared owner review required','programme_key':'D08_directory_08','source_context':str(source.relative_to(R)),'source_context_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_context_mesh_hashes':originals,'packed_context_images':packed,'registered_reference':str(reference.relative_to(R)),'registered_reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'registered_reference_mesh_hashes':reference_hashes,'native':str(destination.relative_to(R)),'native_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'export':str(export.relative_to(R)),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'new_mesh_hashes':{o.name:digest(o) for o in NEW},'new_mesh_roles':{o.name:o['group6_role'] for o in NEW},'original_shoulder_rect_xz':[21,23,214.3,215.7],'original_shoulder_top_y':44,'operator_stance_xyz':[21.9,44,215.20],'west_approach_xyz':[21.5,44,215.20],'valves':valves,'task_light':task,'terminals':terminals,'new_floor_owner_count':0,'new_destination_count':0,'new_capacity':0,'receiver_stream_spine_or_shared_root_modified':False,'fluid_or_acoustic_operation_implemented':False,'cascade_onward_network_connected':False}
(P/'CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n');print('CASCADE PROPOSAL SOURCE PASS',len(originals),len(reference_hashes),len(NEW))
