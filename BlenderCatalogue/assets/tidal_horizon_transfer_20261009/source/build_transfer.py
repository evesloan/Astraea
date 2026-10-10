"""Additive, source-pinned Horizon/Tidal roof transfer contact geometry.
No engineering load certification; do not modify either retained predecessor.
"""
from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parents[1];E=O/'exports';E.mkdir(exist_ok=True)
H=R/'Game/assets/models/SOL_D12_directory_01_entry001.glb';P=R/'BlenderCatalogue/assets/residential_hotels/tidal_garden_20261007_r001/residential-neighborhood-courts-20261007/tidal_garden_house/outputs/house_r001/PLAN.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={str(H.relative_to(R)):sha(H),str(P.relative_to(R)):sha(P)}
assert pins[str(H.relative_to(R))]=='82083e408bbe5dca5abdcbdec21332baaf9c6e14777fd83467331adcc4011a12'
assert not(O/'source/horizon_transfer.blend').exists()
bpy.ops.wm.read_factory_settings(use_empty=True)
mat=bpy.data.materials.new('Tidal_Concealed_Transfer_Steel');mat.diffuse_color=(.16,.19,.20,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Metallic'].default_value=.45;bs.inputs['Roughness'].default_value=.7
parts=[]
def box(name,x0,x1,y0,y1,z0,z1,role,contact):
 # Shared corners, explicit outward Blender face winding, no disconnected-face recalculation.
 world=[(x,y,z)for z in [z0,z1]for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([(x,-z,y)for x,y,z in world],[],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);mesh.update();mesh.materials.append(mat)
 ob=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(ob);ob['role']=role;ob['geometric_contact']=contact;ob['runtime_collision']=True
 uv=mesh.uv_layers.new(name='MetreScaled')
 for poly in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));other=[i for i in range(3)if i!=axis]
  for li in poly.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[other[0]],v[other[1]])
 parts.append({'name':name,'bounds_world_xyz':[[x0,y0,z0],[x1,y1,z1]],'role':role,'contact':contact})
# The upper reinforcement stays above the measured retained canopy maximum83.4296875.
for x in [-45.8,-42.2,-28.75,-12.4,-8.55]:
 box('TGH_Longitudinal_'+str(x),x-.17,x+.17,83.45,83.76,-466.3,-397.7,'concealed_floor_transfer','Meets both retained longitudinal ends and D13 floor underside')
for i,z in enumerate(range(-456,-407,8)):
 box('TGH_CrossTie_'+str(i),-50.65,-8.38,83.45,83.76,z-.17,z+.17,'concealed_floor_transfer','Joins longitudinal grid, existing rear pier and screened front wall head')
 box('TGH_RearPierCap_'+str(i),-50.65,-50.15,83.10,83.45,z-.15,z+.15,'pier_contact','Retained fan_rear_pier'+str(i)+' top at83.10')
 if z!=-432:
  box('TGH_FrontWallCap_'+str(i),-8.86,-8.54,82.96,83.45,z-.15,z+.15,'wall_contact','Retained entry_left/right wall top at82.96; central portal is excluded')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/horizon_transfer.blend'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(E/'horizon_transfer.glb'),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
assert all(sha(R/p)==h for p,h in pins.items())
contract={'schema':'astraea.tidal_horizon_transfer.v1','status':'SOURCE_GEOMETRY_PENDING_CONTACT_CHECK','source_pins':pins,'parts':parts,'source_part_count':len(parts),'floor_underside_y':83.76,'retained_canopy_max_y':83.4296875,'grid_lower_y':83.45,'original_room_floor_y':78,'scope':'Concealed geometric roof-to-floor transfer; rear/front contacts only extend retained opaque supports. No structural engineering or load capacity certification. No modification to Horizon, Tidal allocations, floor owners, door openings or room identities.','holds':['Actual imported contact and source preservation checks','Source-context visual review','Listening Salon transfer remains separate and unresolved','Not installed in default scene'],'native_sha256':sha(O/'source/horizon_transfer.blend'),'export_sha256':sha(E/'horizon_transfer.glb')}
(O/'TRANSFER_CONTRACT.json').write_text(json.dumps(contract,indent=2)+'\n');print('HORIZON_TRANSFER_SOURCE_READY',len(parts),flush=True)
