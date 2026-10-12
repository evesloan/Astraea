from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());F=R/'BlenderCatalogue/assets/group4_completion_20261011/Group4_Completion_Receiving_r002.blend';sourcehash=hashlib.sha256(F.read_bytes()).hexdigest()
catalogue=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
for id in ['AST-TRM-G4-034','AST-TRM-G4-035']:assert all(a['catalogue_id']!=id for a in catalogue['assets'])
bpy.ops.wm.open_mainfile(filepath=str(F));bpy.context.preferences.filepaths.save_version=0
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
family='group4_operating_controls_018';FAMILY=family;parts=[];markers=[];collections={}
for name in ['CAR_CONSOLE_AND_WORK_LAMP','STATION_GATE_CALL_CONTROL','UNEXPORTED_REFERENCE_AND_STUDIO']:
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);collections[name]=c
B=lambda p:(p[0],-p[2],p[1]);sc=(R/'BlenderCatalogue/assets/group4_tram_connections_20261009/build_source.py').read_text();exec(sc[sc.index('def mesh('):sc.index('def guard(')],globals())
metal=bpy.data.materials['champagne_metal'];enamel=bpy.data.materials['ivory_enamel'];opal=enamel.copy();opal.name='G4_Operating_Opal_r001';bsdf=next(n for n in opal.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bsdf.inputs['Emission Color'].default_value=(1,.86,.67,1);bsdf.inputs['Emission Strength'].default_value=.6
current=collections['CAR_CONSOLE_AND_WORK_LAMP']
verts=[(x,y,z) for x in [-.36,.36] for y,z in [(1.155,-2.23),(1.155,-2.01),(1.26,-2.01),(1.37,-2.23)]]
mesh('CarConsole_ReceivedSlopedHousing',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],enamel,'positive15mm old control pedestal embed; new local source, no original modified')
box('CarConsole_ReceiverFoot',(0,1.166,-2.12),(.70,.032,.20),metal,'positive original pedestal receiving under console')
buttons=[];normal=Vector((0,1,.5)).normalized()
for index,(label,x,z) in enumerate([(s,x,-2.07) for s,x in zip(['FORWARD','FORE_MIDSHIP','CENTRAL','AFT_MIDSHIP','AFT'],[-.28,-.14,0,.14,.28])]+[(s,x,-2.19) for s,x in zip(['SECURE','BOARDING','CLAMP'],[-.21,0,.21])]):
 face=Vector((x,1.26+(-z-2.01)*.5,z));inner=face-normal*.005;outer=face+normal*.010;name='CarConsole_Button_'+label
 tube(name+'_ReceivedRim',inner-normal*.002,outer-normal*.005,.048,metal,'bounded source button rim received into sloping console')
 tube(name+'_OpalFace',inner,outer,.037,opal,'physical button face; same original enamel texture with explicit local emission derivative')
 buttons.append({'id':label,'source_mesh':name+'_OpalFace','root':'vehicle','surface_center_xyz':list(outer),'axis_xyz':list(normal),'radius_m':.037,'target_depth_m':.001,'physical_face_height_m':.015,'original_car_parent_unchanged':True})
box('CarWorkLamp_RoofReceiver',(0,2.574,.14),(.50,.052,.65),metal,'positive original coral roof reveal receiving; no roof cut or original geometry change')
box('CarWorkLamp_EnamelShade',(0,2.545,.14),(.46,.070,.61),enamel,'bounded downlight shade wholly inside original car roof envelope')
box('CarWorkLamp_OpalLens',(0,2.507,.14),(.37,.016,.52),opal,'source-backed original-texture opal downlight lens')
car_light={'id':'group4_car_work_lamp_proposal','source_mesh':'CarWorkLamp_OpalLens','position_xyz':[0,2.494,.14],'aim_xyz':[0,-1,0],'full_cone_degrees':110,'range_m':6,'initial_energy':.85,'color':[1,.89,.73],'shadow_requested':True,'illumination_anchor':[0,.96,.14]}
exports=[]
def export(c,id,filename):
 bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:o.select_set(True)
 p=W/filename;bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
 exports.append({'id':id,'file':filename,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_count':len([o for o in c.objects if o.type=='MESH'])})
export(current,'AST-TRM-G4-034','AST-TRM-G4-034_car_console_worklamp_r001.glb')
current=collections['STATION_GATE_CALL_CONTROL']
box('StationCall_StileReceiver',(-1.55,1.10,-.075),(.20,.28,.025),metal,'positive15mm original negative-side ivory stile-skin receiving; aperture unchanged')
box('StationCall_ProfiledHousing',(-1.55,1.10,-.1325),(.18,.25,.125),enamel,'received housing beyond actual original clear apertureX±1.2')
tube('StationCall_ButtonRim',(-1.55,1.1,-.192),(-1.55,1.1,-.203),.052,metal,'bounded button ring received in housing')
tube('StationCall_OpalFace',(-1.55,1.1,-.192),(-1.55,1.1,-.211),.042,opal,'physical station call source; same8-facet source language')
station_button={'id':'STATION_CALL','source_mesh':'StationCall_OpalFace','root':'actual station gate local frame','surface_center_xyz':[-1.55,1.1,-.211],'axis_xyz':[0,0,-1],'radius_m':.042,'target_depth_m':.001,'physical_face_height_m':.019,'original_frame_pin':'Game/assets/models/AST-DOR-003.glb','frame_skin_bounds_xyz':[[-1.9,0,-.085],[-1.2,2.65,-.06]],'source_aperture_x':[-1.2,1.2],'five_instances_on_existing_original_gate_scales':True}
export(current,'AST-TRM-G4-035','AST-TRM-G4-035_station_call_control_r001.glb')
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file:image.pack()
bpy.ops.file.make_paths_relative();native='Group4_Mounted_Operating_Controls_and_CarLamp_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(W/native),compress=True);assert hashlib.sha256(F.read_bytes()).hexdigest()==sourcehash
d={'active':False,'family':family,'native':native,'material_donor_native':str(F.relative_to(R)),'material_donor_sha256':sourcehash,'exports':exports,'car_buttons':buttons,'station_call_button':station_button,'car_light':car_light,'mesh_count':sum(e['mesh_count'] for e in exports),'new_floor_m2':0,'original_models_source_room_ids_capacity_unchanged':True,'local_opal_derivative':'Exact copied ivory enamel graph/texture; only copied material name and emission Color(1,.86,.67)/Strength.6 differ. Original material/source unchanged.','ordinary_controls_and_light_optics_require_actual_tests':True,'main_integrated':False,'engineering_species_hardware_final_art_or_whole_group_accepted':False};(W/'SOURCE_INTERFACE.json').write_text(json.dumps(d,indent=2)+'\n');print('G4_OPERATING_CONTROLS_SOURCE_BUILT',d['mesh_count'],'closed meshes;8 car controls,5 station-call bindings,one mounted car lamp;newfloor0;inactive')
