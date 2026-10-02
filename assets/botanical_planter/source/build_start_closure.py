"""Derived handedness of AST-BOT-006; same authored design, not a new asset.
Reflect mesh X in Blender, recalculate closed-surface winding, export identity
transforms. Seat remains on -Y and soil on +Y. Source .blend stays unchanged.
"""
import bpy,bmesh,json,importlib.util,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DERIVED=ROOT/'derived';DERIVED.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'AST-BOT-006.blend'))
spec=importlib.util.spec_from_file_location('planter_builder',ROOT/'source/build_botanical_planter.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
for ob in objects:
 for v in ob.data.vertices:v.co.x=-v.co.x
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 ob['derived_handedness']='Baked mesh reflection X, positive identity transforms; same AST-BOT-006 design'
bpy.context.view_layer.update();p=DERIVED/'AST-BOT-006_START.glb';builder.export(objects,p);lo,hi,dims,tris=builder.measured(objects)
meta={'catalogue_id':'AST-BOT-006','variant':'START','unique_authored_asset':False,'derived_from':'AST-BOT-006.blend','source_blend_sha256':hashlib.sha256((ROOT/'AST-BOT-006.blend').read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'recipe':'Mesh X reflection; source face normals recalculated; modifiers evaluated; UVs normalized; role consolidation; no negative node transforms','pivot_m':[0,0,0],'placement':'At open start seam, same Z rotation as first straight piece; soil and seat lateral sides unchanged','seam_local_m':[0,0,0],'min_m':lo,'max_m':hi,'dimensions_m':dims,'triangles':tris,'material_roles':sorted(set(o['material_role'] for o in objects))}
p.with_suffix('.manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
original=json.loads((ROOT/'collision_proposals.json').read_text())['AST-BOT-006']
for part in original['parts']:
 for solid in part['solids']:
  for point in solid['points_m']:point[0]=-point[0]
(DERIVED/'AST-BOT-006_START.collision_proposal.json').write_text(json.dumps(original,indent=2)+'\n')
print('START_CLOSURE_DERIVED',json.dumps(meta))
# Keep the optional handedness recipe discoverable after a complete rebuild.
family_path=ROOT/'manifest.json';family=json.loads(family_path.read_text())
family['derived_variants']=[{'path':'derived/AST-BOT-006_START.glb','source_asset':'AST-BOT-006','unique_asset':False,'purpose':'Close start seam without swapping seat and soil sides','recipe':'source/build_start_closure.py; baked X mesh reflection and corrected normals; positive transforms'}]
family['assembly_instances_closed_both_ends']=[{'asset_id':'AST-BOT-006','variant':'START','path':'derived/AST-BOT-006_START.glb','translation_m':[0,0,0],'rotation_z_degrees':0}]+family['assembly_instances']
family_path.write_text(json.dumps(family,indent=2)+'\n')
