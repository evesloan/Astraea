from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).parent;T=P/'import/Game';bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.75;return m
stone=material('Receiving_warm_stone',(.52,.49,.40));steel=material('Receiving_dark_zinc',(.18,.20,.21));parts=[]
def box(name,bounds,mat,kind):
 x0,x1,y0,y1,z0,z1=bounds;vs=[(x,-z,y)for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);parts.append({'name':name,'bounds_xyz':bounds,'kind':kind})
box('Exact_source_adjunct_receiver',[79,89,101.76,102,-24,-16],stone,'source_floor')
box('Missing_connection_to_original_D17',[83.1,84.9,101.76,102,-16,-14],stone,'missing_connector')
for i,x in enumerate([79.5,84,88.5]):box('Underfloor_longitudinal_'+str(i),[x-.12,x+.12,101.50,101.84,-24,-12.5],steel,'frame_bearing_on_original_D17')
for i,z in enumerate([-23.7,-20,-16.25]):box('Underfloor_crossmember_'+str(i),[79.15,88.85,101.50,101.84,z-.12,z+.12],steel,'frame_crossmember')
segments=[(79,-24,89,-24),(79,-24,79,-16),(89,-24,89,-16),(79,-16,83.1,-16),(84.9,-16,89,-16),(83.1,-16,83.1,-14),(84.9,-16,84.9,-14)]
for i,(x0,z0,x1,z1)in enumerate(segments):
 for j,y in enumerate([102.55,103.05]):box('Edge_rail_'+str(i)+'_'+str(j),[min(x0,x1)-.03,max(x0,x1)+.03,y-.03,y+.03,min(z0,z1)-.03,max(z0,z1)+.03],steel,'guard_rail')
 count=max(1,int(max(abs(x1-x0),abs(z1-z0))/2+.999))
 for j in range(count+1):
  x=x0+(x1-x0)*j/count;z=z0+(z1-z0)*j/count;box('Edge_post_'+str(i)+'_'+str(j),[x-.03,x+.03,101.97,103.08,z-.03,z+.03],steel,'guard_post')
plan={'schema':'astraea.root_supported_adjunct_receiving.v1','base':'5bd2cd60376954825712d7ddfde6a7b628feb46f','source_key':'starboard_central_upper_house','source_floor_m2':80,'connector_m2':3.6,'receiver_region':'D17_starboard_house_extension','new_compiler_owners':0,'immutable_source_geometry_edited':False,'beam_primary_structure_capacity_and_lower_section_acceptance':False,'private_admission_and_service_operation':False,'parts':parts};(P/'RECEIVING_FRAME_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');bpy.data.texts.new('RECEIVING_FRAME_PLAN.json').write(json.dumps(plan,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/CENTRAL_ADJUNCT_RECEIVING_FRAME.blend'));out=T/'assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME.glb';out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=False);print('CENTRAL_RECEIVING_NATIVE_FRAME_EXPORTED',len(parts))
