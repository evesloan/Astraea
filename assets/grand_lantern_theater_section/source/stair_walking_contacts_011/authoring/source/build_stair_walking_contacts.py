"""UNRUN. Build a NEW standalone same-family collision-only .blend, never the original.
Later authorized command: blender --background --factory-startup --python THIS -- --output NEW_DIR
No catalogue registration, GLB export, Game writes, engine launch or production application.
"""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=a.output.resolve()
# Authoring must stay scratch-only. A retained source copy can be adopted separately after QA.
assert out.is_relative_to(Path('/workspace/scratch/375c2e438292')) and not out.exists()
for path,pin in json.loads((R/'SOURCE_PINS.json').read_text()).items():assert sha(path)==pin,path
assert sha(R/'WALK_RAMP_PROPOSAL.json')=='1057f62b7c2b9762c377a245e92c62f479eac22e826c923dfc7de512e3d4ce57'
proposal=json.loads((R/'WALK_RAMP_PROPOSAL.json').read_text());assert len(proposal['rows'])==8 and proposal['issues']==[]
# New file only. Existing source is read for its hash, never opened, altered or saved.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.name='AST-CUL-005_StairWalkingContactDerivative011'
scene['catalogue_family']='AST-CUL-005';scene['source_original_sha256']='dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530';scene['walking_contact_approximation']=True;scene['load_certification']=False;scene['rendered']=False
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
for row in proposal['rows']:
    mesh=bpy.data.meshes.new(row['id']+'_EditableMesh')
    # Orientation-preserving Godot->Blender transform (x,y,z)->(x,-z,y).
    origin=row['vertices_world'][0]
    mesh.from_pydata([(x-origin[0],-(z-origin[2]),y-origin[1])for x,y,z in row['vertices_world']],[],row['faces']);mesh.update()
    ob=bpy.data.objects.new(row['id'],mesh);scene.collection.objects.link(ob);ob.location=(origin[0],-origin[2],origin[1])
    ob.hide_render=True;ob.display_type='WIRE'
    for k,v in {'catalogue_family':'AST-CUL-005','source_flight_id':row['source_flight']['id'],'walking_contact_approximation':True,'collision_only':True,'collision_margin_m':.001,'vertical_thickness_m':.04,'original_meshes_and_contacts_retained':True,'compiler_floor_credit':False,'load_certification':False}.items():ob[k]=v
    ob['source_lower_receiver_ids']=json.dumps(row['lower_landing_receivers']);ob['source_upper_receiver_ids']=json.dumps(row['upper_landing_receivers'])
    ob['proposal_sha256']=sha(R/'WALK_RAMP_PROPOSAL.json')
assert len(scene.objects)==8 and len(bpy.data.objects)==8 and all(o.type=='MESH' and len(o.data.vertices)==8 and len(o.data.polygons)==12 for o in scene.objects)
out.mkdir();target=out/'AST-CUL-005_stair_walking_contacts_011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),check_existing=True)
for path,pin in json.loads((R/'SOURCE_PINS.json').read_text()).items():assert sha(path)==pin,path
(out/'BUILD_RECEIPT.json').write_text(json.dumps({'status':'BUILT_REOPEN_PENDING','blend_sha256':sha(target),'builder_sha256':sha(__file__),'proposal_sha256':sha(R/'WALK_RAMP_PROPOSAL.json'),'objects':8,'original_sources_unchanged':True},indent=2)+'\n')
