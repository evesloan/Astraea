"""Reload all real Blender sources, verifying editability, packed textures and markers."""
import bpy,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];out=[]
for p in sorted((BASE/'source').glob('AST-SAL-*.blend')):
 mf=json.loads((BASE/(p.stem+'.manifest.json')).read_text());bpy.ops.wm.open_mainfile(filepath=str(p));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];empties=[o for o in bpy.context.scene.objects if o.type=='EMPTY'];issues=[]
 if len(obs)!=mf['editable_semantic_parts']:issues.append('Semantic object inventory differs')
 if sorted(o.name for o in obs)!=sorted(mf['semantic_parts']):issues.append('Named source semantic objects differ')
 if not all(o.get('material_role') in mf['material_roles'] for o in obs):issues.append('Unlabelled material role')
 if not all(abs(o.scale.x-1)<1e-8 and abs(o.scale.y-1)<1e-8 and abs(o.scale.z-1)<1e-8 for o in obs):issues.append('Unapplied source scale')
 images=[i for i in bpy.data.images if i.source=='FILE']
 if not all(i.packed_file for i in images):issues.append('Unpacked texture')
 for r in mf['positions_and_normals']:
  o=bpy.data.objects.get(r['node_name'])
  if not o or max(abs(o.location[k]-r['source_blender_xyz_m'][k]) for k in range(3))>1e-6:issues.append('Marker location mismatch '+r['name'])
  if r['kind'].startswith('physical') and r['physical_part'] not in [x.name for x in obs]:issues.append('Missing physical part '+r['name'])
 rec={'catalogue_id':p.stem,'status':'PASS' if not issues else'FAIL','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'editable_semantic_objects':len(obs),'retained_modifiers':sum(len(o.modifiers) for o in obs),'actual_marker_nodes':len(empties),'packed_texture_count':len(images),'unit_scale':bpy.context.scene.unit_settings.scale_length,'issues':issues};out.append(rec)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));assert all(r['status']=='PASS' for r in out)
