"""Inspect source surface material/image usage; distinguish unused historical datablocks."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch04';rows=[]
current_images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'materials').rglob('*.png')}
for folder in ['botanical_canopy','botanical_understory','botanical_planter']:
 for p in sorted((ROOT/'assets'/folder).rglob('*.blend')):
  if not p.stem.startswith('AST-BOT'):continue
  bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);used={}
  for o in bpy.context.scene.objects:
   if o.type not in ['MESH','CURVE']:continue
   for m in o.data.materials:
    if m:used.setdefault(m.name,[]).append(o.name)
  materials=[];issues=[]
  for m in bpy.data.materials:
   imgs=[]
   for n in m.node_tree.nodes if m.use_nodes else []:
    if n.type=='TEX_IMAGE' and n.image:
     im=n.image;file=Path(im.filepath).name;h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None
     imgs.append({'image':im.name,'file':file,'packed':bool(im.packed_file),'packed_sha256':h,'current_file_sha256':current_images.get(file),'matches_current_file':h==current_images.get(file)})
   rec={'material':m.name,'used_by_parts':used.get(m.name,[]),'used_surface':m.name in used,'images':imgs}
   materials.append(rec)
   if rec['used_surface'] and any(not i['packed'] or not i['matches_current_file'] for i in imgs):issues.append(m.name+': used image differs from current library or is unpacked')
  image_usage=[]
  for im in bpy.data.images:
   if im.source!='FILE':continue
   linked=[m['material'] for m in materials if any(x['image']==im.name for x in m['images']) and m['used_surface']]
   file=Path(im.filepath).name;h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest() if im.packed_file else None
   image_usage.append({'name':im.name,'file':file,'used_by_surface_materials':linked,'packed_sha256':h,'matches_current_file':h==current_images.get(file),'visible_surface_dependency':bool(linked)})
  rows.append({'image_usage':image_usage,'source':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'materials':materials,'issues':issues,'unused_historical_soil_is_visible_mismatch':False,'scope':'Only materials assigned to actual mesh/curve parts are surface dependencies; loaded unused historical helper roles do not change rendered or exported surfaces.'})
(OUT/'independent_source_material_usage.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{'source':r['source'],'issues':r['issues'],'unused_soil':[m for m in r['materials'] if 'soil' in m['material'] and not m['used_surface']]} for r in rows],indent=2))
