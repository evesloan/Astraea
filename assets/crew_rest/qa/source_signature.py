import bpy,json,hashlib,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def rounded(v):return [round(float(x),8)for x in v]
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def signature(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'location':rounded(o.location),'rotation':rounded(o.rotation_euler),'scale':rounded(o.scale),'properties':{k:o[k]if isinstance(o[k],(str,int,float,bool))else list(o[k])for k in o.keys() if k!='_RNA_UI'}}
  if o.animation_data:r['drivers']=[{'path':d.data_path,'index':d.array_index,'expression':d.driver.expression,'variables':[(v.name,v.type,[(t.id.name if t.id else None,t.data_path)for t in v.targets])for v in d.driver.variables]}for d in o.animation_data.drivers]
  if o.type=='MESH':
   me=o.data;r['vertices']=[rounded(v.co)for v in me.vertices];r['faces']=[list(p.vertices)for p in me.polygons];r['uv']={l.name:[rounded(d.uv)for d in l.data]for l in me.uv_layers};r['materials']=[m.name for m in me.materials];r['modifiers']=[{'name':m.name,'type':m.type,**{k:getattr(m,k)for k in('width','segments','limit_method','thickness','offset','keep_sharp')if hasattr(m,k)}}for m in o.modifiers]
   if me.shape_keys:
    r['shape_keys']={k.name:[rounded(d.co)for d in k.data]for k in me.shape_keys.key_blocks};r['shape_key_drivers']=[{'path':d.data_path,'expression':d.driver.expression}for d in me.shape_keys.animation_data.drivers]
  rows.append(r)
 mats=[]
 for m in sorted(bpy.data.materials,key=lambda m:m.name):
  if not m.get('astraea_material_role'):continue
  nodes=[]
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE':nodes.append({'type':n.type,'image_name':n.image.name,'packed_bytes_sha256':hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest(),'extension':n.extension})
   elif n.type=='BSDF_PRINCIPLED':nodes.append({'type':n.type,'roughness':n.inputs['Roughness'].default_value,'metallic':n.inputs['Metallic'].default_value})
  mats.append({'role':m['astraea_material_role'],'revision':m['material_revision'],'nodes':nodes})
 data={'objects':rows,'materials':mats,'units':bpy.context.scene.unit_settings.scale_length};return {'path':str(path),'scene_signature_sha256':digest(data),'object_count':len(rows),'material_count':len(mats)}
rows=[]
for ident in('AST-CRW-001','AST-CRW-002'):
 a=signature(BASE/'source'/(ident+'.blend'));b=signature(BASE/'qa/source_only_stage/catalogue/assets/crew_rest/source'/(ident+'.blend'));rows.append({'asset':ident,'original':a,'rebuilt':b,'matched':a['scene_signature_sha256']==b['scene_signature_sha256']})
result={'signature_scope':'Actual source scene semantic hierarchy, geometry, UVs, modifiers, shape keys, drivers, source properties, material PBR settings and packed image bytes; external file paths intentionally excluded','results':rows,'all_passed':all(r['matched']for r in rows)};(BASE/'qa/source_signature_comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
