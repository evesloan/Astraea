"""Re-export unchanged frozen sources as material-role runtime groups, without saving .blend."""
import bpy,json,runpy,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
scope=runpy.run_path(str(BASE/'source/build_botanical_cluster.py'));records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted(BASE.glob('AST-BOT-*.manifest.json')):
 r=json.loads(p.read_text());source=BASE/r['source'];before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.view_layer.update()
 scope['export'].__globals__.update(PARTS=[bpy.data.objects[n]for n in r['semantic_parts']],ROOT=bpy.data.objects[r['catalogue_id']],MARKERS=r['physical_and_proposal_markers']);scope['export'](r['catalogue_id']);assert sha(source)==before
 r['glb_sha256']=sha(BASE/r['export']);r['generator_sha256']=sha(BASE/'source/build_botanical_cluster.py');r['runtime_semantics']='One evaluated runtime mesh per material role plus purposeful root/contact/origin empties; full named semantic parts retained in editable source; no engine performance acceptance';r['runtime_mesh_count']=len(r['material_roles']);r['source_unchanged_during_consolidation']=True;p.write_text(json.dumps(r,indent=2)+'\n');records.append(r)
(BASE/'manifest.json').write_text(json.dumps({'family':'Joined botanical cluster silhouettes','unique_design_count':3,'assets':records},indent=2)+'\n')
print([(r['catalogue_id'],r['runtime_mesh_count'],r['glb_sha256'])for r in records])
