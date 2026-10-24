"""Five source-mounted Tidal arrival portals; named editable successor, no slab cuts."""
from pathlib import Path
import bpy, json, hashlib, math
from mathutils import Vector
N=Path(__file__).resolve().parent; R=N.parents[2]; G=R/'Game/tidal_arrival_finish_20261024'
blend=N/'TidalArrivalPortals_r001.blend'; glb=G/'TidalArrivalPortals_r001.glb'
assert not blend.exists() and not glb.exists(), 'Immutable successor output already exists'
source=R/'BlenderCatalogue/assets/tidal_court_finish_20261023/TidalCourtSurfaceAndFixtures_r001.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='5f2a6a8db9922b241a0c7676ced4cf4e5c34ab71d5d7ec9e674e38c8f54d086e'
bpy.ops.wm.read_factory_settings(use_empty=True)
roles=['ivory_enamel','warm_walnut','champagne_metal']
with bpy.data.libraries.load(str(source),link=False) as (a,b): b.materials=['TidalCourtSurface_r001_'+x for x in roles]
materials={role:bpy.data.materials['TidalCourtSurface_r001_'+role] for role in roles}
lens=bpy.data.materials.new('TidalArrival_OpalLens');lens.use_nodes=True
bsdf=lens.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(1,.88,.67,1);bsdf.inputs['Roughness'].default_value=.5;bsdf.inputs['Emission Color'].default_value=(1,.77,.48,1);bsdf.inputs['Emission Strength'].default_value=.65
materials['opal_lens']=lens
parts=[];lights=[];supports=[]
def box(name, center, size, role, deck, bevel=.015):
 x,y,z=center;sx,sy,sz=size
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-z,y));o=bpy.context.object;o.name=name;o.dimensions=(sx,sz,sy)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Authored edge profile','BEVEL');mod.width=min(bevel,min(size)*.25);mod.segments=1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(materials[role]);o['runtime_collision']=role!='opal_lens';o['deck']=deck;o['role']=role;o['owner']='TidalArrivalPortals_r001';o['support_owner']='TG_Batch_'+str(329+deck-13)
 parts.append({'name':name,'center':list(center),'size':list(size),'role':role,'deck':deck,'contact':role!='opal_lens','min':[center[k]-size[k]/2 for k in range(3)],'max':[center[k]+size[k]/2 for k in range(3)]})
for deck in range(13,18):
 y=84+(deck-13)*4.5
 supports.append({'deck':deck,'node':'TG_Batch_'+str(329+deck-13),'min':[-76.44,y+2.88,-377.84],'max':[-72.56,y+3.8,-377.68],'minimum_new_y':y+2.9})
 # Complete source-mounted crown with stepped shoulders and recessed textured field.
 box(f'D{deck}_CrownBack',(-74.5,y+3.36,-377.62),(3.72,.90,.12),'warm_walnut',deck,.035)
 box(f'D{deck}_CrownSoffit',(-74.5,y+2.97,-377.51),(3.60,.14,.30),'ivory_enamel',deck,.025)
 for side in [-1,1]:
  box(f'D{deck}_Shoulder_{side}',(-74.5+side*1.75,y+3.30,-377.48),(.22,.66,.34),'ivory_enamel',deck,.04)
  box(f'D{deck}_ShoulderInner_{side}',(-74.5+side*1.58,y+3.43,-377.49),(.16,.50,.24),'ivory_enamel',deck,.035)
  box(f'D{deck}_LensSocket_{side}',(-74.5+side*.92,y+2.99,-377.43),(.48,.15,.12),'champagne_metal',deck,.02)
  box(f'D{deck}_OpalLens_{side}',(-74.5+side*.92,y+2.985,-377.361),(.38,.085,.016),'opal_lens',deck,.01)
  target=[-83 if side==-1 else -74.5,y+1.15,-376 if side==-1 else -366]
  row={'name':f'D{deck}_Arrival_'+('Stair'if side==-1 else'CrossStreet'),'position':[-74.5+side*.92,y+2.985,-377.342],'target':target,'range':22.0,'energy':3.0,'angle':72.0,'attenuation':.65,'color':[1,.90,.76],'source_fixture':f'D{deck}_OpalLens_{side}','deck':deck}
  lights.append(row)
 for i,x in enumerate([-1.2,-.6,0,.6,1.2]):
  h=.40-.05*abs(x)
  box(f'D{deck}_FlutedReveal_{i}',(-74.5+x,y+3.39,-377.50),(.12,h,.16),'ivory_enamel',deck,.025)
 box(f'D{deck}_UpperShadowBreak',(-74.5,y+3.75,-377.49),(3.25,.10,.22),'champagne_metal',deck,.02)
for row in lights:
 light=bpy.data.lights.new(row['name'],'SPOT');light.energy=140;light.color=row['color'];light.spot_size=math.radians(row['angle']*2);light.spot_blend=.5
 o=bpy.data.objects.new(row['name'],light);bpy.context.scene.collection.objects.link(o)
 x,y,z=row['position'];o.location=(x,-z,y);tx,ty,tz=row['target'];o.rotation_euler=(Vector((tx,-tz,ty))-o.location).to_track_quat('-Z','Y').to_euler()
 o['godot_parameters']=json.dumps(row);o['blender_watts_not_runtime_energy']=True
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.pack()
bpy.context.scene['scope']='Five header-mounted profiled arrival crowns and ten physical spot sources. Original header beams/slabs/rooms/contacts remain.'
bpy.context.scene['status']='SOURCE CANDIDATE; not final visual or gameplay acceptance'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
# Export only new mesh architecture; runtime light parameters are explicit in PLAN.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH')
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
plan={'status':'UNFINISHED_SOURCE_CANDIDATE','parent_commit':'c2d7383311d3f52574a150c56bac6a9b6e3a0c3e','parts':parts,'lights':lights,'supports':supports,'original_parts':334,'installed_guest_units':131,'new_rooms_rests_capacity':0,'new_floor_or_cut':False,'selector_budget':8,'source_plan':'res://tidal_court_finish_20261023/PLAN.json','source_plan_sha256':'4899b37fa73be0e8eec4017918f31ad9fba2ca09720876c22feb42c1efc03be7','model':'res://assets/models/AST-RES-TIDAL_lift_fit_r003.glb','model_sha256':'eedf652f8af8e34666123418b5654f15e2800b33e57bf85a7b87f7b1964ed8ad','glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),'source_material_library_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'references':['master chapter21 fixture-driven illumination and shaped thresholds','master chapter32 preserve interfaces','pixel-inspected master image6 and image11'],'camera_exposure_changed':False}
(G/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(G/'evidence/NATIVE.json').write_text(json.dumps({'status':'PASS_NATIVE_EXPORT_ONLY','parts':len(parts),'physical_emitters':len(lights),'native':{'bytes':blend.stat().st_size,'sha256':plan['native_sha256']},'glb':{'bytes':glb.stat().st_size,'sha256':plan['glb_sha256']},'original_sources_unchanged':True},indent=2)+'\n')
print('TIDAL_ARRIVAL_NATIVE',len(parts),len(lights),glb.stat().st_size)
