"""NEW compact connector source/export. No compiler floor, old source or Game edit."""
import bpy,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');BASE=P/'source/firstpass_003/source_repair003/AST-CUL-005_firstpass_003.blend';EXPECTED='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();OUT=R/'AST-CUL-005_bridge_002.blend';GLB=R/'AST-CUL-005_bridge_002.glb';assert sha(BASE)==EXPECTED and not OUT.exists()and not GLB.exists()
sys.path.insert(0,str(P/'source/firstpass_001'));from firstpass_common import material_record,digest
sys.path.insert(0,str(P/'source/firstpass_003/dependencies'));from precise_normal_export import precise_normals
bpy.ops.wm.read_factory_settings(use_empty=True);d=json.loads((R/'BRIDGE_GEOMETRY_002.json').read_text());assert json.loads((R/'GEOMETRY_SCREEN.json').read_text())['passed_source_route_and_floor_support']
map={'ivory_enamel':'ASTRAEA_ivory_enamel','champagne_metal':'ASTRAEA_champagne_metal','warm_walnut':'ASTRAEA_warm_walnut','gallery_glass':'gallery_glass','hospitality_opal':'FP2_PublicOpal'}
with bpy.data.libraries.load(str(BASE),link=False)as(src,dst):
 assert set(map.values())<=set(src.materials);dst.materials=list(map.values())
mats={role:bpy.data.materials[name]for role,name in map.items()};specs=json.loads((P.parents[1]/'materials/material_manifest.json').read_text())['materials'];root=bpy.data.objects.new('AST_CUL005_D11_RECEIVING_PORTICO',None);bpy.context.collection.objects.link(root);root['compiler_slab']=json.dumps(d['compiler_slab']);root['source_only_uninstalled']=True;expected={};records=[]
for o in d['objects']:
 world=np.array(o['vertices_world'],float);origin=np.floor(world.mean(0));local=world-origin;vertices=[(p[0],-p[2],p[1])for p in local];me=bpy.data.meshes.new(o['name']);me.from_pydata(vertices,[],o['faces']);me.materials.append(mats[o['material_family']]);me.update();uv=me.uv_layers.new(name='material_scaled_metric_uv');scale=specs.get(o['material_family'],{}).get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3)if k!=axis]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
 ob=bpy.data.objects.new(o['name'],me);bpy.context.collection.objects.link(ob);ob.parent=root;ob.location=(origin[0],-origin[2],origin[1]);ob['semantic_id']=o['name'];ob['source_role']=o['role'];ob['material_family']=o['material_family'];ob['collision_role']='static_source_mesh';bpy.context.view_layer.update();me.calc_loop_triangles();xyz=[];uvs=[];norm=[]
 for t in me.loop_triangles:
  for vi,li in zip(t.vertices,t.loops):
   p=ob.matrix_world@me.vertices[vi].co;n=me.corner_normals[li].vector;u=uv.data[li].uv;xyz.append([p.x,p.z,-p.y]);uvs.append([u[0],1-u[1]]);norm.append([n.x,n.z,-n.y])
 expected[o['name']+'_xyz']=np.array(xyz).reshape(-1,3,3);expected[o['name']+'_uv']=np.array(uvs).reshape(-1,3,2);expected[o['name']+'_normal']=np.array(norm).reshape(-1,3,3);records.append({'name':ob.name,'material':mats[o['material_family']].name,'role':o['role'],'triangles':len(me.loop_triangles),'material_tile_m':scale,'location_blender':list(ob.location)})
for row in d['lights']:
 data=bpy.data.lights.new(row['id'],'SPOT');data.energy=row['source_preview_watts'];data.color=row['color_linear'];data.spot_size=math.radians(row['full_cone_degrees']);data.shadow_soft_size=.04;ob=bpy.data.objects.new(row['id'],data);bpy.context.collection.objects.link(ob);ob.location=(row['position_world'][0],-row['position_world'][2],row['position_world'][1]);ob['fixture_contract']=json.dumps(row)
 marker=bpy.data.objects.new('DATUM_'+row['id'],None);bpy.context.collection.objects.link(marker);marker.location=ob.location;marker['fixture_contract']=json.dumps(row)
world=bpy.data.worlds.new('No_hidden_fill');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;bpy.context.scene.world=world
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));sourcehash=sha(OUT)
with precise_normals()as precision:bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_lights=False,export_cameras=False,export_animations=False)
assert sha(BASE)==EXPECTED and sha(OUT)==sourcehash;np.savez_compressed(R/'SOURCE_ATTRIBUTES.npz',**expected);report={'source':str(OUT),'source_sha256':sourcehash,'base_material_source_sha256':EXPECTED,'export':str(GLB),'export_sha256':sha(GLB),'geometry_sha256':sha(R/'BRIDGE_GEOMETRY_002.json'),'records':records,'material_graphs':{k:digest(material_record(v))for k,v in mats.items()},'light_count':3,'normal_precision':precision,'compiler_floor_in_source':False,'pending':['Independent reopen/export attributes and mounting proof','Current-world below-floor band Y68.55–69.20 before installation','Compiler floor/support/normal-eye/loaded-route acceptance']};(R/'BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['records','material_graphs']}))
