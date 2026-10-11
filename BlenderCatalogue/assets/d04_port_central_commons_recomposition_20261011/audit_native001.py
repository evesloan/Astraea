from pathlib import Path
import bpy,json,hashlib,math,re
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def payload(o):
 return {'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(p.vertices)for p in o.data.polygons],'uv_layers':[[list(v.uv)for v in l.data]for l in o.data.uv_layers],'materials':[{'name':re.sub(r'\.\d+$','',m.name),'roughness':m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value,'textures':[hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest()if n.image.packed_file else str(n.image.filepath)for n in m.node_tree.nodes if n.type=='TEX_IMAGE']}for m in o.data.materials]}
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));return {o.name.replace('.','_'):{'payload':payload(o),'world':[list(o.matrix_world@v.co)for v in o.data.vertices]}for o in bpy.data.objects if o.type=='MESH'}
s=read(R/P['source_co_native']);actual=read(W/P['patch']['native']);rows=[]
for q in P['moves']:
 if q['name']in P['front_clip_boxes']:continue
 old=s[q['name']];new=actual[q['name']];assert old['payload']==new['payload'],q['name']+' local payload';d=q['delta'];delta=Vector((d[0],-d[2],d[1]));err=max((Vector(b)-Vector(a)-delta).length for a,b in zip(old['world'],new['world']));bound=max(abs(t)for v in old['world']for t in v)/2**23*4+1e-6;assert err<=bound,(q['name'],err,bound);rows.append({'name':q['name'],'exact_local_geometry_faces_UVs_materials':True,'world_translation_max_error_m':err,'float32_roundoff_bound_m':bound})
s=read(R/P['gate_source']['native']);actual=read(W/P['structure']['native']);copies=[];pivot=P['gate_source']['source_pivot'];pivot=Vector((pivot[0],-pivot[2],pivot[1]))
for i,g in enumerate(P['gates']):
 t=g['pivot'];T=Matrix.Translation(Vector((t[0],-t[2],t[1])))@Matrix.Rotation(math.radians(g['source_rotation_y_degrees']),4,'Z')@Matrix.Translation(-pivot)
 for name in P['gate_source']['members']+P['gate_source']['control_members']:
  key='PCR_G'+str(i)+'_'+name;old=s[name];new=actual[key];assert old['payload']==new['payload'],key+' exact source payload';err=max((Vector(b)-T@Vector(a)).length for a,b in zip(old['world'],new['world']));assert err<=.0001220703125,(key,err);copies.append({'name':key,'source':name,'exact_local_geometry_faces_UVs_materials':True,'world_rigid_error_m':err})
for f,h in P['source_protected_native_exports'].items():assert sha(R/f)==h,f
result={'status':'PASS','rigid_moved_source_meshes':rows,'rigid_source_fitting_copies':copies,'bounded_clip_meshes':len(P['cuts'])+len(P['front_clip_boxes']),'original_native_exports_unchanged':len(P['source_protected_native_exports']),'editable_natives_and_fresh_repeat_exports':P['native_export_records']};(W/'EXACT_NATIVE_SOURCE_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('EXACT SOURCE AUDIT PASS',len(rows),len(copies))
