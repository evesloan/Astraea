from pathlib import Path
import bpy,json,hashlib
P=Path(__file__).parent;T=P/'import/Game';bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.75;return m
stone=material('Receiving_warm_stone',(.52,.49,.40));steel=material('Receiving_dark_zinc',(.18,.20,.21));parts=[]
def box(name,bounds,mat,kind):
 x0,x1,y0,y1,z0,z1=bounds;vs=[(x,-z,y)for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]];faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 if kind=='threshold_ramp':
  vs[4]=(vs[4][0],vs[4][1],102.0);vs[5]=(vs[5][0],vs[5][1],102.0)
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],[tuple(reversed(face))for face in faces]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);parts.append({'name':name,'bounds_xyz':bounds,'kind':kind})
box('Exact_source_adjunct_receiver',[79,89,101.76,102,-24,-16],stone,'source_floor')
box('West_approach_strip',[60.9,81,101.76,102,-16,-14.2],stone,'missing_connector')
box('West_approach_landing',[59.1,60.9,101.76,102,-16,-14.37],stone,'missing_connector')
box('Short_west_connection',[59.1,60.9,101.76,102.025,-14.37,-14.07],stone,'threshold_ramp')
for i,x in enumerate([79.5,84,88.5]):
 box('Underfloor_longitudinal_'+str(i),[x-.12,x+.12,101.50,101.84,-24,-14.15],steel,'frame_crossmember')
 box('Lapped_adjunct_transfer_'+str(i),[x-.12,x+.12,101.78,101.84,-14.5,-12.5],steel,'frame_bearing_on_original_D17')
for i,x in enumerate(range(60,81,2)):
 box('Approach_bracket_'+str(i),[x-.12,x+.12,101.50,101.84,-16,-14.15],steel,'frame_crossmember')
 box('Lapped_approach_transfer_'+str(i),[x-.12,x+.12,101.78,101.84,-14.5,-12.5],steel,'frame_bearing_on_original_D17')
box('Outer_approach_edge_tie',[59.1,81,101.50,101.84,-15.95,-15.71],steel,'frame_crossmember')
for i,z in enumerate([-23.7,-20,-16.25]):box('Underfloor_crossmember_'+str(i),[79.15,88.85,101.50,101.84,z-.12,z+.12],steel,'frame_crossmember')
segments=[(79,-24,89,-24),(89,-24,89,-16),(89,-16,81,-16),(81,-16,81,-14.2),(81,-14.2,60.9,-14.2),(60.9,-14.2,60.9,-14.07),(59.1,-14.07,59.1,-16),(59.1,-16,79,-16),(79,-16,79,-24)]
for i,(x0,z0,x1,z1)in enumerate(segments):
 for j,y in enumerate([102.55,103.05]):box('Edge_rail_'+str(i)+'_'+str(j),[min(x0,x1)-.03,max(x0,x1)+.03,y-.03,y+.03,min(z0,z1)-.03,max(z0,z1)+.03],steel,'guard_rail')
 count=max(1,int(max(abs(x1-x0),abs(z1-z0))/2+.999))
 for j in range(count+1):
  x=x0+(x1-x0)*j/count;z=z0+(z1-z0)*j/count;box('Edge_post_'+str(i)+'_'+str(j),[x-.03,x+.03,101.97,103.08,z-.03,z+.03],steel,'guard_post')
plan={'schema':'astraea.root_supported_adjunct_receiving.v1','base':'403ccf17ddff1e3fa1e987a67d69048583c73366','source_key':'starboard_central_upper_house','source_floor_m2':80,'connector_m2':39.654,'receiver_region':'D17_starboard_house_extension','new_compiler_owners':0,'immutable_source_geometry_edited':False,'beam_primary_structure_capacity_and_lower_section_acceptance':False,'private_admission_and_service_operation':False,'parts':parts};(P/'RECEIVING_FRAME_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');bpy.data.texts.new('RECEIVING_FRAME_PLAN.json').write(json.dumps(plan,indent=2));out=T/'assets/group2_central_receiving_20261013/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.glb';out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=False);print('CENTRAL_RECEIVING_NATIVE_FRAME_EXPORTED',len(parts))

# Editable scoped guard successor references are retained in native authoring but are not exported into the frame; runtime keeps original materials and node/body identities.
pre=json.loads((P/'EXACT_GUARD_PREIMAGES.json').read_text())
for row in pre['rows']:
 a=row['world_min'];b=row['world_max']
 for side,lo,hi in [('left',a[0],59.1),('right',60.9,b[0])]:box('GUARD_REFERENCE_'+row['name']+'_'+side,[lo,hi,a[1],b[1],a[2],b[2]],steel,'unexported_editable_guard_reference')
bpy.data.texts.new('EXACT_GUARD_PREIMAGES.json').write(json.dumps(pre,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/CENTRAL_ADJUNCT_RECEIVING_FRAME_r004.blend'))
