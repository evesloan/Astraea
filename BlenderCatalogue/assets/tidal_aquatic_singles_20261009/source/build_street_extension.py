from pathlib import Path
import bpy,json,hashlib
B=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True)
parts=[('D14_SouthStreetFloor',(-44,88.38,-487.9),(4.1,.24,11.4)),('D14_SouthStreetEndGuard',(-44,89.05,-493.55),(4.1,1.1,.10)),('D14_Unbuilt394SafetyGuard',(-42.0,89.05,-487.9),(.10,1.1,11.2))]
parts.append(('D14_WestStreetGapGuard',(-46.0,89.05,-484.3),(.10,1.1,4.2)))
for name,c,s in parts:
 bpy.ops.mesh.primitive_cube_add(size=1,location=(c[0],-c[2],c[1]));o=bpy.context.object;o.name=name;o.dimensions=(s[0],s[2],s[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=bpy.data.materials.new(name+'Finish');m.diffuse_color=(.5,.46,.38,1);o.data.materials.append(m);o['runtime_collision']=True;o['status']='structural_construction_candidate';o['purpose']='Missing-only extension of existing D14 paired bank street to retained reservation382; guard394 until its receiving work'
bpy.ops.wm.save_as_mainfile(filepath=str(B/'source/TidalD14StreetExtension.blend'),compress=True)
p=B/'exports/TidalD14StreetExtension.glb';bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',export_extras=True)
(B/'STREET_EXTENSION.json').write_text(json.dumps({'model_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parts':4,'floor_y':88.5,'floor_xz_bounds':[-46.05,-493.6,-41.95,-482.2],'floor_area_m2':46.74,'existing_street_boundary_z':-482.2,'source_floor_overlap_m2':0,'limits':'Construction floor and three temporary guards; final structural/hull/enclosure review remains open. Remove394 safety guard only when that room receiving edge is built.'},indent=2)+'\n')
