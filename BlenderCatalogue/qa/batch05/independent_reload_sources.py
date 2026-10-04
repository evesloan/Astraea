"""Blender read-only source reload, semantic editability, used packed image audit."""
import bpy,sys,json,hashlib,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05'
folders=['aquatic_lounge','aquatic_edges','aquatic_float']
files=[p for f in folders for p in (ROOT/'assets'/f).rglob('*.blend') if not any(x in p.parts for x in ['history','backup','source_backups'])]
before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for f in folders:
 sys.argv=['inspect_blend_independent.py','--',str(ROOT/'assets'/f),str(OUT/('independent_'+f+'_blend_report.json'))]
 runpy.run_path(str(ROOT/'qa/inspect_blend_independent.py'),run_name='__main__')
material_files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'materials').rglob('*.png')}
rows=[]
for p in files:
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);used={}
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','CURVE']:continue
  for m in o.data.materials:
   if m:used.setdefault(m.name,[]).append(o.name)
 row={'path':str(p.relative_to(ROOT)),'sha256':before[str(p.relative_to(ROOT))],'materials':[],'issues':[],'scope':'Only materials assigned to source mesh/curve geometry are surface dependencies. Unused historical datablocks are reported separately.'}
 for m in bpy.data.materials:
  images=[]
  for n in m.node_tree.nodes if m.use_nodes else []:
   if n.type!='TEX_IMAGE' or not n.image:continue
   im=n.image;h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None;fn=Path(im.filepath).name
   images.append({'image':im.name,'file':fn,'packed':bool(im.packed_file),'packed_sha256':h,'current_file_sha256':material_files.get(fn),'matches_current':h==material_files.get(fn)})
  rec={'name':m.name,'used_by_parts':used.get(m.name,[]),'images':images};row['materials'].append(rec)
  if rec['used_by_parts'] and any(not x['packed'] or not x['matches_current'] for x in images):row['issues'].append(m.name+': assigned surface image unpacked or differs from current material role')
 rows.append(row)
after={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(OUT/'independent_source_material_usage.json').write_text(json.dumps(rows,indent=2)+'\n')
(OUT/'independent_source_reload_stability.json').write_text(json.dumps({'before':before,'after':after,'unchanged':before==after},indent=2)+'\n')
print(json.dumps([{'source':r['path'],'issues':r['issues']} for r in rows],indent=2))
