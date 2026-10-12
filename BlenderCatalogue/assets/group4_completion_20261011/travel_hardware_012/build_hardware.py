from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());P=json.loads((W/'TRAVEL_SOURCE_PLAN.json').read_text())
CAT=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());owners={a['catalogue_id']:a for a in CAT['assets']}
assert not any(i in owners for i in P['reserved_unregistered_ids'])
FAMILY='group4_travel_hardware_012';F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';SOURCE=R/'BlenderCatalogue/assets/group4_completion_20261011/boarding_safety_009/Group4_Powered_Portal_Body_r001.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0
for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
for co in list(bpy.data.collections):bpy.data.collections.remove(co)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
B=lambda p:(p[0],-p[2],p[1]);parts=[];markers=[];current=None;collections={}
for name in ['BOGIE_HARDWARE','END_BUFFER_HARDWARE','UNEXPORTED_REFERENCE_AND_STUDIO']:
 co=bpy.data.collections.new(name);scene.collection.children.link(co);collections[name]=co
metal=bpy.data.materials['champagne_metal'];rubber=bpy.data.materials['dark_rubber']
sc=(F/'build_source.py').read_text();exec(sc[sc.index('def mesh('):sc.index('def guard(')],globals())
current=collections['BOGIE_HARDWARE'];witnesses=[]
for z in [-1.5,1.5]:
 fixed=marker('BOGIE_FIXED_ROOT_'+str(z),(0,0,0),'fixed original-car-underfloor receiver; body-relative source')
 start=len(parts)
 for zz in [-.20,.20]:
  box('Bolster_Fixed_SlideGuide_'+str((z,zz)),(0,-.225,z+zz),(2.02,.04,.07),metal,'fixed transverse slide guide; positive25mm original floor receiver','moving_shape_candidate')
 box('Bolster_Fixed_FloorLap_'+str(z),(0,-.215,z),(1.98,.04,.28),metal,'positive original underfloor lap; mechanical sizing remains open','moving_shape_candidate')
 for x in [-.95,.95]:box('Bolster_Fixed_EndShoe_'+str((z,x)),(x,-.24,z),(.12,.08,.48),metal,'fixed guide end shoe','moving_shape_candidate')
 for x in [-.23,.23]:box('Bolster_Fixed_TravelStop_'+str((z,x)),(x,-.28,z+.25),(.03,.10,.07),metal,'bounded0.20m cross-slide stop witness','no_collision_detail')
 for ob in parts[start:]:ob.parent=fixed
 pivot=marker('BOGIE_MOVING_ROOT_'+str(z),(0,-.2,z),'source truck steering axis at original kingpin; slide±0.20m, separate original wheels reused')
 bpy.context.view_layer.update()
 start=len(parts)
 box('Bogie_CrossSlide_Carriage_'+str(z),(0,-.255,z),(.38,.08,.28),metal,'moving carriage positively meets fixed floor lap; capacity open','animatable_shape_candidate')
 box('Bogie_Transverse_Frame_'+str(z),(0,-.25,z),(1.70,.045,.16),metal,'steering truck frame;3m kingpin chord and original gauge retained','animatable_shape_candidate')
 tube('Bogie_Original_Axle_'+str(z),(-.86,-.2,z),(.86,-.2,z),.035,metal,'original wheel axis shaft; no wheel asset duplicated','animatable_shape_candidate')
 for x in [-.79,.79]:
  box('Bogie_Axle_Bearing_'+str((z,x)),(x,-.22,z),(.14,.10,.20),metal,'positive axle/bearing receiver','animatable_shape_candidate')
 for x in [-.15,.15]:tube('Bogie_Slide_Bearing_'+str((z,x)),(x,-.29,z-.18),(x,-.21,z-.18),.025,metal,'source bearing/pin witness','no_collision_detail')
 for ob in parts[start:]:ob.parent=pivot;ob.matrix_parent_inverse=pivot.matrix_world.inverted()
 witnesses.append({'kingpin_z':z,'original_floor_bounds_y':[-.22,0],'fixed_floor_lap_y':[-.235,-.195],'positive_embed_m':.025,'slide_limit_m':.20,'maximum_source_travel_m':P['maximum_cross_slide_m'],'wheel_meshes_reused':2,'wheel_asset_exported':False})
current=collections['END_BUFFER_HARDWARE'];buffer_receivers=[]
for sign in [-1,1]:
 z=sign*465.6;start=len(parts)
 for x in [-.86,.86]:
  box('EndBuffer_WebFoot_'+str((sign,x)),(-5.6+x,55.64,z),(.36,.10,.60),metal,'positive90mm retained guideway-web receiving; capacity remains open')
  box('EndBuffer_Column_'+str((sign,x)),(-5.6+x,56.04,z),(.16,.88,.18),metal,'buffer column positively received in web foot')
 box('EndBuffer_Crosshead_'+str(sign),(-5.6,56.38,z),(2.20,.16,.20),metal,'physical terminal crosshead')
 for x in [-.65,.65]:box('EndBuffer_RubberPad_'+str((sign,x)),(-5.6+x,56.38,z-sign*.18),(.30,.30,.24),rubber,'physical inward terminal energy-pad source; impact/capacity not certified')
 for x in [-1.0,1.0]:box('EndBuffer_FootLedger_'+str((sign,x)),(-5.6+x,55.62,z),(.18,.08,.90),metal,'positive guideway-web end receiving ledger')
 buffer_receivers.append({'z':z,'track_x':-5.6,'web_floor_y':[55.55,55.68],'new_foot_y':[55.59,55.69],'positive_embed_m':.09,'ordinary_travel_limit_centre_z':sign*462,'impact_tested':False})
exports=[]
for co,name in [('BOGIE_HARDWARE','AST-TRM-G4-028_steering_bogie_hardware_r002.glb'),('END_BUFFER_HARDWARE','AST-TRM-G4-029_terminal_end_buffers_r002.glb')]:
 bpy.ops.object.select_all(action='DESELECT')
 for ob in collections[co].objects:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(W/name),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 exports.append({'file':name,'sha256':hashlib.sha256((W/name).read_bytes()).hexdigest(),'mesh_count':sum(o.type=='MESH' for o in collections[co].objects)})
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(W/'Group4_Steering_Bogies_and_EndBuffers_r002.blend'),compress=True)
(W/'HARDWARE_INTERFACE.json').write_text(json.dumps({'family':FAMILY,'reserved_unregistered_ids':P['reserved_unregistered_ids'],'native':'Group4_Steering_Bogies_and_EndBuffers_r002.blend','exports':exports,'bogie_receivers':witnesses,'end_buffer_receivers':buffer_receivers,'original024_body_and_four_wheels_unchanged':True,'original_wheels_exported_or_duplicated':False,'mechanical_capacity_or_impact_accepted':False,'whole_group_complete':False},indent=2)+'\n');print('TRAVEL_HARDWARE_BUILT',exports)
