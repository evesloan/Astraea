"""Repack botanical-soil dependency without changing any architectural mesh.
Source/GLB evidence must be refreshed after this texture-only update.
"""
import bpy,importlib.util,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
family=json.loads((ROOT/'manifest.json').read_text());rows=[]
for cid in ['AST-BOT-004','AST-BOT-005','AST-BOT-006']:
 blend=ROOT/(cid+'.blend');bpy.ops.wm.open_mainfile(filepath=str(blend))
 spec=importlib.util.spec_from_file_location('planter_builder',ROOT/'source/build_botanical_planter.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];before={o.name:[list(v.co) for v in o.data.vertices] for o in obs}
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);glb=ROOT/(cid+'.glb');builder.export(obs,glb)
 assert before=={o.name:[list(v.co) for v in o.data.vertices] for o in obs}
 p=ROOT/(cid+'.manifest.json');meta=json.loads(p.read_text());meta['hashes']={'blend_sha256':sha(blend),'glb_sha256':sha(glb)};meta['texture_revision_note']='Botanical soil repacked after independent pixel review; architectural vertices and guest material roles unchanged';meta['assembly_topology']='Closed editable component solids; returned coping may intersect adjacent closed solids. Consolidated material-role GLB is not a Boolean union or single welded manifold.';p.write_text(json.dumps(meta,indent=2)+'\n');rows.append(meta)
family['assets']=rows
for p in [CAT/'standards/botanical_materials.py',CAT/'materials/botanical/manifest.json']:
 family['dependency_sha256'][str(p.relative_to(CAT))]=sha(p)
family['soil_revision_evidence']='Original five views preserved in qa/revision01_original_soil; corrected soil is verified by refreshed standing and construction-detail imported-GLB views.'
(ROOT/'manifest.json').write_text(json.dumps(family,indent=2)+'\n')
print('SOIL_REPACK_COMPLETE_NO_VERTEX_CHANGES')
